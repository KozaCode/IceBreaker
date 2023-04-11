call python -m venv venv
call venv\Scripts\activate
call pip install -r requirements.txt
set FLASK_APP=app.py
set FLASK_ENV=development