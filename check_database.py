#!/usr/bin/env python3
"""
Database checker and API token generator
Shows existing users, projects, and helps get API tokens
"""

import os
import sys
import django
import requests
import json

# Setup Django
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'finance_app.settings')
django.setup()

from api.models import User, MainAccount, Project, Expense

BASE_URL = "http://localhost:8000/api"

def check_database_contents():
    """Check what's currently in the database"""
    print("🗄️  DATABASE CONTENTS")
    print("=" * 50)
    
    # Check Users
    users = User.objects.all()
    print(f"👥 USERS ({users.count()}):")
    for user in users:
        print(f"   📝 Username: {user.username}")
        print(f"   📧 Email: {user.email}")
        print(f"   🆔 ID: {user.id}")
        print(f"   🏦 Has Main Account: {hasattr(user, 'main_account')}")
        if hasattr(user, 'main_account'):
            print(f"   💰 Main Account Balance: ${user.main_account.balance}")
        print()
    
    # Check Projects
    projects = Project.objects.all()
    print(f"📋 PROJECTS ({projects.count()}):")
    for project in projects:
        print(f"   🏷️  Name: {project.name}")
        print(f"   👤 Owner: {project.user.username}")
        print(f"   💰 Budget: ${project.budget}")
        print(f"   🆔 ID: {project.id}")
        expense_count = project.expenses.count()
        total_expenses = sum(expense.amount for expense in project.expenses.all())
        print(f"   💸 Expenses: {expense_count} totaling ${total_expenses}")
        print()
    
    # Check Expenses
    expenses = Expense.objects.all()
    print(f"💸 EXPENSES ({expenses.count()}):")
    for expense in expenses:
        print(f"   📝 Description: {expense.description}")
        print(f"   💰 Amount: ${expense.amount}")
        print(f"   📋 Project: {expense.project.name}")
        print(f"   📅 Date: {expense.created_at.strftime('%Y-%m-%d %H:%M')}")
        print()

def get_api_token(username="testuser_demo", password="securepass123"):
    """Get JWT token for API testing"""
    print("🔑 GETTING API TOKEN")
    print("=" * 50)
    
    data = {
        "username": username,
        "password": password
    }
    
    try:
        response = requests.post(f"{BASE_URL}/login/", json=data)
        if response.status_code == 200:
            tokens = response.json()
            print(f"✅ Login successful!")
            print(f"🎫 Access Token: {tokens['access']}")
            print(f"🔄 Refresh Token: {tokens['refresh']}")
            print()
            return tokens['access']
        else:
            print(f"❌ Login failed: {response.status_code} - {response.text}")
            return None
    except Exception as e:
        print(f"❌ Error connecting to server: {e}")
        print("💡 Make sure Django server is running: python manage.py runserver")
        return None

def test_project_balance_endpoint(token):
    """Test the Project Balance View endpoint"""
    print("📊 TESTING PROJECT BALANCE VIEW")
    print("=" * 50)
    
    headers = {"Authorization": f"Bearer {token}"}
    
    try:
        response = requests.get(f"{BASE_URL}/project-balances/", headers=headers)
        if response.status_code == 200:
            data = response.json()
            print("✅ Project Balance View successful!")
            print()
            print("📈 SUMMARY:")
            summary = data.get("summary", {})
            for key, value in summary.items():
                print(f"   {key}: {value}")
            
            print()
            print("📋 PROJECTS:")
            for project in data.get("projects", []):
                print(f"   🏷️  {project['name']}")
                print(f"      💰 Budget: ${project['budget']}")
                print(f"      💸 Expenses: ${project['total_expenses']}")
                print(f"      📊 Count: {project['expense_count']}")
                print()
        else:
            print(f"❌ Project balance check failed: {response.status_code} - {response.text}")
    except Exception as e:
        print(f"❌ Error: {e}")

def show_curl_examples(token):
    """Show curl command examples"""
    print("🌐 CURL COMMAND EXAMPLES")
    print("=" * 50)
    
    print("1️⃣  Test Project Balance View:")
    print(f'curl -H "Authorization: Bearer {token}" \\')
    print(f'     http://localhost:8000/api/project-balances/')
    print()
    
    print("2️⃣  Check Main Account:")
    print(f'curl -H "Authorization: Bearer {token}" \\')
    print(f'     http://localhost:8000/api/my-main-account/')
    print()
    
    print("3️⃣  List All Projects:")
    print(f'curl -H "Authorization: Bearer {token}" \\')
    print(f'     http://localhost:8000/api/projects/')
    print()
    
    print("4️⃣  Add Funds to Main Account:")
    print(f'curl -X POST -H "Authorization: Bearer {token}" \\')
    print(f'     -H "Content-Type: application/json" \\')
    print(f'     -d \'{{"amount": "100.00"}}\' \\')
    print(f'     http://localhost:8000/api/add-funds/')
    print()

def show_known_credentials():
    """Show known test credentials"""
    print("🔐 KNOWN TEST CREDENTIALS")
    print("=" * 50)
    print("From test_api.py script:")
    print("   Username: testuser_demo")
    print("   Password: securepass123")
    print("   Email: demo@example.com")
    print()
    print("From docs.txt (if still valid):")
    print("   Username: testuser6")
    print("   Token in docs.txt (may be expired)")
    print()

def main():
    print("🚀 FINANCE APP DATABASE & API CHECKER")
    print("=" * 60)
    print()
    
    # Check database contents
    check_database_contents()
    
    # Show known credentials
    show_known_credentials()
    
    # Get API token
    token = get_api_token()
    
    if token:
        # Test the project balance endpoint
        test_project_balance_endpoint(token)
        
        # Show curl examples
        show_curl_examples(token)
    
    print("🎯 TIP: Save the access token above to use in your API tests!")

if __name__ == "__main__":
    main() 