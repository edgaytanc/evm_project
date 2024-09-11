# core/urls.py

# core/urls.py

from django.urls import path
from django.contrib.auth.views import LoginView
from . import views

urlpatterns = [
    path('dashboard/', views.dashboard, name='dashboard'),
    path('', LoginView.as_view(template_name='core/login.html'), name='login'),
    path('project_list/', views.project_list, name='project_list'),  # Protegido para usuarios autenticados
    path('project/create/', views.project_create, name='project_create'),  # Ruta para crear proyecto
    path('project/edit/<int:pk>/', views.project_edit, name='project_edit'),  # Ruta para editar proyecto
    path('project/<int:pk>/', views.project_detail, name='project_detail'),  # Ruta para ver detalles del proyecto
    path('project/performance_chart/<int:pk>/', views.project_performance_chart, name='project_performance_chart'),  # Nueva ruta para el gráfico
    path('project/<int:pk>/export_pdf/', views.export_project_pdf, name='export_project_pdf'),
    path('project/<int:pk>/export_csv/', views.export_project_csv, name='export_project_csv'),
    path('projects/export_all_csv/', views.export_all_projects_csv, name='export_all_projects_csv'),
    path('project/<int:pk>/delete/', views.project_delete, name='project_delete'),
]
