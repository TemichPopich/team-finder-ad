from django.urls import path

from . import views

app_name = 'users'

urlpatterns = [
    path('register/', views.register_view, name='register'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('<int:user_id>/', views.user_details_view, name='user_details'),
    path('list/', views.participants_view, name='participants'),
    path('edit-profile/', views.edit_profile_view, name='edit_profile'),
    path('change-password/', views.change_password_view, name='change_password'),
    path('skills/', views.skills_autocomplete, name='skills_autocomplete'),
    path('<int:user_id>/skills/add/', views.add_skill, name='add_skill'),
    path('<int:user_id>/skills/<int:skill_id>/remove/', views.remove_skill, name='remove_skill'),
]
