from django.urls import path, include
from . import views

urlpatterns = [
    path('get-room-plans/<int:house_id>/', views.get_room_plans.as_view(), name='get_room_plans'),
    path('create-plan/<int:house_id>/', views.create_plan.as_view(), name='create_plan'),
]