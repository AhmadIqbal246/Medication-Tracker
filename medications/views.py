from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_POST
from .models import Medication
from .forms import MedicationForm
from .tasks import send_email_reminder
from django.utils import timezone

@login_required
def medication_list(request):
    medications = Medication.objects.filter(user=request.user)
    pending_medications = medications.filter(status='pending')
    taken_medications = medications.filter(status='taken')
    
    # Calculate statistics
    from django.utils import timezone
    now = timezone.now()
    overdue_medications = pending_medications.filter(scheduled_datetime__lt=now)
    today_medications = pending_medications.filter(
        scheduled_datetime__date=now.date()
    )
    
    context = {
        'pending_medications': pending_medications,
        'taken_medications': taken_medications,
        'total_medications': medications.count(),
        'pending_count': pending_medications.count(),
        'taken_count': taken_medications.count(),
        'overdue_count': overdue_medications.count(),
        'today_count': today_medications.count(),
        'current_time': now,
    }
    return render(request, 'medications/medication_list.html', context)

@login_required
def add_medication(request):
    if request.method == 'POST':
        form = MedicationForm(request.POST)
        if form.is_valid():
            medication = form.save(commit=False)
            medication.user = request.user
            medication.save()
            
            # Schedule Celery task for email reminder
            send_email_reminder.apply_async(
                kwargs={
                    'user_email': request.user.email,
                    'medication_name': medication.name,
                    'medication_id': medication.id,
                    'scheduled_datetime': medication.scheduled_datetime.strftime('%Y-%m-%d %H:%M'),
                    'dosage': medication.dosage
                },
                eta=medication.scheduled_datetime
            )
            
            messages.success(request, f'Medication "{medication.name}" added successfully! Reminder scheduled for {medication.scheduled_datetime.strftime("%Y-%m-%d %H:%M")}.')
            return redirect('medications:medication_list')
    else:
        form = MedicationForm()
    
    return render(request, 'medications/medication_form.html', {'form': form, 'title': 'Add Medication'})

@login_required
def edit_medication(request, pk):
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    
    if request.method == 'POST':
        form = MedicationForm(request.POST, instance=medication)
        if form.is_valid():
            updated_medication = form.save()
            
            # Reschedule email reminder if datetime changed
            send_email_reminder.apply_async(
                kwargs={
                    'user_email': request.user.email,
                    'medication_name': updated_medication.name,
                    'medication_id': updated_medication.id,
                    'scheduled_datetime': updated_medication.scheduled_datetime.strftime('%Y-%m-%d %H:%M'),
                    'dosage': updated_medication.dosage
                },
                eta=updated_medication.scheduled_datetime
            )
            
            messages.success(request, f'Medication "{updated_medication.name}" updated successfully!')
            return redirect('medications:medication_list')
    else:
        form = MedicationForm(instance=medication)
    
    return render(request, 'medications/medication_form.html', {'form': form, 'title': 'Edit Medication'})

@login_required
@require_POST
def mark_as_taken(request, pk):
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    medication.status = 'taken'
    medication.save()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': f'{medication.name} marked as taken!'})
    
    messages.success(request, f'{medication.name} marked as taken!')
    return redirect('medications:medication_list')

@login_required
@require_POST
def delete_medication(request, pk):
    medication = get_object_or_404(Medication, pk=pk, user=request.user)
    medication_name = medication.name
    medication.delete()
    
    if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
        return JsonResponse({'status': 'success', 'message': f'{medication_name} deleted successfully!'})
    
    messages.success(request, f'{medication_name} deleted successfully!')
    return redirect('medications:medication_list')
