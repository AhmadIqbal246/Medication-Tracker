from django.http import JsonResponse
from django.contrib.auth.decorators import login_required
from django.views.decorators.http import require_http_methods
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.core.serializers import serialize
import json
from .models import Medication

@login_required
@require_http_methods(["GET"])
def api_medications_list(request):
    """
    API endpoint to get user's medications as JSON
    Usage: GET /medications/api/list/
    """
    medications = Medication.objects.filter(user=request.user).order_by('-scheduled_datetime')
    
    data = []
    for med in medications:
        data.append({
            'id': med.id,
            'name': med.name,
            'dosage': med.dosage,
            'scheduled_datetime': med.scheduled_datetime.isoformat(),
            'status': med.status,
            'is_overdue': med.is_overdue,
            'created_at': med.created_at.isoformat(),
        })
    
    return JsonResponse({
        'success': True,
        'medications': data,
        'count': len(data)
    })

@login_required
@require_http_methods(["GET"])
def api_medication_detail(request, pk):
    """
    API endpoint to get specific medication details
    Usage: GET /medications/api/detail/<id>/
    """
    try:
        medication = Medication.objects.get(pk=pk, user=request.user)
        
        data = {
            'id': medication.id,
            'name': medication.name,
            'dosage': medication.dosage,
            'scheduled_datetime': medication.scheduled_datetime.isoformat(),
            'status': medication.status,
            'is_overdue': medication.is_overdue,
            'created_at': medication.created_at.isoformat(),
            'updated_at': medication.updated_at.isoformat(),
        }
        
        return JsonResponse({
            'success': True,
            'medication': data
        })
        
    except Medication.DoesNotExist:
        return JsonResponse({
            'success': False,
            'error': 'Medication not found'
        }, status=404)

@login_required
@require_http_methods(["GET"])
def api_statistics(request):
    """
    API endpoint to get user's medication statistics
    Usage: GET /medications/api/statistics/
    """
    from django.utils import timezone
    
    medications = Medication.objects.filter(user=request.user)
    pending_medications = medications.filter(status='pending')
    taken_medications = medications.filter(status='taken')
    
    now = timezone.now()
    overdue_medications = pending_medications.filter(scheduled_datetime__lt=now)
    today_medications = pending_medications.filter(
        scheduled_datetime__date=now.date()
    )
    
    return JsonResponse({
        'success': True,
        'statistics': {
            'total': medications.count(),
            'pending': pending_medications.count(),
            'taken': taken_medications.count(),
            'overdue': overdue_medications.count(),
            'today': today_medications.count(),
        },
        'timestamp': now.isoformat()
    })
