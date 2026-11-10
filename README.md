# Django course and mock-exam application

## Setup

```bash
python -m venv .venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate
pip install -r requirements.txt
python manage.py migrate
python manage.py createsuperuser
python manage.py runserver
```

Visit `/admin/` to add courses, lessons, questions, and answer choices. Visit `/courses/<course_id>/` to view a course and take lesson exams. Exam submission and result pages require a signed-in user.

This repository includes a local-development Django secret key and `DEBUG=True`; configure secure settings before deploying.
