from datetime import datetime

from sqlalchemy import Boolean, Column, ForeignKey, Integer, String, DateTime, Text
from sqlalchemy import Enum as SAEnum
from sqlalchemy.orm import relationship

from app.db.session import Base
from app.models.enums import (
    BloodGroup,
    Role,
    AvailabilityStatus,
    Urgency,
    RequestStatus,
    CoordinationStatus,
)


class User(Base):
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, nullable=False)
    email = Column(String, unique=True, index=True, nullable=False)
    password_hash = Column(String, nullable=False)
    role = Column(SAEnum(Role), nullable=False, default=Role.requester)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    donor = relationship("Donor", back_populates="user", uselist=False)
    requests = relationship("BloodRequest", back_populates="requester")
    status_changes = relationship("RequestStatusHistory", back_populates="changed_by_user")


class Donor(Base):
    __tablename__ = "donors"

    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), unique=True, nullable=False)
    blood_group = Column(SAEnum(BloodGroup), nullable=False, index=True)
    phone_number = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    availability_status = Column(
        SAEnum(AvailabilityStatus), default=AvailabilityStatus.unknown
    )
    consent_to_contact = Column(Boolean, default=False)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    user = relationship("User", back_populates="donor")
    coordinations = relationship("DonationCoordination", back_populates="donor")


class BloodRequest(Base):
    __tablename__ = "blood_requests"

    id = Column(Integer, primary_key=True, index=True)
    requester_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    blood_group = Column(SAEnum(BloodGroup), nullable=False, index=True)
    units_required = Column(Integer, nullable=False)
    hospital_name = Column(String, nullable=False)
    city = Column(String, nullable=False, index=True)
    urgency = Column(SAEnum(Urgency), nullable=False, default=Urgency.routine)
    required_by = Column(DateTime, nullable=True)
    status = Column(SAEnum(RequestStatus), nullable=False, default=RequestStatus.pending)
    created_at = Column(DateTime, default=datetime.utcnow)

    requester = relationship("User", back_populates="requests")
    coordinations = relationship("DonationCoordination", back_populates="request")
    status_history = relationship("RequestStatusHistory", back_populates="request")


class DonationCoordination(Base):
    __tablename__ = "donation_coordination"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("blood_requests.id"), nullable=False)
    donor_id = Column(Integer, ForeignKey("donors.id"), nullable=False)
    coordination_status = Column(
        SAEnum(CoordinationStatus), default=CoordinationStatus.contact_pending
    )
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("BloodRequest", back_populates="coordinations")
    donor = relationship("Donor", back_populates="coordinations")


class RequestStatusHistory(Base):
    __tablename__ = "request_status_history"

    id = Column(Integer, primary_key=True, index=True)
    request_id = Column(Integer, ForeignKey("blood_requests.id"), nullable=False)
    changed_by = Column(Integer, ForeignKey("users.id"), nullable=False)
    previous_status = Column(String, nullable=True)
    new_status = Column(String, nullable=False)
    note = Column(Text, nullable=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    request = relationship("BloodRequest", back_populates="status_history")
    changed_by_user = relationship("User", back_populates="status_changes")
