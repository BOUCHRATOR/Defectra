from sqlalchemy import (
    Column,
    Integer,
    String,
    Float,
    Text,
    Date,
    DateTime,
    ForeignKey
)

from sqlalchemy.orm import declarative_base, relationship
from datetime import datetime

Base = declarative_base()


# ==========================================================
# VEHICLE
# ==========================================================

class Vehicle(Base):
    __tablename__ = "vehicles_vehicle"

    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer)

    plate_number = Column(String)

    brand = Column(String)

    model = Column(String)

    year = Column(Integer)

    color = Column(String)

    fuel_type = Column(String)

    mileage = Column(Integer)

    vin = Column(String)

    vehicle_image = Column(String)

    created_at = Column(DateTime)

    updated_at = Column(DateTime)

    inspections = relationship(
        "Inspection",
        back_populates="vehicle"
    )


# ==========================================================
# INSPECTION
# ==========================================================

class Inspection(Base):
    __tablename__ = "inspections_inspection"

    id = Column(Integer, primary_key=True)

    vehicle_id = Column(
        Integer,
        ForeignKey("vehicles_vehicle.id")
    )

    inspection_date = Column(Date)

    notes = Column(Text)

    status = Column(String)

    created_at = Column(DateTime)

    vehicle = relationship(
        "Vehicle",
        back_populates="inspections"
    )

    defects = relationship(
        "Defect",
        back_populates="inspection"
    )

    report = relationship(
        "Report",
        back_populates="inspection",
        uselist=False
    )

    conversations = relationship(
        "Conversation",
        back_populates="inspection"
    )


# ==========================================================
# DEFECT
# ==========================================================

class Defect(Base):

    __tablename__ = "defects_defect"

    id = Column(Integer, primary_key=True)

    inspection_id = Column(
        Integer,
        ForeignKey("inspections_inspection.id")
    )

    defect_name = Column(String)

    confidence = Column(Float)

    severity = Column(String)

    description = Column(Text)

    solution = Column(Text)

    defect_image = Column(String)

    # Nouvelles informations
    location = Column(String)

    x1 = Column(Float)
    y1 = Column(Float)
    x2 = Column(Float)
    y2 = Column(Float)

    created_at = Column(
    DateTime,
    default=datetime.utcnow,
    nullable=False
    )

    inspection = relationship(
        "Inspection",
        back_populates="defects"
    )

# ==========================================================
# REPORT
# ==========================================================

class Report(Base):
    __tablename__ = "reports_report"

    id = Column(Integer, primary_key=True)

    inspection_id = Column(
        Integer,
        ForeignKey("inspections_inspection.id")
    )

    summary = Column(Text)

    overall_condition = Column(String)

    recommendation = Column(Text)

    pdf_file = Column(String)

    generated_at = Column(DateTime)

    inspection = relationship(
        "Inspection",
        back_populates="report"
    )


# ==========================================================
# CONVERSATION
# ==========================================================

class Conversation(Base):
    __tablename__ = "chat_conversations"

    id = Column(Integer, primary_key=True)

    owner_id = Column(Integer, nullable=False)

    inspection_id = Column(
        Integer,
        ForeignKey("inspections_inspection.id"),
        nullable=True
    )

    title = Column(String)

    created_at = Column(DateTime)

    updated_at = Column(DateTime)

    inspection = relationship(
        "Inspection",
        back_populates="conversations"
    )

    messages = relationship(
        "Message",
        back_populates="conversation",
        cascade="all, delete-orphan"
    )


# ==========================================================
# MESSAGE
# ==========================================================

class Message(Base):
    __tablename__ = "chat_messages"

    id = Column(Integer, primary_key=True)

    conversation_id = Column(
        Integer,
        ForeignKey("chat_conversations.id")
    )

    role = Column(String)

    content = Column(Text)

    created_at = Column(DateTime)

    conversation = relationship(
        "Conversation",
        back_populates="messages"
    )