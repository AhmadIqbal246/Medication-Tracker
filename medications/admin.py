from django.contrib import admin
from .models import Medication

@admin.register(Medication)
class MedicationAdmin(admin.ModelAdmin):
    list_display = ['name', 'user', 'scheduled_datetime', 'status', 'created_at']
    list_filter = ['status', 'created_at', 'scheduled_datetime']
    search_fields = ['name', 'user__username']
    ordering = ['-scheduled_datetime']
