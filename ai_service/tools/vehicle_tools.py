from database.postgres import SessionLocal
from database.repository import Repository


class VehicleTools:

    def __init__(self):
        self.db = SessionLocal()
        self.repository = Repository(self.db)

    def get_vehicle_by_plate(self, plate):
        """
        Retourne un véhicule à partir de sa plaque.
        """
        return self.repository.get_vehicle(plate)

    def vehicle_exists(self, plate):
        """
        Vérifie si un véhicule existe.
        """
        vehicle = self.repository.get_vehicle(plate)
        return vehicle is not None

    def close(self):
        self.db.close()