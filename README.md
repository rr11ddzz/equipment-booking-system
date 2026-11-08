# Equipment Booking System

A Django web application for managing equipment availability, user access and reservations.

## Features represented in the codebase

- User registration, login and approval-aware access control
- Search and sorting for the equipment catalogue
- Equipment records with device type, CPU, GPU and RAM details
- Booking and return dates with pending, approved, returned and cancelled states
- Inventory counts, device audits and report records

## Technology

- Python and Django 4.2
- SQLite for local development
- Django templates and the built-in authentication system

## Run locally

1. Create and activate a Python virtual environment.
2. Install the dependency: `pip install -r requirements.txt`.
3. Copy `.env.example` to `.env`, choose a long random `DJANGO_SECRET_KEY`, then load the values into your shell.
4. Run `python manage.py migrate` and `python manage.py runserver`.

The repository intentionally excludes the local database and credentials. It begins with an empty local database after migrations.
