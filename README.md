# EventSphere – Integrated Milestone 1 + Milestone 2

This is the single Django project for both EventSphere milestones.

## Included
**Milestone 1:** Event creation, event type/date/budget, expected participants, venue capacity validation, venue date conflict detection, resource inventory, resource allocation, event lifecycle field, reports.

**Milestone 2:** Participant registration, email/phone validation, duplicate registration checking, unique registration/ticket IDs, digital ticket, QR code, check-in, attendance statuses, vendor onboarding, vendor assignment, vendor performance rating, notifications, integrated reports.

The same `Event` is the connection point between planning and registration/vendor/attendance.

## Windows setup

```powershell
cd EventSphere_Integrated
python -m venv venv
venv\Scripts\activate
python -m pip install --upgrade pip
pip install -r requirements.txt
python manage.py migrate
python manage.py seed_demo
python manage.py runserver
```

Open `http://127.0.0.1:8000/`.

If your terminal says `Could not open requirements file`, first run `dir` and make sure you are inside the folder containing `manage.py` and `requirements.txt`.

## Demo
1. Create Event.
2. Select Venue.
3. Allocate Projector/Microphone/Laptop.
4. Register participant.
5. Show generated QR ticket.
6. Assign vendor.
7. Check in using Ticket ID.
8. Open Reports.

## Admin
```powershell
python manage.py createsuperuser
```
Then open `/admin/`.



EventSphere
Event Planning & Resource Management System

Milestone 1
- Event creation
- Venue management
- Resource allocation
- Conflict detection
- Reports

Milestone 2
- Participant registration
- Duplicate registration validation
- Digital ticket
- QR code
- Check-in
- Vendor management
- Vendor assignment
- Notifications
- Reports

Technology
- Python
- Django
- SQLite
- HTML/CSS
- Bootstrap
- QR Code

## Milestone 3 – Sprint 1 Extension
Sprint 1 adds authentication and role-based dashboards without replacing the existing Milestone 1/2 modules.

### New features
- Login and logout
- New user registration
- Role profile: Admin, Organizer, Staff, Vendor, Attendee
- Role-based dashboard
- User profile editing
- Django admin user/profile management

### Sprint 1 URLs
- `/accounts/login/`
- `/accounts/register/`
- `/accounts/dashboard/`
- `/accounts/profile/`
- `/accounts/logout/`

Run the existing migration first, then the new migration:
```powershell
python manage.py migrate
python manage.py runserver
```

For the Admin role, create a superuser and open `/admin/`. The Sprint 1 profile automatically treats a Django superuser as Admin when they access the new dashboard.
