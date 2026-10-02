from django.urls import path
from . import views
app_name = 'accounts'
urlpatterns = [
    path('', views.home, name='home'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('register/', views.register, name='register'),
    path('register/authority/', views.register_authority, name='register_authority'),
    path('authority/requests/', views.authority_requests, name='authority_requests'),
    path('authority/requests/<int:request_id>/approve/', views.approve_authority_request, name='approve_authority_request'),
    path('authority/requests/<int:request_id>/reject/', views.reject_authority_request, name='reject_authority_request'),
    path('citizen-dashboard/', views.citizen_dashboard, name='citizen_dashboard'),
    path('authority-dashboard/', views.authority_dashboard, name='authority_dashboard'),
]
