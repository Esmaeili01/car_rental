## Car Rental Project (Django + PostgreSQL)

Simple car rental web application for a cloud computing course.

### Main Features
- Custom auth with `phone_number` login (and email/phone sign in support).
- User roles: `renter`, `owner`, `admin`, `superadmin`.
- Car listing with image upload.
- Search/filter cars.
- Rent request flow with payment and status updates.
- Car comments and score system.
- Dashboard with role-based sections.
- Owner balance update after successful payment.

---

## Tech Stack
- Python 3.11
- Django 5.x
- PostgreSQL
- Bootstrap 5
- Docker + Docker Compose

---

## Project Structure
- `car_rental/` Django project config (`settings.py`, `urls.py`)
- `rental/` main app (models, views, templates, migrations)
- `media/` uploaded car images
- `static/` static assets
- `db_schema.sql` raw database schema reference

---

## Environment Variables
Create/update `.env` in project root:

```env
DB_NAME=car_rental_db
DB_USER=rental_user
DB_PASSWORD=asdf123456789
DB_HOST=localhost
DB_PORT=5432
SECRET_KEY=your-secret-key
DEBUG=True
```

For Docker, `DB_HOST` is overridden to `db` by `docker-compose.yml`.

---

## Run Locally (without Docker)

1. Create and activate virtualenv.
2. Install dependencies:

```bash
pip install -r requirements.txt
```

3. Apply migrations:

```bash
python manage.py migrate
```

4. Run server:

```bash
python manage.py runserver
```

Open: `http://127.0.0.1:8000`

---

## Run with Docker

Build and run:

```bash
docker compose up --build
```

Open: `http://localhost:8000`

Services:
- `web` (Django)
- `db` (PostgreSQL)

---

## Database Notes (Important)

Schema changes for key columns (including `cars.max_days` and `users.balance`) are now enforced by migrations.

Use:

```bash
python manage.py migrate
```

If running with Docker:

```bash
docker compose up --build
```

---

## Useful Commands

Django health check:

```bash
python manage.py check
```

Open DB shell in Docker:

```bash
docker compose exec db psql -U rental_user -d car_rental_db
```

Stop containers:

```bash
docker compose down
```

---

## Notes
- Car images are stored in `media/` (Docker volume-backed in compose).
- Database stores paths/relations, not image binary data.
- Current setup is suitable for development/course deployment.
