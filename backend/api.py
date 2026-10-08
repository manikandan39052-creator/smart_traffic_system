"""REST/WebSocket review API; run with uvicorn backend.api:app --reload."""
from pathlib import Path
from fastapi import FastAPI, HTTPException, WebSocket
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from database.database import Database
from backend.schemas import CameraIn,ReviewIn
from backend.websocket_manager import manager
app=FastAPI(title='Smart Traffic Enforcement API'); db=Database()
app.mount('/dashboard', StaticFiles(directory=Path(__file__).resolve().parents[1]/'dashboard', html=True), name='dashboard')
@app.get('/api/violations')
def violations(): return db.list_violations()
@app.get('/api/violations/{violation_id}')
def violation(violation_id:str):
    item=db.get_violation(violation_id)
    if not item: raise HTTPException(404,'Violation not found')
    return item
@app.post('/api/violations/{violation_id}/confirm')
async def confirm(violation_id:str,review:ReviewIn): db.review(violation_id,'CONFIRMED',review.note); await manager.broadcast({'type':'violation_reviewed','violation_id':violation_id,'status':'CONFIRMED'}); return {'ok':True}
@app.post('/api/violations/{violation_id}/reject')
async def reject(violation_id:str,review:ReviewIn): db.review(violation_id,'REJECTED',review.note); await manager.broadcast({'type':'violation_reviewed','violation_id':violation_id,'status':'REJECTED'}); return {'ok':True}
@app.get('/api/statistics')
def statistics(): return db.statistics()
@app.get('/api/cameras')
def cameras():
    with db.connect() as c:return [dict(r) for r in c.execute('SELECT * FROM cameras')]
@app.post('/api/cameras')
def add_camera(camera:CameraIn):
    with db.connect() as c:c.execute('INSERT OR REPLACE INTO cameras VALUES (?,?,?,?)',(camera.id,camera.name,camera.source,'DISCONNECTED'))
    return camera
@app.put('/api/cameras/{camera_id}')
def update_camera(camera_id:str,camera:CameraIn):
    with db.connect() as c:c.execute('UPDATE cameras SET name=?,source=? WHERE id=?',(camera.name,camera.source,camera_id))
    return camera
@app.delete('/api/cameras/{camera_id}')
def delete_camera(camera_id:str):
    with db.connect() as c:c.execute('DELETE FROM cameras WHERE id=?',(camera_id,))
    return {'ok':True}
@app.get('/api/evidence/{violation_id}')
def evidence(violation_id:str):
    item=db.get_violation(violation_id)
    if not item or not item['evidence_path']: raise HTTPException(404,'Evidence not found')
    path=Path(item['evidence_path'])/'overview.jpg'
    if not path.exists(): raise HTTPException(404,'Overview image not found')
    return FileResponse(path)
@app.websocket('/ws/events')
async def events(ws:WebSocket):
    await manager.connect(ws)
    try:
        while True: await ws.receive_text()
    except Exception: manager.disconnect(ws)
