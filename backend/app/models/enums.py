import enum


class Role(str, enum.Enum):
    admin = "admin"
    donor = "donor"
    requester = "requester"


class BloodGroup(str, enum.Enum):
    A_POS = "A+"
    A_NEG = "A-"
    B_POS = "B+"
    B_NEG = "B-"
    AB_POS = "AB+"
    AB_NEG = "AB-"
    O_POS = "O+"
    O_NEG = "O-"


class AvailabilityStatus(str, enum.Enum):
    available = "available"
    unavailable = "unavailable"
    unknown = "unknown"


class Urgency(str, enum.Enum):
    routine = "routine"
    urgent = "urgent"
    emergency = "emergency"


class RequestStatus(str, enum.Enum):
    pending = "pending"
    in_progress = "in_progress"
    fulfilled = "fulfilled"
    cancelled = "cancelled"


class CoordinationStatus(str, enum.Enum):
    contact_pending = "contact_pending"
    contacted = "contacted"
    declined = "declined"
    completed = "completed"
