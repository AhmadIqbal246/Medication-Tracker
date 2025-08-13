from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, authenticate
from django.contrib.auth.views import LogoutView
from django.contrib.auth.models import User
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.contrib.auth.mixins import LoginRequiredMixin
from django.views.generic import UpdateView
from django.urls import reverse_lazy
from .forms import SignUpForm, CustomLoginForm, UserUpdateForm, UserProfileForm
from .models import UserProfile
import json


def custom_login_view(request):
    if request.user.is_authenticated:
        return redirect('medications:medication_list')
        
    if request.method == 'POST':
        form = CustomLoginForm(request.POST)
        if form.is_valid():
            email = form.cleaned_data['email']
            password = form.cleaned_data['password']
            
            try:
                # Handle multiple users with same email - get the first one that matches password
                users = User.objects.filter(email=email)
                authenticated_user = None
                
                for user in users:
                    if user.check_password(password):
                        authenticated_user = user
                        break
                
                if authenticated_user:
                    login(request, authenticated_user)
                    messages.success(request, 'Successfully logged in!')
                    return redirect('medications:medication_list')
                else:
                    messages.error(request, 'Invalid email or password.')
                    
            except User.DoesNotExist:
                messages.error(request, 'Invalid email or password.')
    else:
        form = CustomLoginForm()
    
    return render(request, 'accounts/login.html', {'form': form})


def signup_view(request):
    if request.method == 'POST':
        form = SignUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Account created successfully!')
            return redirect('medications:medication_list')
    else:
        form = SignUpForm()
    return render(request, 'accounts/signup.html', {'form': form})


class CustomLogoutView(LogoutView):
    next_page = '/accounts/login/'


@login_required
def profile_view(request):
    """Display user profile"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    # Get medication statistics
    from medications.models import Medication
    user_medications = Medication.objects.filter(user=request.user)
    
    context = {
        'user': request.user,
        'profile': profile,
        'total_medications': user_medications.count(),
        'pending_medications_count': user_medications.filter(status='pending').count(),
        'taken_medications_count': user_medications.filter(status='taken').count(),
    }
    return render(request, 'accounts/profile.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile with forms"""
    profile, created = UserProfile.objects.get_or_create(user=request.user)
    
    if request.method == 'POST':
        user_form = UserUpdateForm(request.POST, instance=request.user)
        profile_form = UserProfileForm(request.POST, instance=profile)
        
        if user_form.is_valid() and profile_form.is_valid():
            user_form.save()
            profile_form.save()
            messages.success(request, 'Your profile has been updated successfully!')
            return redirect('accounts:profile')
    else:
        user_form = UserUpdateForm(instance=request.user)
        profile_form = UserProfileForm(instance=profile)
    
    context = {
        'user_form': user_form,
        'profile_form': profile_form,
    }
    return render(request, 'accounts/edit_profile.html', context)


@login_required
@require_http_methods(["PATCH", "PUT"])
def patch_profile_api(request):
    """API endpoint to update specific profile fields using PATCH method"""
    try:
        profile, created = UserProfile.objects.get_or_create(user=request.user)
        data = json.loads(request.body)
        
        # Update User fields
        user_fields = ['username', 'email', 'first_name', 'last_name']
        for field in user_fields:
            if field in data:
                setattr(request.user, field, data[field])
        
        # Update Profile fields
        profile_fields = ['bio', 'gender', 'age', 'phone_number']
        for field in profile_fields:
            if field in data:
                setattr(profile, field, data[field])
        
        # Save changes
        request.user.save()
        profile.save()
        
        return JsonResponse({
            'status': 'success',
            'message': 'Profile updated successfully',
            'data': {
                'username': request.user.username,
                'email': request.user.email,
                'first_name': request.user.first_name,
                'last_name': request.user.last_name,
                'bio': profile.bio,
                'gender': profile.get_gender_display(),
                'age': profile.age,
                'phone_number': profile.phone_number,
            }
        })
    
    except json.JSONDecodeError:
        return JsonResponse({'status': 'error', 'message': 'Invalid JSON data'}, status=400)
    except Exception as e:
        return JsonResponse({'status': 'error', 'message': str(e)}, status=500)
