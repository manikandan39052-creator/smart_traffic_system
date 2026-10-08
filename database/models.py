from dataclasses import dataclass
@dataclass
class ViolationRecord:
    id:str; violation_type:str; camera_id:str; timestamp:str; status:str='PENDING_REVIEW'
