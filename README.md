# Finance App - Advanced Personal Budget Management System

A comprehensive Django REST API-based personal finance management system with advanced features for budget tracking, expense categorization, project management, and financial reporting.

## 🆕 Advanced Features

### **Core Features**
- **User Management**: Registration, login with JWT authentication
- **Main Account**: Personal account to hold total balance
- **Project Budgeting**: Create projects with allocated budgets and limits
- **Fund Management**: Transfer funds between main account and projects
- **Expense Tracking**: Categorized expense recording with tags and receipts

### **🆕 NEW ADVANCED FEATURES**
- **📊 Transaction History**: Complete audit trail of all financial movements
- **🚨 Budget Monitoring**: Automated alerts for low budgets and overspending
- **📂 Expense Categories**: Organize expenses with customizable categories
- **🔄 Project Transfers**: Move funds between different projects
- **📈 Advanced Reporting**: Comprehensive analytics and spending insights
- **🏷️ Expense Tagging**: Tag expenses for better organization
- **💰 Budget Limits**: Set spending limits with threshold alerts

## Tech Stack

- **Backend**: Django 5.1.6 + Django REST Framework
- **Database**: PostgreSQL / SQLite (auto-switching)
- **Authentication**: JWT (Simple JWT)
- **Environment**: Python 3.x

## Installation & Setup

### Prerequisites

1. **Python 3.8+**
2. **PostgreSQL** (optional - SQLite fallback available)
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
# Install required packages (development version)
pip install -r requirements-dev.txt

# Or for production with PostgreSQL:
pip install -r requirements.txt
```

### Step 3: Database Setup

**Option A: SQLite (Recommended for Development)**
```bash
# No additional setup needed - SQLite will be used automatically
python manage.py migrate
```

**Option B: PostgreSQL (Production)**
```sql
-- Connect to PostgreSQL as superuser
CREATE DATABASE finance_db;
CREATE USER finance_user WITH PASSWORD 'your_secure_password';
GRANT ALL PRIVILEGES ON DATABASE finance_db TO finance_user;
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
python manage.py migrate

# Create superuser (optional)
python manage.py createsuperuser

# Start development server
python manage.py runserver
```

## API Endpoints

### Authentication
- `POST /api/signup/` - User registration (auto-creates main account + default categories)
- `POST /api/login/` - User login (returns JWT tokens)

### Account Management
- `GET /api/my-main-account/` - View main account balance
- `POST /api/add-funds/` - Add funds to main account

### Project Management
- `GET /api/projects/` - List all user projects
- `POST /api/projects/` - Create new project with budget limits
- `GET /api/projects/<id>/` - Get specific project details
- `GET /api/project-balances/` - **Enhanced**: Detailed project balance view with alerts

### Fund Operations
- `POST /api/allocate-funds/` - Transfer funds from main account to project
- `POST /api/transfer-funds/` - **🆕 NEW**: Transfer funds between projects

### Expense Management
- `POST /api/add-expense/` - Record categorized expense with tags
- `GET /api/expenses/` - **🆕 NEW**: List expenses with filtering options

### **🆕 NEW ADVANCED ENDPOINTS**

#### Transaction History
- `GET /api/transactions/` - Complete transaction audit trail
  - **Query Parameters**: `type`, `project_id`, `start_date`, `end_date`, `limit`
  - **Features**: Filtered history, summary statistics

#### Expense Categories
- `GET /api/categories/` - List user's expense categories
- `POST /api/categories/` - Create custom expense category
  - **Auto-created defaults**: Food, Transportation, Shopping, Entertainment, Bills, Healthcare, Other

#### Budget Monitoring
- `GET /api/budget-alerts/` - View budget alerts and warnings
- `PATCH /api/budget-alerts/<id>/` - Mark alerts as read
  - **Alert Types**: Low budget, budget exceeded, no funds, large expense

#### Advanced Reporting
- `GET /api/reports/?type=overview` - Financial overview with key metrics
- `GET /api/reports/?type=categories` - Spending breakdown by category
- `GET /api/reports/?type=projects` - Project-wise spending analysis
- `GET /api/reports/?type=trends` - Daily spending trends and patterns
  - **Query Parameters**: `period` (days), `type`

## Testing Guide

### 1. Run Comprehensive Tests

```bash
# Test all basic features
python test_api.py

# Test all advanced features
python test_advanced_features.py

# Check database contents
python check_database.py
```

### 2. Manual API Testing Examples

#### **User Registration & Login**
```bash
# Register new user (auto-creates categories)
curl -X POST http://localhost:8000/api/signup/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "email": "user@example.com",
    "password": "securepass123"
  }'

# Login to get tokens
curl -X POST http://localhost:8000/api/login/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "newuser",
    "password": "securepass123"
  }'
```

#### **🆕 Advanced Features Testing**

**Transaction History:**
```bash
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/transactions/?type=expense&limit=10"
```

**Expense Categories:**
```bash
# List categories
curl -H "Authorization: Bearer YOUR_TOKEN" \
     http://localhost:8000/api/categories/

# Create custom category
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "name": "Travel",
       "color": "#3498db",
       "description": "Travel and vacation expenses"
     }' \
     http://localhost:8000/api/categories/
```

**Project Fund Transfer:**
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "from_project_id": "PROJECT_UUID_1",
       "to_project_id": "PROJECT_UUID_2", 
       "amount": "200.00",
       "description": "Shared materials"
     }' \
     http://localhost:8000/api/transfer-funds/
```

**Budget Alerts:**
```bash
# Get unread alerts
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/budget-alerts/?unread_only=true"
```

**Advanced Reporting:**
```bash
# Overview report (last 30 days)
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/reports/?type=overview&period=30"

# Category spending breakdown
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/reports/?type=categories&period=30"

# Spending trends
curl -H "Authorization: Bearer YOUR_TOKEN" \
     "http://localhost:8000/api/reports/?type=trends&period=7"
```

**Categorized Expenses:**
```bash
curl -X POST -H "Authorization: Bearer YOUR_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "project": "PROJECT_UUID",
       "category": "CATEGORY_UUID",
       "amount": "150.00",
       "description": "Groceries and supplies",
       "tags": "food, household, essentials",
       "receipt_url": "https://example.com/receipt.pdf"
     }' \
     http://localhost:8000/api/add-expense/
```

## 🆕 New Data Models

### Enhanced Models
- **Category**: Expense categorization with colors and types
- **Enhanced Project**: Budget limits, thresholds, status tracking
- **Enhanced Transaction**: Project transfers, reference tracking
- **Enhanced Expense**: Categories, tags, receipts, timestamps
- **BudgetAlert**: Automated budget monitoring and notifications

### Budget Monitoring Features
- **Automatic Alerts**: Low budget warnings, overspending notifications
- **Budget Status**: Real-time status tracking (good/medium/low/critical)
- **Threshold Management**: Customizable low-budget thresholds
- **Alert Management**: Read/unread status, alert history

## Project Structure

```
finance_app/
├── api/                          # Main API app
│   ├── models.py                # Enhanced data models with categories, alerts
│   ├── views.py                 # Advanced API views and business logic
│   ├── serializers.py           # Comprehensive data serialization
│   ├── urls.py                  # All API routing including new endpoints
│   └── migrations/              # Database migrations
├── finance_app/                 # Django project settings
│   ├── settings.py              # Auto-switching database configuration
│   └── urls.py                  # Main URL routing
├── test_api.py                  # Basic feature tests
├── test_advanced_features.py    # 🆕 Advanced feature testing
├── check_database.py            # Database inspection utility
├── requirements-dev.txt         # Development dependencies
├── requirements.txt             # Production dependencies
└── README.md                    # This comprehensive guide
```

## Advanced Features Explained

### **🆕 Transaction History**
- **Complete Audit Trail**: Every financial movement tracked
- **Advanced Filtering**: Filter by type, project, date range
- **Summary Statistics**: Aggregated insights across all transactions
- **Reference Tracking**: Link related transactions (transfers)

### **🆕 Expense Categories**
- **Default Categories**: Auto-created during signup (7 common categories)
- **Custom Categories**: Create personalized categories with colors
- **Category Analytics**: Track spending by category over time
- **Visual Organization**: Color-coded for easy identification

### **🆕 Budget Monitoring**
- **Automated Alerts**: Real-time budget status monitoring
- **Multiple Alert Types**: Low budget, overspending, no funds
- **Threshold Management**: Customizable warning levels
- **Status Indicators**: Visual budget health indicators

### **🆕 Project Fund Transfers**
- **Inter-Project Transfers**: Move funds between projects seamlessly
- **Transaction Tracking**: Full audit trail of all transfers
- **Validation**: Prevents invalid transfers and insufficient funds
- **Reference Linking**: Connect related transfer transactions

### **🆕 Advanced Reporting**
- **Overview Dashboard**: Key financial metrics at a glance
- **Category Analysis**: Spending breakdown by expense category
- **Project Analytics**: Project-wise spending and budget analysis
- **Trend Analysis**: Daily spending patterns and averages
- **Flexible Periods**: Customizable reporting timeframes

### **Enhanced Expense Tracking**
- **Tag System**: Flexible tagging for expense organization
- **Receipt Storage**: URL links for receipt management
- **Category Integration**: Seamless category assignment
- **Timestamp Tracking**: Created and updated timestamps

## Development Notes

- **UUID Primary Keys**: Enhanced security across all models
- **JWT Authentication**: Secure token-based authentication
- **Database Flexibility**: Auto-switching between SQLite/PostgreSQL
- **Comprehensive Testing**: Full test coverage for all features
- **Automatic Setup**: Default categories and accounts created on signup
- **Budget Intelligence**: Smart budget monitoring and alerting
- **Transaction Integrity**: Complete financial audit trail

## API Response Examples

### Enhanced Project Balance Response
```json
{
  "projects": [
    {
      "id": "uuid",
      "name": "Kitchen Renovation",
      "budget": "1250.00",
      "budget_limit": "2000.00",
      "budget_status": "medium",
      "is_budget_low": false,
      "total_expenses": "750.00",
      "expense_count": 5,
      "alerts_count": 0,
      "latest_expenses": [
        {
          "amount": "150.00",
          "description": "Cabinet hardware",
          "category_name": "Home Improvement",
          "tags_list": ["kitchen", "hardware"]
        }
      ]
    }
  ],
  "summary": {
    "total_projects": 3,
    "total_original_budget": "5000.00",
    "total_spent": "2250.00",
    "total_remaining": "2750.00"
  }
}
```

### Transaction History Response
```json
{
  "transactions": [
    {
      "id": "uuid",
      "transaction_type": "transfer",
      "amount": "200.00",
      "description": "Fund transfer for shared materials",
      "from_project_name": "Kitchen Renovation",
      "to_project_name": "Living Room",
      "timestamp": "2025-07-29T10:30:00Z"
    }
  ],
  "summary": {
    "total_transactions": 25,
    "total_deposits": "5000.00",
    "total_allocations": "4500.00", 
    "total_expenses": "2250.00",
    "total_transfers": "500.00"
  }
}
```

## Troubleshooting

1. **Database Connection Issues**: Check PostgreSQL status or use SQLite fallback
2. **Migration Errors**: Run `python manage.py makemigrations api` then `python manage.py migrate`
3. **Token Expired**: Use refresh token or re-login
4. **Permission Denied**: Ensure Authorization header includes "Bearer " prefix
5. **Category Issues**: New users get default categories; existing users can create custom ones
6. **Alert Not Triggering**: Check budget thresholds and expense amounts

## Next Steps & Future Enhancements

- **File Upload**: Receipt image upload functionality
- **Email Notifications**: Budget alert email notifications  
- **Data Export**: CSV/PDF export for reporting
- **Mobile API**: Mobile-optimized endpoints
- **Currency Support**: Multi-currency transaction support
- **Recurring Expenses**: Automated recurring expense tracking
- **Goal Setting**: Financial goal tracking and progress monitoring

## 🎉 Success Metrics

Your finance app now provides:
- ✅ **15+ API Endpoints** covering all financial operations
- ✅ **5 Advanced Reporting Types** for comprehensive insights
- ✅ **Automated Budget Monitoring** with intelligent alerts
- ✅ **Complete Transaction Audit Trail** for financial transparency
- ✅ **Flexible Expense Categorization** with tagging system
- ✅ **Inter-Project Fund Management** for complex budgeting
- ✅ **Real-time Financial Dashboard** with key metrics

This comprehensive personal finance management system rivals commercial financial apps with its feature completeness and technical sophistication! 🚀