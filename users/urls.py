# users/urls.py

from django.urls import path # type: ignore
from .views import RegisterView, LoginView, LogoutView, ProfileView, UserToHouse, ChangeProfile # type: ignore

urlpatterns = [
    path('register/', RegisterView.as_view(), name='register'),
    path('login/', LoginView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('profile/', ProfileView.as_view(), name='profile'),
    path('changeProfile/', ChangeProfile.as_view(), name='changeProfile'),
    path('addUserToHouse/<int:houseid>', UserToHouse.as_view(), name='addUserToHouse'),
]
