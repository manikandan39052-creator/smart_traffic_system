from database.database import Database
def test_database(tmp_path):
 db=Database(tmp_path/'test.db'); db.add_violation({'id':'V1','vehicle_track_id':1,'plate_number':None,'violation_type':'NO_PARKING','camera_id':'CAM_01','timestamp':'2026-01-01','duration':1,'vehicle_type':'car','vehicle_confidence':.9,'plate_confidence':0,'evidence_path':'','status':'PENDING_REVIEW','reviewed_by':None,'reviewed_at':None,'note':None}); assert db.get_violation('V1')['id']=='V1'
