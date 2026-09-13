from database.postgres import SessionLocal
from database.repository import Repository


class HistoryTools:

    def __init__(self):
        self.db = SessionLocal()
        self.repository = Repository(self.db)

    def get_last_inspection(self, vehicle_id):
        """
        Retourne la dernière inspection d'un véhicule.
        """
        return self.repository.get_last_inspection(vehicle_id)

    def close(self):
        self.db.close()