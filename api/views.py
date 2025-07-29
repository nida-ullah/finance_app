
from .models import MainAccount
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import (UserSignupSerializer, ProjectSerializer, FundAllocationSerializer, 
                         UserSerializer, MainAccountSerializer, ExpenseSerializer, CategorySerializer,
                         TransactionSerializer, BudgetAlertSerializer, ProjectTransferSerializer)
from .models import Project, MainAccount, Expense, Category, Transaction, BudgetAlert
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated
from django.db.models import Q, Sum, Count
from django.utils import timezone
from datetime import datetime, timedelta
import uuid


User = get_user_model()

# Signup View


class UserSignupView(APIView):
    def post(self, request):
        serializer = UserSignupSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserMainAccountView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        try:
            main_account = MainAccount.objects.get(user=request.user)
            serializer = MainAccountSerializer(main_account)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except MainAccount.DoesNotExist:
            return Response({"error": "Main account not found"}, status=status.HTTP_404_NOT_FOUND)


class ProjectListCreateView(generics.ListCreateAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class UserCreateView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = UserSerializer


class ProjectDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Project.objects.all()
    serializer_class = ProjectSerializer


class AllocateFundsView(APIView):
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = FundAllocationSerializer(data=request.data)
        if serializer.is_valid():
            try:
                project = Project.objects.get(
                    id=serializer.validated_data['project_id'], user=request.user)
                main_account = MainAccount.objects.get(user=request.user)

                amount = serializer.validated_data['amount']
                
                if main_account.balance >= amount:
                    # Update balances
                    main_account.balance -= amount
                    project.budget += amount
                    main_account.save()
                    project.save()
                    
                    # Create transaction record
                    Transaction.objects.create(
                        user=request.user,
                        project=project,
                        main_account=main_account,
                        transaction_type="allocate",
                        amount=amount,
                        description=f"Allocated funds to {project.name}"
                    )
                    
                    return Response({"message": "Funds allocated successfully"}, status=status.HTTP_200_OK)
                return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
            except Project.DoesNotExist:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class UserLoginView(APIView):
    permission_classes = [permissions.AllowAny]

    def post(self, request):
        username = request.data.get('username')
        password = request.data.get('password')

        user = User.objects.filter(username=username).first()
        if user and user.check_password(password):
            refresh = RefreshToken.for_user(user)
            return Response({
                'refresh': str(refresh),
                'access': str(refresh.access_token)
            })
        return Response({"error": "Invalid credentials"}, status=400)


class AddFundsView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        amount = request.data.get("amount")
        try:
            main_account = MainAccount.objects.get(user=request.user)
            amount_decimal = Decimal(str(amount))
            main_account.balance += amount_decimal
            main_account.save()
            
            # Create transaction record
            Transaction.objects.create(
                user=request.user,
                main_account=main_account,
                transaction_type="deposit",
                amount=amount_decimal,
                description="Deposit to main account"
            )
            
            return Response({"message": "Funds added successfully!", "balance": main_account.balance}, status=status.HTTP_200_OK)
        except MainAccount.DoesNotExist:
            return Response({"error": "Main account not found!"}, status=status.HTTP_404_NOT_FOUND)


class AddExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            try:
                project = Project.objects.get(
                    id=serializer.validated_data["project"].id, user=request.user)

                amount = serializer.validated_data["amount"]
                
                if project.budget >= amount:
                    project.budget -= amount
                    project.save()

                    expense = serializer.save()
                    
                    # Create transaction record
                    main_account = MainAccount.objects.get(user=request.user)
                    Transaction.objects.create(
                        user=request.user,
                        project=project,
                        main_account=main_account,
                        transaction_type="expense",
                        amount=amount,
                        description=f"Expense: {expense.description}"
                    )
                    
                    # Check for budget alerts
                    self._check_budget_alerts(request.user, project)
                    
                    return Response({"message": "Expense added successfully"}, status=status.HTTP_201_CREATED)
                return Response({"error": "Insufficient project budget"}, status=status.HTTP_400_BAD_REQUEST)
            except Project.DoesNotExist:
                return Response({"error": "Project not found"}, status=status.HTTP_404_NOT_FOUND)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    def _check_budget_alerts(self, user, project):
        """Check and create budget alerts if needed"""
        if project.is_budget_low():
            BudgetAlert.objects.get_or_create(
                user=user,
                project=project,
                alert_type="low_budget",
                defaults={
                    "message": f"Project '{project.name}' budget is running low (${project.budget} remaining)"
                }
            )
        
        if project.budget <= 0:
            BudgetAlert.objects.get_or_create(
                user=user,
                project=project,
                alert_type="no_funds",
                defaults={
                    "message": f"Project '{project.name}' has no remaining budget"
                }
            )


class ProjectBalanceView(APIView):
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        """Get detailed balance information for all user's projects"""
        try:
            projects = Project.objects.filter(user=request.user).prefetch_related('expenses')
            
            if not projects.exists():
                return Response({"message": "No projects found"}, status=status.HTTP_200_OK)
            
            # Import here to avoid circular import
            from .serializers import ProjectBalanceSerializer
            serializer = ProjectBalanceSerializer(projects, many=True)
            
            # Calculate summary statistics
            total_allocated = sum(project.budget for project in projects)
            total_original_budget = sum(
                project.budget + sum(expense.amount for expense in project.expenses.all()) 
                for project in projects
            )
            total_spent = total_original_budget - total_allocated
            
            response_data = {
                "projects": serializer.data,
                "summary": {
                    "total_projects": projects.count(),
                    "total_original_budget": total_original_budget,
                    "total_spent": total_spent,
                    "total_remaining": total_allocated
                }
            }
            
            return Response(response_data, status=status.HTTP_200_OK)
            
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# 🆕 NEW FEATURE VIEWS

class TransactionHistoryView(APIView):
    """🆕 Transaction History: View all transactions for audit trail"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        # Get query parameters
        transaction_type = request.query_params.get('type')
        project_id = request.query_params.get('project_id')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        limit = int(request.query_params.get('limit', 50))
        
        # Build query
        transactions = Transaction.objects.filter(user=request.user)
        
        if transaction_type:
            transactions = transactions.filter(transaction_type=transaction_type)
        if project_id:
            transactions = transactions.filter(
                Q(project_id=project_id) | Q(from_project_id=project_id) | Q(to_project_id=project_id)
            )
        if start_date:
            transactions = transactions.filter(timestamp__gte=start_date)
        if end_date:
            transactions = transactions.filter(timestamp__lte=end_date)
        
        transactions = transactions.order_by('-timestamp')[:limit]
        
        serializer = TransactionSerializer(transactions, many=True)
        
        # Calculate summary
        total_deposits = transactions.filter(transaction_type='deposit').aggregate(Sum('amount'))['amount__sum'] or 0
        total_expenses = transactions.filter(transaction_type='expense').aggregate(Sum('amount'))['amount__sum'] or 0
        total_allocations = transactions.filter(transaction_type='allocate').aggregate(Sum('amount'))['amount__sum'] or 0
        total_transfers = transactions.filter(transaction_type='transfer').aggregate(Sum('amount'))['amount__sum'] or 0
        
        return Response({
            "transactions": serializer.data,
            "summary": {
                "total_transactions": transactions.count(),
                "total_deposits": total_deposits,
                "total_expenses": total_expenses,
                "total_allocations": total_allocations,
                "total_transfers": total_transfers
            }
        })


class CategoryListCreateView(APIView):
    """🆕 Expense Categories: Manage expense categories"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        categories = Category.objects.filter(user=request.user)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)
    
    def post(self, request):
        serializer = CategorySerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class ProjectTransferView(APIView):
    """🆕 Fund Transfer Between Projects: Move funds between projects"""
    permission_classes = [IsAuthenticated]
    
    def post(self, request):
        serializer = ProjectTransferSerializer(data=request.data)
        if serializer.is_valid():
            try:
                from_project = Project.objects.get(
                    id=serializer.validated_data['from_project_id'], user=request.user)
                to_project = Project.objects.get(
                    id=serializer.validated_data['to_project_id'], user=request.user)
                
                amount = serializer.validated_data['amount']
                description = serializer.validated_data.get('description', 
                    f"Transfer from {from_project.name} to {to_project.name}")
                
                if from_project.budget >= amount:
                    # Update project budgets
                    from_project.budget -= amount
                    to_project.budget += amount
                    from_project.save()
                    to_project.save()
                    
                    # Create transaction records
                    main_account = MainAccount.objects.get(user=request.user)
                    reference_id = str(uuid.uuid4())
                    
                    Transaction.objects.create(
                        user=request.user,
                        main_account=main_account,
                        from_project=from_project,
                        to_project=to_project,
                        transaction_type="transfer",
                        amount=amount,
                        description=description,
                        reference_id=reference_id
                    )
                    
                    return Response({
                        "message": "Funds transferred successfully",
                        "from_project": from_project.name,
                        "to_project": to_project.name,
                        "amount": amount
                    }, status=status.HTTP_200_OK)
                
                return Response({"error": "Insufficient funds in source project"}, 
                              status=status.HTTP_400_BAD_REQUEST)
                
            except Project.DoesNotExist:
                return Response({"error": "One or both projects not found"}, 
                              status=status.HTTP_404_NOT_FOUND)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BudgetAlertsView(APIView):
    """🆕 Budget Monitoring: View and manage budget alerts"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        alerts = BudgetAlert.objects.filter(user=request.user)
        unread_only = request.query_params.get('unread_only', 'false').lower() == 'true'
        
        if unread_only:
            alerts = alerts.filter(is_read=False)
        
        serializer = BudgetAlertSerializer(alerts, many=True)
        
        return Response({
            "alerts": serializer.data,
            "unread_count": alerts.filter(is_read=False).count(),
            "total_count": alerts.count()
        })
    
    def patch(self, request, alert_id):
        """Mark alert as read"""
        try:
            alert = BudgetAlert.objects.get(id=alert_id, user=request.user)
            alert.is_read = True
            alert.save()
            return Response({"message": "Alert marked as read"})
        except BudgetAlert.DoesNotExist:
            return Response({"error": "Alert not found"}, status=status.HTTP_404_NOT_FOUND)


class ReportingView(APIView):
    """🆕 Reporting: Summary views of spending patterns"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        report_type = request.query_params.get('type', 'overview')
        period = request.query_params.get('period', '30')  # days
        
        end_date = timezone.now()
        start_date = end_date - timedelta(days=int(period))
        
        if report_type == 'overview':
            return self._get_overview_report(request.user, start_date, end_date)
        elif report_type == 'categories':
            return self._get_category_report(request.user, start_date, end_date)
        elif report_type == 'projects':
            return self._get_project_report(request.user, start_date, end_date)
        elif report_type == 'trends':
            return self._get_trends_report(request.user, start_date, end_date)
        else:
            return Response({"error": "Invalid report type"}, status=status.HTTP_400_BAD_REQUEST)
    
    def _get_overview_report(self, user, start_date, end_date):
        # Basic financial overview
        main_account = MainAccount.objects.get(user=user)
        projects = Project.objects.filter(user=user)
        
        total_expenses = Expense.objects.filter(
            project__user=user, created_at__range=[start_date, end_date]
        ).aggregate(Sum('amount'))['amount__sum'] or 0
        
        total_budget = sum(project.budget for project in projects)
        
        return Response({
            "period": f"{(end_date - start_date).days} days",
            "main_account_balance": main_account.balance,
            "total_project_budget": total_budget,
            "total_expenses": total_expenses,
            "projects_count": projects.count(),
            "low_budget_projects": [p.name for p in projects if p.is_budget_low()]
        })
    
    def _get_category_report(self, user, start_date, end_date):
        # Spending by category
        categories = Category.objects.filter(user=user).annotate(
            period_expenses=Sum('expenses__amount', 
                filter=Q(expenses__created_at__range=[start_date, end_date]))
        ).filter(period_expenses__gt=0).order_by('-period_expenses')
        
        return Response({
            "categories": [
                {
                    "name": cat.name,
                    "color": cat.color,
                    "amount": cat.period_expenses or 0,
                    "expense_count": cat.expenses.filter(created_at__range=[start_date, end_date]).count()
                }
                for cat in categories
            ]
        })
    
    def _get_project_report(self, user, start_date, end_date):
        # Project spending analysis
        projects = Project.objects.filter(user=user).annotate(
            period_expenses=Sum('expenses__amount',
                filter=Q(expenses__created_at__range=[start_date, end_date]))
        )
        
        return Response({
            "projects": [
                {
                    "name": project.name,
                    "current_budget": project.budget,
                    "budget_limit": project.budget_limit,
                    "period_expenses": project.period_expenses or 0,
                    "budget_status": project.budget_status(),
                    "is_budget_low": project.is_budget_low()
                }
                for project in projects
            ]
        })
    
    def _get_trends_report(self, user, start_date, end_date):
        # Daily spending trends
        daily_expenses = Expense.objects.filter(
            project__user=user, created_at__range=[start_date, end_date]
        ).extra(
            select={'day': 'date(created_at)'}
        ).values('day').annotate(
            total=Sum('amount'), count=Count('id')
        ).order_by('day')
        
        return Response({
            "daily_trends": list(daily_expenses),
            "average_daily_spending": sum(d['total'] for d in daily_expenses) / len(daily_expenses) if daily_expenses else 0
        })


class ExpenseListView(APIView):
    """Enhanced expense list with filtering and categorization"""
    permission_classes = [IsAuthenticated]
    
    def get(self, request):
        expenses = Expense.objects.filter(project__user=request.user)
        
        # Apply filters
        category_id = request.query_params.get('category')
        project_id = request.query_params.get('project')
        start_date = request.query_params.get('start_date')
        end_date = request.query_params.get('end_date')
        
        if category_id:
            expenses = expenses.filter(category_id=category_id)
        if project_id:
            expenses = expenses.filter(project_id=project_id)
        if start_date:
            expenses = expenses.filter(created_at__gte=start_date)
        if end_date:
            expenses = expenses.filter(created_at__lte=end_date)
        
        expenses = expenses.order_by('-created_at')
        serializer = ExpenseSerializer(expenses, many=True)
        
        return Response(serializer.data)
