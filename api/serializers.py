from .models import Project, MainAccount
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import MainAccount, Project, Expense, Category, Transaction, BudgetAlert
from django.contrib.auth import get_user_model


User = get_user_model()


class UserSignupSerializer(serializers.ModelSerializer):
    email = serializers.EmailField(required=True)  # Ensure email is required
    username = serializers.CharField(
        required=True)  # Ensure username is required
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ["id", "username", "email", "password"]

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username is already taken.")
        return value

    def validate_email(self, value):
        if User.objects.filter(email=value).exists():
            raise serializers.ValidationError("Email is already registered.")
        return value

    def create(self, validated_data):
        validated_data["password"] = make_password(validated_data["password"])
        user = User.objects.create(**validated_data)

        # Automatically create a MainAccount for the new user
        MainAccount.objects.create(user=user)
        
        # Create default expense categories
        default_categories = [
            {"name": "Food & Dining", "color": "#e74c3c"},
            {"name": "Transportation", "color": "#3498db"},
            {"name": "Shopping", "color": "#9b59b6"},
            {"name": "Entertainment", "color": "#f39c12"},
            {"name": "Bills & Utilities", "color": "#e67e22"},
            {"name": "Healthcare", "color": "#1abc9c"},
            {"name": "Other", "color": "#95a5a6"},
        ]
        
        for cat_data in default_categories:
            Category.objects.create(
                user=user,
                name=cat_data["name"],
                color=cat_data["color"],
                type="expense"
            )

        return user


class CategorySerializer(serializers.ModelSerializer):
    expense_count = serializers.SerializerMethodField()
    total_amount = serializers.SerializerMethodField()
    
    class Meta:
        model = Category
        fields = ["id", "name", "type", "color", "description", "expense_count", "total_amount", "created_at"]
    
    def get_expense_count(self, obj):
        return obj.expenses.count()
    
    def get_total_amount(self, obj):
        return sum(expense.amount for expense in obj.expenses.all())


class ProjectSerializer(serializers.ModelSerializer):
    budget_status = serializers.SerializerMethodField()
    is_budget_low = serializers.SerializerMethodField()
    total_expenses = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = '__all__'
    
    def get_budget_status(self, obj):
        return obj.budget_status()
    
    def get_is_budget_low(self, obj):
        return obj.is_budget_low()
    
    def get_total_expenses(self, obj):
        return sum(expense.amount for expense in obj.expenses.all())


class TransactionSerializer(serializers.ModelSerializer):
    from_project_name = serializers.SerializerMethodField()
    to_project_name = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Transaction
        fields = ["id", "transaction_type", "amount", "description", "reference_id", 
                 "project", "project_name", "from_project", "from_project_name", 
                 "to_project", "to_project_name", "timestamp"]
    
    def get_from_project_name(self, obj):
        return obj.from_project.name if obj.from_project else None
    
    def get_to_project_name(self, obj):
        return obj.to_project.name if obj.to_project else None
    
    def get_project_name(self, obj):
        return obj.project.name if obj.project else None


class BudgetAlertSerializer(serializers.ModelSerializer):
    project_name = serializers.SerializerMethodField()
    
    class Meta:
        model = BudgetAlert
        fields = ["id", "alert_type", "message", "is_read", "project", "project_name", "created_at"]
    
    def get_project_name(self, obj):
        return obj.project.name


class ProjectTransferSerializer(serializers.Serializer):
    from_project_id = serializers.UUIDField()
    to_project_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)
    description = serializers.CharField(max_length=500, required=False)
    
    def validate(self, data):
        if data['from_project_id'] == data['to_project_id']:
            raise serializers.ValidationError("Cannot transfer funds to the same project.")
        return data


class FundAllocationSerializer(serializers.Serializer):
    project_id = serializers.UUIDField()
    amount = serializers.DecimalField(max_digits=15, decimal_places=2)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password']
        extra_kwargs = {'password': {'write_only': True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class MainAccountSerializer(serializers.ModelSerializer):
    class Meta:
        model = MainAccount
        fields = '__all__'


class ExpenseSerializer(serializers.ModelSerializer):
    category_name = serializers.SerializerMethodField()
    category_color = serializers.SerializerMethodField()
    tags_list = serializers.SerializerMethodField()
    project_name = serializers.SerializerMethodField()
    
    class Meta:
        model = Expense
        fields = ["id", "project", "project_name", "category", "category_name", "category_color", 
                 "amount", "description", "receipt_url", "tags", "tags_list", "created_at", "updated_at"]
    
    def get_category_name(self, obj):
        return obj.category.name if obj.category else None
    
    def get_category_color(self, obj):
        return obj.category.color if obj.category else "#95a5a6"
    
    def get_tags_list(self, obj):
        return obj.get_tags_list()
    
    def get_project_name(self, obj):
        return obj.project.name


class ProjectBalanceSerializer(serializers.ModelSerializer):
    total_expenses = serializers.SerializerMethodField()
    remaining_budget = serializers.SerializerMethodField()
    expense_count = serializers.SerializerMethodField()
    latest_expenses = serializers.SerializerMethodField()
    budget_status = serializers.SerializerMethodField()
    is_budget_low = serializers.SerializerMethodField()
    alerts_count = serializers.SerializerMethodField()
    
    class Meta:
        model = Project
        fields = ["id", "name", "budget", "budget_limit", "low_budget_threshold", "total_expenses", 
                 "remaining_budget", "expense_count", "latest_expenses", "budget_status", 
                 "is_budget_low", "alerts_count", "created_at"]
    
    def get_total_expenses(self, obj):
        """Calculate total expenses for this project"""
        total = sum(expense.amount for expense in obj.expenses.all())
        return total
    
    def get_remaining_budget(self, obj):
        """Calculate remaining budget (current budget field already accounts for expenses)"""
        return obj.budget
    
    def get_expense_count(self, obj):
        """Get total number of expenses for this project"""
        return obj.expenses.count()
    
    def get_latest_expenses(self, obj):
        """Get latest 3 expenses for this project"""
        latest_expenses = obj.expenses.order_by('-created_at')[:3]
        return ExpenseSerializer(latest_expenses, many=True).data
    
    def get_budget_status(self, obj):
        return obj.budget_status()
    
    def get_is_budget_low(self, obj):
        return obj.is_budget_low()
    
    def get_alerts_count(self, obj):
        return obj.alerts.filter(is_read=False).count()
