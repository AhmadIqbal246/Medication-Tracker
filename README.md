# Medication Reminder Web Application

A simple Django-based web application for managing medication schedules with email reminders using Celery and Redis.

## Features

### Authentication System
- User registration with username, email, and password
- User login/logout functionality
- Email verification for medication reminders

### Medication Management
- Create, Read, Update, Delete (CRUD) medications
- Set medication name, dosage, and exact scheduled date/time
- Mark medications as "Pending" or "Taken"
- Visual indicators for overdue medications
- User-specific medication lists

### Email Reminders
- Automatic email reminders sent at scheduled times
- Uses Celery for background task processing
- Redis as message broker
- SMTP email backend configuration

### Frontend
- Clean, responsive HTML templates
- Vanilla CSS styling (no external frameworks)
- JavaScript for dynamic interactions (AJAX)
- Mark medications as taken without page reload
- Delete medications with confirmation

## Technical Stack

- **Backend**: Django 4.2.7
- **Task Queue**: Celery 5.3.4
- **Message Broker**: Redis 5.0.1
- **Database**: SQLite (default)
- **Frontend**: HTML5, CSS3, Vanilla JavaScript
- **Email**: Django SMTP backend

## Installation Instructions

### Prerequisites
- Python 3.8 or higher
- Redis server
- SMTP email account (Gmail recommended)

### Step 1: Clone and Setup Virtual Environment
```bash
# Navigate to your project directory
cd "D:\med tracker"

# Create virtual environment
python -m venv medication_env

# Activate virtual environment
# On Windows:
medication_env\Scripts\activate
# On macOS/Linux:
source medication_env/bin/activate
```

### Step 2: Install Dependencies
```bash
pip install -r requirements.txt
```

### Step 3: Configure Email Settings
Edit `medication_reminder/settings.py` and update these email settings:

```python
EMAIL_HOST_USER = 'your-email@gmail.com'  # Replace with your Gmail
EMAIL_HOST_PASSWORD = 'your-app-password'  # Replace with Gmail App Password
DEFAULT_FROM_EMAIL = 'your-email@gmail.com'  # Replace with your Gmail
```

**For Gmail:**
1. Enable 2-factor authentication
2. Generate an App Password: https://support.google.com/accounts/answer/185833
3. Use the App Password (not your regular password)

### Step 4: Database Setup
```bash
# Create and apply database migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional, for admin access)
python manage.py createsuperuser
```

### Step 5: Install Redis

**Windows:**
1. Download Redis from: https://github.com/microsoftarchive/redis/releases
2. Install and start Redis server
3. Or use WSL with: `sudo apt-get install redis-server`

**macOS:**
```bash
brew install redis
brew services start redis
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt-get install redis-server
sudo systemctl start redis
```

## Running the Application

You need to run **three separate processes** in different terminal windows:

### Terminal 1: Redis Server
```bash
redis-server
```

### Terminal 2: Celery Worker
```bash
# Navigate to project directory and activate virtual environment
cd "D:\med tracker"
medication_env\Scripts\activate

# Start Celery worker
celery -A medication_reminder worker -l info
```

### Terminal 3: Django Server
```bash
# Navigate to project directory and activate virtual environment
cd "D:\med tracker" 
medication_env\Scripts\activate

# Start Django development server
python manage.py runserver
```

## Usage Guide

### 1. User Registration
1. Open http://127.0.0.1:8000 in your browser
2. Click "Sign up here"
3. Enter username, email, and password
4. **Important**: Use a real email address for medication reminders

### 2. Adding Medications
1. After login, click "Add New Medication"
2. Enter medication name (e.g., "Aspirin")
3. Enter dosage information (e.g., "2 tablets, 500mg each")
4. Set the exact date and time for reminder
5. Click "Save Medication"

### 3. Managing Medications
- **View All**: See pending and taken medications on the main page
- **Mark as Taken**: Click green button to mark medication as taken
- **Edit**: Modify medication details and reschedule
- **Delete**: Remove medication (with confirmation)

### 4. Email Reminders
- Emails are automatically sent at the scheduled time
- Check your email (including spam folder) for reminders
- Reminders include medication name and scheduled time

### 5. Visual Indicators
- **Green cards**: Taken medications
- **Red cards**: Overdue medications
- **White cards**: Pending medications
- **"OVERDUE" label**: Medications past their scheduled time

## Application Structure

```
medication_reminder/
├── medication_reminder/          # Main Django project
│   ├── __init__.py
│   ├── settings.py              # Configuration
│   ├── urls.py                  # Main URL routing
│   ├── wsgi.py
│   └── celery.py               # Celery configuration
├── accounts/                    # Authentication app
│   ├── templates/accounts/     # Login/signup templates
│   ├── forms.py               # Authentication forms
│   ├── views.py               # Authentication views
│   └── urls.py                # Authentication URLs
├── medications/                # Medication management app
│   ├── templates/medications/ # Medication templates
│   ├── models.py             # Medication model
│   ├── forms.py              # Medication forms
│   ├── views.py              # Medication views
│   ├── tasks.py              # Celery email tasks
│   ├── admin.py              # Admin configuration
│   └── urls.py               # Medication URLs
├── requirements.txt          # Python dependencies
└── README.md                # This file
```

## Key Features Explained

### Email Workflow
1. User creates medication with scheduled time
2. Django saves medication to database
3. Celery task scheduled for exact datetime
4. Task sent to Redis message broker
5. Celery worker processes task at scheduled time
6. SMTP email sent to user's registered email

### AJAX Functionality
- Mark as taken without page refresh
- Delete medications with confirmation
- Real-time status updates
- Enhanced user experience

### Security Features
- CSRF protection on all forms
- User authentication required for medication access
- User-specific medication filtering
- Secure password validation

## Troubleshooting

### Common Issues

**1. Email not sending:**
- Check EMAIL_HOST_USER and EMAIL_HOST_PASSWORD in settings.py
- Ensure Gmail App Password is used (not regular password)
- Check spam folder for test emails

**2. Celery worker not starting:**
- Ensure Redis server is running
- Check Redis connection: `redis-cli ping` should return `PONG`
- Verify celery command syntax

**3. Database errors:**
- Run: `python manage.py makemigrations medications`
- Run: `python manage.py migrate`

**4. Template not found errors:**
- Ensure template directories exist
- Check INSTALLED_APPS includes both 'accounts' and 'medications'

### Development Tips

**Testing Email Locally:**
For testing without sending real emails, change in settings.py:
```python
EMAIL_BACKEND = 'django.core.mail.backends.console.EmailBackend'
```

**Celery Task Monitoring:**
Use Celery Flower for task monitoring:
```bash
pip install flower
celery -A medication_reminder flower
```
Then visit: http://localhost:5555

## Admin Interface

Access Django admin at: http://127.0.0.1:8000/admin/

**Features:**
- View all medications
- Filter by status, user, date
- Search medications
- Manual medication management

## Future Enhancements

Potential improvements for this application:
- Multiple medication schedules (daily, weekly, monthly)
- SMS reminders via Twilio
- Mobile-responsive design improvements  
- Medication history and analytics
- Family/caregiver sharing features
- Medicine interaction warnings
- Prescription refill reminders

## Support

For issues or questions:
1. Check the troubleshooting section above
2. Ensure all prerequisites are installed correctly
3. Verify all three processes are running (Redis, Celery, Django)

## License

This project is for educational purposes. Feel free to modify and adapt for your needs.
