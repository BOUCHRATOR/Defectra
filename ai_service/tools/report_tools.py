from database.postgres import SessionLocal
from database.repository import Repository


class ReportTools:

    def __init__(self):
        self.db = SessionLocal()
        self.repository = Repository(self.db)

    def get_report(self, inspection_id):
        """
        Retourne le rapport associé à une inspection.
        """
        return self.repository.get_report(inspection_id)

    def close(self):
        self.db.close()