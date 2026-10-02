from django.urls import path
from . import views
app_name = 'complaints'
urlpatterns = [
    path('', views.complaint_list, name='complaint_list'),
    path('submitted/', views.submitted_complaints, name='submitted_complaints'),
    path('track/', views.track_status, name='track_status'),
    path('api/submit/', views.api_submit_complaint, name='api_submit_complaint'),
    path('api/track/<str:tracking_id>/', views.api_track_complaint, name='api_track_complaint'),
    path('feedback/', views.feedback_center, name='feedback_center'),
    path('feedback/all/', views.feedback_list, name='feedback_list'),
    path('submit/', views.submit_complaint, name='submit_complaint'),
    path('<int:pk>/', views.complaint_detail, name='complaint_detail'),
    path('<int:pk>/update/', views.update_complaint, name='update_complaint'),
    path('<int:pk>/feedback/', views.submit_feedback, name='submit_feedback'),
    path('map/', views.complaint_map, name='complaint_map'),
]
