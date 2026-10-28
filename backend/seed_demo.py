import random
from app.core.security import hash_password
from app.db.session import Sessionlocal
from app.models.user import User, Donor, BloodRequest
from app.models.enums import Role, BloodGroup, AvailabilityStatus, Urgency, RequestStatus

BLOOD_GROUPS = list(BloodGroup)
CITIES = ["Delhi", "Mumbai", "Bangalore", "Chennai", "Kolkata", "Hyderabad", "Pune", "Ahmedabad"]
HOSPITALS = ["AIIMS", "Fortis Hospital", "Apollo Hospital", "Max Hospital"]
URGENCIES = [Urgency.routine, Urgency.urgent, Urgency.emergency]
AVAILABILITY = [AvailabilityStatus.available, AvailabilityStatus.unavailable, AvailabilityStatus.unknown]

db = Sessionlocal()
try:
    for i in range(1, 21):
        email = "donor" + str(i) + "@demo.test"
        if db.query(User).filter(User.email == email).first():
            print("skip donor " + email + " (exists)")
            continue
        user = User(full_name="Demo Donor " + str(i), email=email, password_hash=hash_password("demo1234"), role=Role.donor)
        db.add(user)
        db.flush()
        db.add(Donor(user_id=user.id, blood_group=random.choice(BLOOD_GROUPS), phone_number="98765" + str(i).zfill(5), city=random.choice(CITIES), availability_status=random.choice(AVAILABILITY), consent_to_contact=random.choice([True, True, False])))
    db.commit()

    for i in range(1, 21):
        email = "requester" + str(i) + "@demo.test"
        user = db.query(User).filter(User.email == email).first()
        if not user:
            user = User(full_name="Demo Requester " + str(i), email=email, password_hash=hash_password("demo1234"), role=Role.requester)
            db.add(user)
            db.flush()
        db.add(BloodRequest(requester_id=user.id, blood_group=random.choice(BLOOD_GROUPS), units_required=random.choice([1,2,3,4]), hospital_name=random.choice(HOSPITALS), city=random.choice(CITIES), urgency=random.choice(URGENCIES), status=RequestStatus.pending))
    db.commit()
    print("Seeded 20 donors and 20 blood requests (password: demo1234)")
finally:
    db.close()
