# Finance App - Personal Budget Management System

A Django REST API-based personal finance management system that allows users to manage main accounts, create budget projects, allocate funds, and track expenses.

## Features

- **User Management**: Registration, login with JWT authentication
- **Main Account**: Personal account to hold total balance
- **Project Budgeting**: Create projects with allocated budgets
- **Fund Management**: Transfer funds from main account to projects
- **Expense Tracking**: Record and track expenses against projects
- **Balance Overview**: Detailed view of project balances and spending

## Tech Stack

- **Backend**: Django 5.1.6 + Django REST Framework
- **Database**: PostgreSQL
- **Authentication**: JWT (Simple JWT)
- **Environment**: Python 3.x

## Installation & Setup

### Prerequisites

1. **Python 3.8+**
2. **PostgreSQL** (running on localhost:5432)
3. **Git**

### Step 1: Clone and Setup Environment

```bash
# Clone the repository
git clone <your-repo-url>
cd finance_app

# Create virtual environment
python -m venv env

# Activate virtual environment
# On Windows:
env\Scripts\activate
# On macOS/Linux:
source env/bin/activate
```

### Step 2: Install Dependencies

```bash
# Install required packages
pip install django==5.1.6
pip install djangorestframework
pip install djangorestframework-simplejwt
pip install psycopg2-binary
pip install python-dotenv
```

### Step 3: Database Setup

1. **Create PostgreSQL Database:**
```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE finance_db;
CREATE USER finance_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE finance_db TO finance_user;
```

2. **Create Environment File:**
```bash
# Create env/.env file
mkdir env
```

Create `env/.env` with:
```
DB_NAME=finance_db
DB_USER=finance_user
DB_PASSWORD=your_secure_password
```

### Step 4: Django Setup

```bash
# Run migrations
python manage.py makemigrations
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/signup/` - User registration
- `POST /api/login/` - User login (returns JWT tokens)

### Account Management
- `GET /api/my-main-account/` - View main account balance
- `POST /api/add-funds/` - Add funds to main account

### Project Management
- `GET /api/projects/` - List all user projects
- `POST /api/projects/` - Create new project
- `GET /api/projects/<id>/` - Get specific project details
- `GET /api/project-balances/` - **NEW**: Detailed project balance view

### Fund Operations
- `POST /api/allocate-funds/` - Transfer funds from main account to project
- `POST /api/add-expense/` - Record expense against project

## Testing Guide

### 1. User Registration

```bash
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "securepass123"
  }'
```

### 2. User Login

```bash
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "password": "securepass123"
  }'
```

**Save the access token from response for subsequent requests.**

### 3. Add Funds to Main Account

```bash
curl -X POST http://localhost:8000/api/add-funds/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "amount": "1000.00"
  }'
```

### 4. Check Main Account Balance

```bash
curl -X GET http://localhost:8000/api/my-main-account/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

### 5. Create a Project

```bash
curl -X POST http://localhost:8000/api/projects/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "name": "Home Renovation",
    "budget": "0.00",
    "user": "YOUR_USER_ID"
  }'
```

### 6. Allocate Funds to Project

```bash
curl -X POST http://localhost:8000/api/allocate-funds/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "project_id": "PROJECT_UUID",
    "amount": "500.00"
  }'
```

### 7. Add Expense to Project

```bash
curl -X POST http://localhost:8000/api/add-expense/ \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN" \
  -d '{
    "project": "PROJECT_UUID",
    "amount": "150.00",
    "description": "Paint and brushes"
  }'
```

### 8. **NEW**: Check Project Balances

```bash
curl -X GET http://localhost:8000/api/project-balances/ \
  -H "Authorization: Bearer YOUR_ACCESS_TOKEN"
```

**Response includes:**
- Individual project details with remaining budgets
- Total expenses per project
- Latest 3 expenses per project
- Summary statistics across all projects

## Project Structure

```
finance_app/
├── api/                    # Main API app
│   ├── models.py          # Data models (User, MainAccount, Project, Transaction, Expense)
│   ├── views.py           # API views and business logic
│   ├── serializers.py     # Data serialization/validation
│   ├── urls.py            # API routing
│   └── migrations/        # Database migrations
├── finance_app/           # Django project settings
│   ├── settings.py        # Configuration
│   └── urls.py            # Main URL routing
├── db_setup/              # Database initialization scripts
├── env/                   # Environment variables
└── manage.py              # Django management script
```

## Key Features Explained

### Main Account System
- Each user automatically gets a MainAccount upon registration
- Acts as the primary wallet for all funds
- Funds are transferred from here to individual projects

### Project Budgeting
- Create projects for different goals (e.g., "Home Renovation", "Vacation")
- Allocate specific amounts from main account to each project
- Track remaining budget as expenses are recorded

### Expense Tracking
- Record expenses against specific projects
- Automatically deducts from project budget
- Maintains history of all expenses with descriptions

### **NEW: Project Balance View**
- Comprehensive overview of all projects
- Shows total expenses, remaining budget, and expense count
- Includes latest expenses for quick reference
- Summary statistics across all projects

## Development Notes

- Uses UUID primary keys for better security
- JWT authentication with refresh/access token pattern
- PostgreSQL for reliable financial data storage
- Django REST Framework for robust API development
- Automatic main account creation on user signup

## Troubleshooting

1. **Database Connection Issues**: Check PostgreSQL is running and credentials in `.env`
2. **Migration Errors**: Run `python manage.py makemigrations api` then `python manage.py migrate`
3. **Token Expired**: Use refresh token to get new access token
4. **Permission Denied**: Ensure Authorization header includes "Bearer " prefix

## Next Steps

- Transaction history view
- Budget alerts and notifications
- Fund transfers between projects
- Expense categorization
- Reporting and analytics