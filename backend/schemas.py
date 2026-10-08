from pydantic import BaseModel
class CameraIn(BaseModel): id:str; name:str; source:str
class ReviewIn(BaseModel): note:str|None=None
