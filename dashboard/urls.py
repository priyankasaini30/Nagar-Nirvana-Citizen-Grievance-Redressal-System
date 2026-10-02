from django.urls import path
from . import views
app_name = 'dashboard'
urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('analytics/', views.analytics, name='analytics'),
    path('citizen/', views.citizen_dashboard, name='citizen_dashboard'),
    path('authority/', views.authority_dashboard, name='authority_dashboard'),
    path('submit-complaint/', views.submit_complaint, name='submit_complaint'), 
    path('chatbot/', views.chatbot, name='chatbot'),
]
