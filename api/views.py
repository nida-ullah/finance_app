
from .models import MainAccount
from rest_framework import status
from django.contrib.auth import get_user_model
from rest_framework import permissions, status, generics
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework_simplejwt.tokens import RefreshToken
from django.contrib.auth.models import User
from .serializers import UserSignupSerializer, ProjectSerializer, FundAllocationSerializer, UserSerializer, MainAccountSerializer, ExpenseSerializer
from .models import Project, MainAccount, Expense
from django.core.exceptions import ObjectDoesNotExist
from django.http import JsonResponse
from django.views import View
from decimal import Decimal
from rest_framework.permissions import IsAuthenticated


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
    def post(self, request):
        serializer = FundAllocationSerializer(data=request.data)
        if serializer.is_valid():
            project = Project.objects.get(
                id=serializer.validated_data['project_id'])
            main_account = MainAccount.objects.get(user=request.user)

            if main_account.balance >= serializer.validated_data['amount']:
                main_account.balance -= serializer.validated_data['amount']
                project.budget += serializer.validated_data['amount']
                main_account.save()
                project.save()
                return Response({"message": "Funds allocated successfully"}, status=status.HTTP_200_OK)
            return Response({"error": "Insufficient funds"}, status=status.HTTP_400_BAD_REQUEST)
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
        main_account_id = request.data.get("main_account")
        amount = request.data.get("amount")
        try:
            main_account = MainAccount.objects.get(user=request.user)
            main_account.balance += Decimal(str(amount))
            main_account.save()
            return Response({"message": "Funds added successfully!", "balance": main_account.balance}, status=status.HTTP_200_OK)
        except MainAccount.DoesNotExist:
            return Response({"error": "Main account not found!"}, status=status.HTTP_404_NOT_FOUND)


class AddExpenseView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = ExpenseSerializer(data=request.data)
        if serializer.is_valid():
            project = Project.objects.get(
                id=serializer.validated_data["project"].id)

            if project.budget >= serializer.validated_data["amount"]:
                project.budget -= serializer.validated_data["amount"]
                project.save()

                serializer.save()
                return Response({"message": "Expense added successfully"}, status=status.HTTP_201_CREATED)
            return Response({"error": "Insufficient project budget"}, status=status.HTTP_400_BAD_REQUEST)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


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
