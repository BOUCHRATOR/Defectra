from database.postgres import SessionLocal
from database.repository import Repository


class Tools:

    def __init__(self):

        self.db = SessionLocal()

        self.repository = Repository(self.db)

    # ==========================================
    # VEHICLE
    # ==========================================

    def get_vehicle(self, plate):

        return self.repository.get_vehicle(plate)

    # ==========================================
    # INSPECTION
    # ==========================================

    def get_last_inspection(self, vehicle_id):

        return self.repository.get_last_inspection(vehicle_id)

    # ==========================================
    # REPORT
    # ==========================================

    def get_report(self, inspection_id):

        return self.repository.get_report(inspection_id)

    # ==========================================
    # DEFECT
    # ==========================================

    def get_defects(self, inspection_id):

        return self.repository.get_defects_by_inspection(
            inspection_id
        )

    # ==========================================
    # CLOSE
    # ==========================================

    def close(self):

        self.db.close()