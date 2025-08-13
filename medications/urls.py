from django.urls import path
from . import views, api_views

app_name = 'medications'

urlpatterns = [
    # Web views (Class-based)
    path('', views.MedicationListView.as_view(), name='medication_list'),
    path('add/', views.MedicationCreateView.as_view(), name='add_medication'),
    path('<int:pk>/edit/', views.MedicationUpdateView.as_view(), name='edit_medication'),
    path('<int:pk>/mark-taken/', views.MedicationMarkAsTakenView.as_view(), name='mark_as_taken'),
    path('<int:pk>/delete/', views.MedicationDeleteView.as_view(), name='delete_medication'),
    
    # API endpoints (for future mobile app integration)
    path('api/list/', api_views.api_medications_list, name='api_medications_list'),
    path('api/detail/<int:pk>/', api_views.api_medication_detail, name='api_medication_detail'),
    path('api/statistics/', api_views.api_statistics, name='api_statistics'),
]
