from .models import Project, MainAccount
from django.contrib.auth.models import User
from rest_framework import serializers
from django.contrib.auth.hashers import make_password
from .models import MainAccount, Project, Expense
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

        return user


class ProjectSerializer(serializers.ModelSerializer):
    class Meta:
        model = Project
        fields = '__all__'


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
    class Meta:
        model = Expense
        fields = ["id", "project", "amount", "description", "created_at"]


# from django.contrib.auth import get_user_model
# from rest_framework import serializers
# from django.contrib.auth.hashers import make_password
# from .models import MainAccount
# from django.contrib.auth.models import User


# User = get_user_model()


# class UserSignupSerializer(serializers.ModelSerializer):
#     password = serializers.CharField(write_only=True)

#     class Meta:
#         model = User
#         fields = ["id", "username", "password"]

#     def create(self, validated_data):
#         validated_data["password"] = make_password(validated_data["password"])
#         user = User.objects.create(**validated_data)

#         # Automatically create a MainAccount for the new user
#         MainAccount.objects.create(user=user)
#         return user
