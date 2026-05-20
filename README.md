# Healthcare Backend System

Django REST Framework backend for secure management of patients, doctors, and patient-doctor assignments.

## Stack

- Django 6
- Django REST Framework
- SimpleJWT
- PostgreSQL via `psycopg` when configured with `.env`
- SQLite fallback for local development when `DB_NAME` is empty or unset

## Setup

```bash
source .venv/bin/activate
python -m pip install -r requirements.txt
python WhatBytesAssignment/manage.py migrate
python WhatBytesAssignment/manage.py runserver
```


## API Endpoints

Authentication:

- `POST /api/auth/register/`
- `POST /api/auth/login/`
- `POST /api/auth/token/refresh/`

Patients:

- `POST /api/patients/`
- `GET /api/patients/`
- `GET /api/patients/<id>/`
- `PUT /api/patients/<id>/`
- `DELETE /api/patients/<id>/`

Doctors:

- `POST /api/doctors/`
- `GET /api/doctors/`
- `GET /api/doctors/<id>/`
- `PUT /api/doctors/<id>/`
- `DELETE /api/doctors/<id>/`

Mappings:

- `POST /api/mappings/`
- `GET /api/mappings/`
- `GET /api/mappings/<patient_id>/`
- `DELETE /api/mappings/<mapping_id>/`

Protected endpoints require:

```http
Authorization: Bearer <access_token>
```

## Tests

```bash
python -m pytest WhatBytesAssignment
```

