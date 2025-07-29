from django.urls import path
from .views import (UserMainAccountView, UserSignupView, UserLoginView, ProjectListCreateView, 
                   ProjectDetailView, AllocateFundsView, UserCreateView, AddExpenseView, 
                   ProjectBalanceView, TransactionHistoryView, CategoryListCreateView,
                   ProjectTransferView, BudgetAlertsView, ReportingView, ExpenseListView)
from api.views import AddFundsView

urlpatterns = [
    # Authentication
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('users/', UserCreateView.as_view(), name='user-create'),
    
    # Account Management
    path('my-main-account/', UserMainAccountView.as_view(), name='my-main-account'),
    path('add-funds/', AddFundsView.as_view(), name='add-funds'),
    
    # Project Management
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('project-balances/', ProjectBalanceView.as_view(), name='project-balances'),
    
    # Fund Operations
    path('allocate-funds/', AllocateFundsView.as_view(), name='allocate-funds'),
    path('transfer-funds/', ProjectTransferView.as_view(), name='transfer-funds'),  # 🆕 NEW
    
    # Expense Management
    path('add-expense/', AddExpenseView.as_view(), name='add-expense'),
    path('expenses/', ExpenseListView.as_view(), name='expense-list'),  # 🆕 NEW
    
    # Categories
    path('categories/', CategoryListCreateView.as_view(), name='category-list'),  # 🆕 NEW
    
    # 🆕 NEW ADVANCED FEATURES
    path('transactions/', TransactionHistoryView.as_view(), name='transaction-history'),
    path('budget-alerts/', BudgetAlertsView.as_view(), name='budget-alerts'),
    path('budget-alerts/<uuid:alert_id>/', BudgetAlertsView.as_view(), name='budget-alert-detail'),
    path('reports/', ReportingView.as_view(), name='reports'),

]
