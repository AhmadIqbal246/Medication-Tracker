@echo off
echo Starting Django Development Server...
echo.
call medication_env\Scripts\activate
python manage.py runserver
pause
