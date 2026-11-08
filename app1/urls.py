from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name='home'),
    path('register/', views.register, name='register'),
    path('login/', views.user_login, name='login'),
    path('logout_view/', views.logout_view, name='logout_view'),
    path('booking_page/<int:equipment_id>/', views.booking_page, name='booking_page'),
    path('initiate_reservation/<int:equipment_id>/', views.initiate_reservation, name='initiate_reservation'),
    path('user_profile/', views.user_profile, name='user_profile'),
    path('cancel_reservation/<int:pk>/', views.cancel_reservation, name='cancel_reservation'),

]