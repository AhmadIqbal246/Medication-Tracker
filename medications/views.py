from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.http import JsonResponse
from django.utils import timezone
from django.views.generic import ListView, CreateView, UpdateView, View
from django.contrib.auth.mixins import LoginRequiredMixin
from django.utils.decorators import method_decorator
from django.views.decorators.http import require_POST
from django.urls import reverse_lazy
from django.core.paginator import Paginator
from .models import Medication
from .forms import MedicationForm
from .tasks import send_email_reminder


class MedicationListView(LoginRequiredMixin, ListView):
    model = Medication
    template_name = 'medications/medication_list.html'
    context_object_name = 'medications'
    paginate_by = 5  # Show 5 medications per page
    
    def get_queryset(self):
        return Medication.objects.filter(user=self.request.user)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        medications = self.get_queryset()
        pending_medications = medications.filter(status='pending')
        taken_medications = medications.filter(status='taken')
        
        # Calculate statistics
        now = timezone.now()
        overdue_medications = pending_medications.filter(scheduled_datetime__lt=now)
        today_medications = pending_medications.filter(
            scheduled_datetime__date=now.date()
        )
        
        # Separate pagination for pending and taken medications
        pending_paginator = Paginator(pending_medications, self.paginate_by)
        taken_paginator = Paginator(taken_medications, self.paginate_by)
        
        pending_page = self.request.GET.get('pending_page', 1)
        taken_page = self.request.GET.get('taken_page', 1)
        
        context.update({
            'pending_medications': pending_paginator.get_page(pending_page),
            'taken_medications': taken_paginator.get_page(taken_page),
            'total_medications': medications.count(),
            'pending_count': pending_medications.count(),
            'taken_count': taken_medications.count(),
            'overdue_count': overdue_medications.count(),
            'today_count': today_medications.count(),
            'current_time': now,
        })
        return context


class MedicationCreateView(LoginRequiredMixin, CreateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'medications/medication_form.html'
    success_url = reverse_lazy('medications:medication_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Add Medication'
        return context
    
    def form_valid(self, form):
        form.instance.user = self.request.user
        response = super().form_valid(form)
        
        # Schedule Celery task for email reminder
        send_email_reminder.apply_async(
            kwargs={
                'user_email': self.request.user.email,
                'medication_name': self.object.name,
                'medication_id': self.object.id,
                'scheduled_datetime': self.object.scheduled_datetime.strftime('%Y-%m-%d %H:%M'),
                'dosage': self.object.dosage
            },
            eta=self.object.scheduled_datetime
        )
        
        messages.success(self.request, f'Medication "{self.object.name}" added successfully! Reminder scheduled for {self.object.scheduled_datetime.strftime("%Y-%m-%d %H:%M")}.')
        return response


class MedicationUpdateView(LoginRequiredMixin, UpdateView):
    model = Medication
    form_class = MedicationForm
    template_name = 'medications/medication_form.html'
    success_url = reverse_lazy('medications:medication_list')
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = 'Edit Medication'
        return context
    
    def get_queryset(self):
        return Medication.objects.filter(user=self.request.user)
    
    def form_valid(self, form):
        response = super().form_valid(form)
        
        # Reschedule email reminder if datetime changed
        send_email_reminder.apply_async(
            kwargs={
                'user_email': self.request.user.email,
                'medication_name': self.object.name,
                'medication_id': self.object.id,
                'scheduled_datetime': self.object.scheduled_datetime.strftime('%Y-%m-%d %H:%M'),
                'dosage': self.object.dosage
            },
            eta=self.object.scheduled_datetime
        )
        
        messages.success(self.request, f'Medication "{self.object.name}" updated successfully!')
        return response


class MedicationMarkAsTakenView(LoginRequiredMixin, View):
    
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk, user=request.user)
        medication.status = 'taken'
        medication.save()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f'{medication.name} marked as taken!'})
        
        messages.success(request, f'{medication.name} marked as taken!')
        return redirect('medications:medication_list')


class MedicationDeleteView(LoginRequiredMixin, View):
    
    @method_decorator(require_POST)
    def dispatch(self, *args, **kwargs):
        return super().dispatch(*args, **kwargs)
    
    def post(self, request, pk):
        medication = get_object_or_404(Medication, pk=pk, user=request.user)
        medication_name = medication.name
        medication.delete()
        
        if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
            return JsonResponse({'status': 'success', 'message': f'{medication_name} deleted successfully!'})
        
        messages.success(request, f'{medication_name} deleted successfully!')
        return redirect('medications:medication_list')
