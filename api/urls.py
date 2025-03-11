from django.urls import path
from .views import UserMainAccountView, UserSignupView, UserLoginView, ProjectListCreateView, ProjectDetailView, AllocateFundsView
from .views import UserCreateView, AddExpenseView
from api.views import AddFundsView

urlpatterns = [
    path('signup/', UserSignupView.as_view(), name='signup'),
    path('users/', UserCreateView.as_view(), name='user-create'),
    path('login/', UserLoginView.as_view(), name='login'),
    path('projects/', ProjectListCreateView.as_view(), name='project-list'),
    path('projects/<uuid:pk>/', ProjectDetailView.as_view(), name='project-detail'),
    path('allocate-funds/', AllocateFundsView.as_view(), name='allocate-funds'),
    path('add-funds/', AddFundsView.as_view(), name='add-funds'),
    path('my-main-account/', UserMainAccountView.as_view(), name='my-main-account'),
    path("add-expense/", AddExpenseView.as_view(), name="add-expense"),

]
