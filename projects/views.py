from http import HTTPStatus

from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from django.http import JsonResponse
from django.views.decorators.http import require_http_methods
from django.core.paginator import Paginator

from .models import Project
from .forms import ProjectForm
from users.models import Skill

# View constants
PROJECTS_PER_PAGE = 12
SKILLS_AUTOCOMPLETE_LIMIT = 10
PROJECT_STATUS_OPEN = 'open'
PROJECT_STATUS_CLOSED = 'closed'


def _get_paginated_queryset(queryset, per_page, request):
    """Helper function for pagination."""
    paginator = Paginator(queryset, per_page)
    page_number = request.GET.get('page')
    return paginator.get_page(page_number)


def project_list_view(request):
    """List of all projects with pagination."""
    projects = Project.objects.select_related('owner').filter(status=PROJECT_STATUS_OPEN).order_by('-created_at')
    page_obj = _get_paginated_queryset(projects, PROJECTS_PER_PAGE, request)
    
    return render(request, 'projects/project_list.html', {'projects': page_obj})


def project_details_view(request, project_id):
    """Project details view."""
    project = get_object_or_404(Project, pk=project_id)
    return render(request, 'projects/project-details.html', {'project': project})


@login_required
def create_project_view(request):
    """Create new project view."""
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            project = form.save(commit=False)
            project.owner = request.user
            project.save()
            return redirect('projects:project_details', project_id=project.id)
    else:
        form = ProjectForm()
    
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': False})


@login_required
def edit_project_view(request, project_id):
    """Edit project view."""
    project = get_object_or_404(Project, pk=project_id)
    
    if request.user != project.owner:
        return redirect('projects:project_details', project_id=project_id)
    
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('projects:project_details', project_id=project.id)
    else:
        form = ProjectForm(instance=project)
    
    return render(request, 'projects/create-project.html', {'form': form, 'is_edit': True})


@login_required
@require_http_methods(["POST"])
def complete_project_view(request, project_id):
    """Complete/close project view."""
    project = get_object_or_404(Project, pk=project_id)
    
    if request.user != project.owner:
        return JsonResponse({'status': 'error', 'message': 'Permission denied'}, status=HTTPStatus.FORBIDDEN)
    
    if project.status == PROJECT_STATUS_OPEN:
        project.status = PROJECT_STATUS_CLOSED
        project.save()
        return JsonResponse({'status': 'ok', 'project_status': PROJECT_STATUS_CLOSED})
    
    return JsonResponse({'status': 'error', 'message': 'Project already closed'}, status=HTTPStatus.BAD_REQUEST)


@login_required
@require_http_methods(["POST"])
def toggle_participate_view(request, project_id):
    """Toggle user participation in project."""
    project = get_object_or_404(Project, pk=project_id)
    user = request.user
    
    if project.participants.filter(id=user.id).exists():
        if user == project.owner:
            return JsonResponse({'status': 'error', 'message': 'Owner cannot leave project'}, status=HTTPStatus.BAD_REQUEST)
        project.participants.remove(user)
        return JsonResponse({'status': 'ok', 'participant': False})
    else:
        project.participants.add(user)
        return JsonResponse({'status': 'ok', 'participant': True})


@login_required
def favorite_projects_view(request):
    """List of user's favorite projects."""
    projects = request.user.participated_projects.all().order_by('-created_at')
    return render(request, 'projects/favorite_projects.html', {'projects': projects})


@login_required
@require_http_methods(["GET"])
def skills_autocomplete(request):
    """Skills autocomplete for filtering (Variant 2 - user skills)."""
    query = request.GET.get('q', '')
    if query:
        skills = Skill.objects.filter(name__icontains=query).order_by('name')[:SKILLS_AUTOCOMPLETE_LIMIT]
    else:
        skills = Skill.objects.none()
    
    data = [{'id': skill.id, 'name': skill.name} for skill in skills]
    return JsonResponse(data, safe=False)
