from django.urls import path

from . import views

app_name = 'projects'

urlpatterns = [
    path('list/', views.project_list_view, name='project_list'),
    path('<int:project_id>/', views.project_details_view, name='project_details'),
    path('create-project/', views.create_project_view, name='create_project'),
    path('<int:project_id>/edit/', views.edit_project_view, name='edit_project'),
    path('<int:project_id>/complete/', views.complete_project_view, name='complete_project'),
    path('<int:project_id>/toggle-participate/', views.toggle_participate_view, name='toggle_participate'),
    path('favorites/', views.favorite_projects_view, name='favorite_projects'),
    path('skills/', views.skills_autocomplete, name='skills_autocomplete'),
]
