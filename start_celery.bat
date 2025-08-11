@echo off
echo Starting Celery Worker for Medication Reminder...
echo Make sure Redis server is running first!
echo.
call medication_env\Scripts\activate
celery -A medication_reminder worker -l info
@REM celery -A medication_reminder worker -l info --pool=eventlet --concurrency=1
pause
