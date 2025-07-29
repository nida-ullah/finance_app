import uuid
from django.db import models
from django.contrib.auth.models import AbstractUser
from django.contrib.auth import get_user_model


# class User(AbstractUser):
#     id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)

class User(AbstractUser):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)

    def __str__(self):
        return str(self.username)


class Category(models.Model):
    CATEGORY_TYPES = [
        ("expense", "Expense"),
        ("income", "Income"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="categories")
    name = models.CharField(max_length=100)
    type = models.CharField(max_length=10, choices=CATEGORY_TYPES, default="expense")
    color = models.CharField(max_length=7, default="#3498db")  # Hex color code
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        verbose_name_plural = "Categories"
        unique_together = ['user', 'name']  # Prevent duplicate category names per user
    
    def __str__(self):
        return f"{self.user.username} - {self.name}"


class MainAccount(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, related_name="main_account")
    balance = models.DecimalField(
        max_digits=12, decimal_places=2, default=0.00)

    objects = models.Manager()  # Explicitly define the manager

    def __str__(self):
        return f"{self.user.username}'s Main Account"  # pylint: disable=no-member


class Project(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="projects")
    name = models.CharField(max_length=255)
    budget = models.DecimalField(max_digits=15, decimal_places=2, default=0.00)
    budget_limit = models.DecimalField(max_digits=15, decimal_places=2, null=True, blank=True)
    low_budget_threshold = models.DecimalField(max_digits=15, decimal_places=2, default=50.00)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    def is_budget_low(self):
        """Check if project budget is below the low threshold"""
        return self.budget <= self.low_budget_threshold
    
    def budget_status(self):
        """Get budget status with percentage remaining"""
        if self.budget_limit:
            percentage = (self.budget / self.budget_limit) * 100
            if percentage <= 10:
                return "critical"
            elif percentage <= 25:
                return "low"
            elif percentage <= 50:
                return "medium"
            else:
                return "good"
        return "unlimited"
    
    def __str__(self):
        return f"{self.name} - {self.user.username}"


class Transaction(models.Model):
    TRANSACTION_TYPES = [
        ("deposit", "Deposit"),
        ("allocate", "Allocate to Project"),
        ("expense", "Expense"),
        ("transfer", "Transfer Between Projects"),
        ("refund", "Refund"),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        User, on_delete=models.CASCADE, related_name="transactions")
    project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="transactions")
    main_account = models.ForeignKey(
        MainAccount, on_delete=models.CASCADE, related_name="transactions")
    
    # For project transfers
    from_project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_out")
    to_project = models.ForeignKey(
        Project, on_delete=models.SET_NULL, null=True, blank=True, related_name="transfers_in")
    
    transaction_type = models.CharField(
        max_length=10, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(max_digits=12, decimal_places=2)
    description = models.TextField(blank=True)
    reference_id = models.CharField(max_length=100, blank=True)  # For tracking related transactions
    timestamp = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.transaction_type} - {self.amount} - {self.timestamp.strftime('%Y-%m-%d')}"


class Expense(models.Model):
    id = models.UUIDField(default=uuid.uuid4, primary_key=True, editable=False)
    project = models.ForeignKey(
        "Project", on_delete=models.CASCADE, related_name="expenses")
    category = models.ForeignKey(
        Category, on_delete=models.SET_NULL, null=True, blank=True, related_name="expenses")
    amount = models.DecimalField(max_digits=10, decimal_places=2)
    description = models.TextField()
    receipt_url = models.URLField(blank=True)  # For receipt storage
    tags = models.CharField(max_length=255, blank=True)  # Comma-separated tags
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"{self.amount} - {self.description}"
    
    def get_tags_list(self):
        """Return tags as a list"""
        return [tag.strip() for tag in self.tags.split(',') if tag.strip()]


class BudgetAlert(models.Model):
    ALERT_TYPES = [
        ("low_budget", "Low Budget"),
        ("budget_exceeded", "Budget Exceeded"),
        ("no_funds", "No Funds"),
        ("large_expense", "Large Expense"),
    ]
    
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name="budget_alerts")
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name="alerts")
    alert_type = models.CharField(max_length=20, choices=ALERT_TYPES)
    message = models.TextField()
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.alert_type} - {self.project.name}"
