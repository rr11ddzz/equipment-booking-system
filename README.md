# Equipment Booking System

A Django coursework application for discovering equipment and requesting reservations. Includes account approval, a searchable catalogue, equipment specifications and user-linked bookings.

[Project case study and original screenshots](https://rr11ddzz.github.io/portfolio/projects/equipment-booking/)

## November 2026 engineering update

The original coursework is preserved in repository history. This later, AI-assisted maintenance pass adds:

- Ownership-scoped cancellation using POST and CSRF protection; cancelled records remain in the history.
- Server-side validation for missing, malformed, past and reversed dates.
- Rejection of unavailable equipment and overlapping active reservations, including open-ended legacy bookings.
- Approval checks when creating reservations.
- 19 automated regression tests covering access, dates, conflicts, cancellation, CSRF and repeatable sample data.
- Django 5.2.19 and a template path that works independently of the shell's working directory.

The work is a documented maintenance exercise, not a claim that these improvements were part of the original university submission.

## Run locally

Use Python 3.12 (the version used for this verification) and a virtual environment. On macOS/Linux, from this repository:

```sh
python3 -m venv .venv
source .venv/bin/activate
python -m pip install -r requirements.txt
export DJANGO_SECRET_KEY="$(python -c 'import secrets; print(secrets.token_urlsafe(48))')"
export DJANGO_DEBUG=true
export DJANGO_ALLOWED_HOSTS=localhost,127.0.0.1
python manage.py migrate
python manage.py seed_demo
python manage.py createsuperuser
python manage.py runserver
```

Open http://127.0.0.1:8000/admin/ with the local superuser you just created. Register a separate user through `/register/`, then enable that user's **ApprovalStatus** in the admin before signing in at `/login/`. No shared demo password is committed. `seed_demo` creates three fictional equipment items and can be repeated without duplicating them; it does not create accounts or overwrite existing equipment.

The `.env.example` documents environment settings; the application reads shell environment variables and does not automatically load `.env` files. The local database is excluded from Git.

## Run the checks

With the environment above active:

```sh
python manage.py check
python manage.py makemigrations --check --dry-run
python manage.py test app1
```

Verified on 11 November 2026 with Python 3.12, Django 5.2.19 and SQLite: **19 tests passed**. Django's system check reported no issues and no model migration changes were detected. Tests use an isolated test database. This is not a production security audit.

## Reservation rules

- Both dates are required. The start must be today or later; the end may equal the start.
- Dates are inclusive: returning on a date prevents another reservation starting on that same date.
- Pending and approved bookings block overlapping dates, except records rejected by an administrator. Cancelled and returned bookings do not block dates.
- An active legacy booking with no return date is treated as open-ended.
- Only the signed-in owner can cancel a pending or approved booking.

## Limits and next steps

SQLite is intended for a local demonstration. The booking view uses an atomic transaction and requests an equipment-row lock, but SQLite does not implement `select_for_update` row locking. The tests are sequential and do **not** prove concurrent booking protection. Before shared deployment, use a suitable database, test simultaneous requests and enforce consistent rules for administrative edits.

Inventory counts, audit and report models are present, but are not a complete operational asset-management product. Account recovery, production hosting, browser accessibility and the full admin lifecycle require additional work. External Bootstrap assets are used by the original templates.

## Framework reference

[Django supported versions](https://www.djangoproject.com/download/) and [queryset locking behaviour](https://docs.djangoproject.com/en/5.2/ref/models/querysets/#select-for-update).
