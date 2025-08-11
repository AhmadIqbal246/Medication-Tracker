from django.urls import path
from . import views, api_views

app_name = 'medications'

urlpatterns = [
    # Web views
    path('', views.medication_list, name='medication_list'),
    path('add/', views.add_medication, name='add_medication'),
    path('<int:pk>/edit/', views.edit_medication, name='edit_medication'),
    path('<int:pk>/mark-taken/', views.mark_as_taken, name='mark_as_taken'),
    path('<int:pk>/delete/', views.delete_medication, name='delete_medication'),
    
    # API endpoints (for future mobile app integration)
    path('api/list/', api_views.api_medications_list, name='api_medications_list'),
    path('api/detail/<int:pk>/', api_views.api_medication_detail, name='api_medication_detail'),
    path('api/statistics/', api_views.api_statistics, name='api_statistics'),
]
