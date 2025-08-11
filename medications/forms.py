from django import forms
from .models import Medication
from django.utils import timezone

class MedicationForm(forms.ModelForm):
    scheduled_datetime = forms.DateTimeField(
        widget=forms.DateTimeInput(
            attrs={
                'type': 'datetime-local',
                'class': 'form-control'
            }
        ),
        help_text='Select the date and time for your medication reminder'
    )
    
    class Meta:
        model = Medication
        fields = ['name', 'dosage', 'scheduled_datetime']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Enter medication name'}),
            'dosage': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Enter dosage information (e.g., 2 tablets, 500mg)'}),
        }
    
    def clean_scheduled_datetime(self):
        scheduled_datetime = self.cleaned_data['scheduled_datetime']
        
        # Ensure the datetime is timezone-aware
        if timezone.is_naive(scheduled_datetime):
            # Convert naive datetime to timezone-aware using current timezone
            scheduled_datetime = timezone.make_aware(scheduled_datetime, timezone.get_current_timezone())
        
        if scheduled_datetime <= timezone.now():
            raise forms.ValidationError("Scheduled time must be in the future.")
        
        return scheduled_datetime
