from database.database import Database
class ViolationRepository:
    def __init__(self,db:Database): self.db=db
    def list(self): return self.db.list_violations()
