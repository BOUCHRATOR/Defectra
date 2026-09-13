from database.postgres import SessionLocal
from database.repository import Repository


class DefectTools:

    def __init__(self):
        self.db = SessionLocal()
        self.repository = Repository(self.db)

    def get_defects(self, inspection_id):
        """
        Retourne tous les défauts d'une inspection.
        """
        return self.repository.get_defects_by_inspection(
            inspection_id
        )

    def close(self):
        self.db.close()