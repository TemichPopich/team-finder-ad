import json
from http import HTTPStatus

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login, logout, update_session_auth_hash
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from .models import User, Skill
from .forms import RegisterForm, LoginForm, ProfileEditForm, CustomPasswordChangeForm

# View constants
USERS_PER_PAGE = 12
SKILLS_AUTOCOMPLETE_LIMIT = 10


def _get_paginated_queryset(queryset, per_page, request):
    """Helper function for pagination."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def register_view(request):
    """User registration view."""
    if request.user.is_authenticated:
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            return redirect('projects:project_list')
    else:
        form = RegisterForm()
    
    return render(request, 'users/register.html', {'form': form})


def login_view(request):
    """User login view."""
    if request.user.is_authenticated:
        return redirect('projects:project_list')
    
    if request.method == 'POST':
        form = LoginForm(request, data=request.POST)
        if form.is_valid():
            user = form.get_user()
            login(request, user)
            return redirect('projects:project_list')
    else:
        form = LoginForm()
    
    return render(request, 'users/login.html', {'form': form})


def logout_view(request):
    """User logout view."""
    logout(request)
    return redirect('projects:project_list')


def user_details_view(request, user_id):
    """User profile details view."""
    user = get_object_or_404(User, pk=user_id)
    return render(request, 'users/user-details.html', {'user': user})


def participants_view(request):
    """List of all users with filtering by skills (Variant 2)."""
    users = User.objects.all().order_by('-created_at')
    
    all_skills = Skill.objects.all().order_by('name')
    active_skill = request.GET.get('skill')
    
    if active_skill:
        users = users.filter(skills__name=active_skill)
    
    page_obj = _get_paginated_queryset(users, USERS_PER_PAGE, request)
    
    context = {
        'participants': page_obj,
        'all_skills': all_skills,
        'active_skill': active_skill,
    }
    return render(request, 'users/participants.html', context)


@login_required
def edit_profile_view(request):
    """Edit user profile view."""
    if request.method == 'POST':
        form = ProfileEditForm(request.POST, request.FILES, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('users:user_details', user_id=request.user.id)
    else:
        form = ProfileEditForm(instance=request.user)
    
    return render(request, 'users/edit_profile.html', {'form': form})


@login_required
def change_password_view(request):
    """Change password view."""
    if request.method == 'POST':
        form = CustomPasswordChangeForm(request.user, request.POST)
        if form.is_valid():
            user = form.save()
            update_session_auth_hash(request, user)
            messages.success(request, 'Password changed successfully')
            return redirect('users:user_details', user_id=request.user.id)
    else:
        form = CustomPasswordChangeForm(request.user)
    
    return render(request, 'users/change_password.html', {'form': form})


@login_required
@require_http_methods(["GET"])
def skills_autocomplete(request):
    """Skills autocomplete for user skills (Variant 2)."""
    query = request.GET.get('q', '')
    if query:
        skills = Skill.objects.filter(name__icontains=query).order_by('name')[:SKILLS_AUTOCOMPLETE_LIMIT]
    else:
        skills = Skill.objects.none()
    
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)


@login_required
@require_http_methods(["POST"])
def add_skill(request, user_id):
    """Add skill to user (Variant 2)."""
    if request.user.id != user_id:
        return JsonResponse({'error': 'Permission denied'}, status=HTTPStatus.FORBIDDEN)
    
    try:
        data = json.loads(request.body)
    except json.JSONDecodeError:
        return JsonResponse({'error': 'Invalid JSON'}, status=HTTPStatus.BAD_REQUEST)
    
    skill_id = data.get('skill_id')
    skill_name = data.get('name')
    
    user = get_object_or_404(User, pk=user_id)
    
    if skill_id:
        skill = get_object_or_404(Skill, pk=skill_id)
        created = False
    elif skill_name:
        skill, created = Skill.objects.get_or_create(name=skill_name)
    else:
        return JsonResponse({'error': 'skill_id or name required'}, status=HTTPStatus.BAD_REQUEST)
    
    added = False
    if not user.skills.filter(id=skill.id).exists():
        user.skills.add(skill)
        added = True
    
    return JsonResponse({
        'skill_id': skill.id,
        'name': skill.name,
        'created': created,
        'added': added,
    })


@login_required
@require_http_methods(["POST"])
def remove_skill(request, user_id, skill_id):
    """Remove skill from user (Variant 2)."""
    if request.user.id != user_id:
        return JsonResponse({'error': 'Permission denied'}, status=HTTPStatus.FORBIDDEN)
    
    user = get_object_or_404(User, pk=user_id)
    skill = get_object_or_404(Skill, pk=skill_id)
    
    if user.skills.filter(id=skill.id).exists():
        user.skills.remove(skill)
    
    return JsonResponse({'status': 'ok'})
