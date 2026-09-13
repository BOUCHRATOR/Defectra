from database.models import (
    Vehicle,
    Inspection,
    Defect,
    Report,
    Conversation,
    Message
)


class Repository:

    def __init__(self, db):
        self.db = db

    # ==========================================
    # VEHICLE
    # ==========================================

    def get_vehicle(self, plate):
        """
        Recherche un véhicule par sa plaque.
        """

        return (
            self.db.query(Vehicle)
            .filter(Vehicle.plate_number == plate)
            .first()
        )
    def get_vehicle_by_id(self, vehicle_id):

        return (
            self.db.query(Vehicle)
            .filter(Vehicle.id == vehicle_id)
            .first()
        )

    def create_vehicle(self, vehicle):
        """
        Enregistre un nouveau véhicule.
        """

        self.db.add(vehicle)
        self.db.commit()
        self.db.refresh(vehicle)

        return vehicle

    def update_vehicle(self, vehicle):
        """
        Sauvegarde les modifications.
        """

        self.db.add(vehicle)

        self.db.commit()

        self.db.refresh(vehicle)

        return vehicle
    def delete_vehicle(self, vehicle_id):

        vehicle = self.get_vehicle_by_id(vehicle_id)

        if vehicle:

            self.db.delete(vehicle)

            self.db.commit()

        return vehicle

    # ===============================
    # INSPECTIONS
    # ===============================
    def get_inspection(self, inspection_id):

        return (
            self.db.query(Inspection)
            .filter(Inspection.id == inspection_id)
            .first()
        )
    def update_inspection(self, inspection):

        self.db.add(inspection)

        self.db.commit()

        self.db.refresh(inspection)

        return inspection
    def delete_inspection(self, inspection_id):

        inspection = self.get_inspection(inspection_id)

        if inspection:

            self.db.delete(inspection)

            self.db.commit()

        return inspection

    def create_inspection(self, inspection):

        self.db.add(inspection)

        self.db.commit()

        self.db.refresh(inspection)

        return inspection


    def get_last_inspection(self, vehicle_id):

        return (
            self.db.query(Inspection)
            .filter(Inspection.vehicle_id == vehicle_id)
            .order_by(Inspection.id.desc())
            .first()
        )
    def get_defects_by_inspection(self, inspection_id):

        return (
            self.db.query(Defect)
            .filter(
                Defect.inspection_id == inspection_id
            )
            .all()
        )
    def get_inspection_context(self, inspection_id):

        inspection = (
            self.db.query(Inspection)
            .filter(Inspection.id == inspection_id)
            .first()
        )

        if not inspection:
            return None

        vehicle = self.get_vehicle_by_id(
            inspection.vehicle_id
        )

        defects = self.get_defects_by_inspection(
            inspection_id
        )

        report = self.get_report(
            inspection_id
        )

        return {
            "vehicle": vehicle,
            "inspection": inspection,
            "defects": defects,
            "report": report
        }
   # ==========================================
# DEFECT
# ==========================================

    def create_defect(self, defect):

        self.db.add(defect)
        self.db.commit()
        self.db.refresh(defect)

        return defect


    def get_defects_by_inspection(self, inspection_id):

        return (
            self.db.query(Defect)
            .filter(Defect.inspection_id == inspection_id)
            .all()
        )
    def get_defect(self, defect_id):

        return (
            self.db.query(Defect)
            .filter(Defect.id == defect_id)
            .first()
        )
    def update_defect(self, defect):

        self.db.add(defect)

        self.db.commit()

        self.db.refresh(defect)

        return defect
    def delete_defect(self, defect_id):

        defect = self.get_defect(defect_id)

        if defect:

            self.db.delete(defect)

            self.db.commit()

        return defect
   # ==========================================
    # REPORT
    # ==========================================

    def create_report(self, report):

        self.db.add(report)
        self.db.commit()
        self.db.refresh(report)

        return report


    def get_report(self, inspection_id):

        return (
            self.db.query(Report)
            .filter(Report.inspection_id == inspection_id)
            .first()
        )
    def update_report(self, report):

        self.db.add(report)

        self.db.commit()

        self.db.refresh(report)

        return report
    def delete_report(self, inspection_id):

        report = self.get_report(inspection_id)

        if report:

            self.db.delete(report)

            self.db.commit()

        return report
    # ==========================================
    # CONVERSATION
    # ==========================================

    def create_conversation(self, conversation):

        self.db.add(conversation)

        self.db.commit()

        self.db.refresh(conversation)

        return conversation


    def get_conversation(self, conversation_id):

        return (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )


    def get_user_conversations(self, owner_id):

        return (
            self.db.query(Conversation)
            .filter(Conversation.owner_id == owner_id)
            .all()
        )
        # ==========================================
        # UPDATE CONVERSATION
        # ==========================================

    def update_conversation(self, conversation):

        self.db.add(conversation)
        self.db.commit()

        self.db.refresh(conversation)

        return conversation
    def delete_conversation(self, conversation_id):

        conversation = (
            self.db.query(Conversation)
            .filter(Conversation.id == conversation_id)
            .first()
        )

        if conversation:

            self.db.delete(conversation)

            self.db.commit()
    def get_last_conversation(self, owner_id):

        return (
            self.db.query(Conversation)
            .filter(Conversation.owner_id == owner_id)
            .order_by(Conversation.id.desc())
            .first()
        )
    # ==========================================
    # MESSAGE
    # ==========================================

    def create_message(self, message):

        self.db.add(message)

        self.db.commit()

        self.db.refresh(message)

        return message
    def get_message(self, message_id):

        return (
            self.db.query(Message)
            .filter(Message.id == message_id)
            .first()
        )

    def get_messages(self, conversation_id):

        return (
            self.db.query(Message)
            .filter(Message.conversation_id == conversation_id)
            .order_by(Message.id.asc())
            .all()
        )

    def delete_message(self, message_id):

        message = self.get_message(message_id)

        if message:

            self.db.delete(message)

            self.db.commit()

        return message