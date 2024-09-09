import matplotlib.pyplot as plt
import pandas as pd
import io
import urllib, base64
from django.http import HttpResponse
# from django.contrib.auth.views import LoginView, LogoutView
from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.decorators import login_required
from .models import Project
from django.db.models import Avg
from .forms import ProjectForm
from decimal import Decimal
import tempfile  # Asegúrate de importar tempfile
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas  # Aquí está la importación que faltaba
import os

# Vista para crear un proyecto
@login_required
def project_create(request):
    if request.method == 'POST':
        form = ProjectForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm()
    return render(request, 'core/project_form.html', {'form': form})

# Nueva vista para editar un proyecto
@login_required
def project_edit(request, pk):
    project = get_object_or_404(Project, pk=pk)
    if request.method == 'POST':
        form = ProjectForm(request.POST, instance=project)
        if form.is_valid():
            form.save()
            return redirect('project_list')
    else:
        form = ProjectForm(instance=project)
    return render(request, 'core/project_form.html', {'form': form, 'project': project})

# Vista para listar y ver los proyectos
@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'core/project_list.html', {'projects': projects})

# Nueva vista para ver detalles de un proyecto
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)
    return render(request, 'core/project_detail.html', {'project': project})




# Vista para el Dashboard
@login_required
def dashboard(request):
    # Calcular métricas globales (promedios de CPI y SPI)
    total_projects = Project.objects.count()

    if total_projects > 0:
        avg_cpi = float(Project.objects.aggregate(Avg('earned_value'))['earned_value__avg']) / float(Project.objects.aggregate(Avg('actual_cost'))['actual_cost__avg'])
        avg_spi = float(Project.objects.aggregate(Avg('earned_value'))['earned_value__avg']) / float(Project.objects.aggregate(Avg('planned_cost'))['planned_cost__avg'])
    else:
        avg_cpi = None
        avg_spi = None

    # Simulación de datos semanales de rendimiento global
    weeks = list(range(1, 25))  # 24 semanas
    avg_planned_costs = [float(sum(project.planned_cost for project in Project.objects.all())) * (week / 24) for week in weeks]
    avg_earned_values = [float(sum(project.earned_value for project in Project.objects.all())) * (week / 24) for week in weeks]

    # Crear gráfico de rendimiento general de proyectos
    plt.figure(figsize=(10, 6))
    plt.plot(weeks, avg_planned_costs, label="Average Planned Cost (PV)", color='blue', marker='o')
    plt.plot(weeks, avg_earned_values, label="Average Earned Value (EV)", color='green', marker='o')
    plt.xlabel('Weeks')
    plt.ylabel('Cost / Value')
    plt.title('General Project Performance')
    plt.legend()

    # Guardar gráfico en memoria
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    chart_uri = urllib.parse.quote(string)

    context = {
        'project_summary': {
            'total_projects': total_projects,
            'avg_cpi': avg_cpi,
            'avg_spi': avg_spi,
            'chart_uri': chart_uri  # Gráfico del rendimiento general
        }
    }
    return render(request, 'core/dashboard.html', context)


# Vista para generar el gráfico dinámico con Matplotlib
@login_required
def project_performance_chart(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Convertir los valores a float para realizar cálculos
    planned_cost = float(project.planned_cost)
    earned_value = float(project.earned_value)

    # Simulación de datos semanales de costo planificado (PV) y valor ganado (EV)
    weeks = list(range(1, 25))  # 24 semanas
    planned_costs = [planned_cost * (week / 24) for week in weeks]  # Simular evolución PV
    earned_values = [earned_value * (week / 24) for week in weeks]  # Simular evolución EV

    # Crear el gráfico con Matplotlib
    plt.figure(figsize=(10, 6))
    plt.plot(weeks, planned_costs, label="Planned Cost (PV)", color='blue', marker='o')
    plt.plot(weeks, earned_values, label="Earned Value (EV)", color='green', marker='o')
    plt.xlabel('Weeks')
    plt.ylabel('Cost / Value')
    plt.title(f'Project Performance - {project.name}')
    plt.legend()

    # Guardar el gráfico en memoria para enviarlo como respuesta HTTP
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    string = base64.b64encode(buf.read())
    uri = urllib.parse.quote(string)

    return render(request, 'core/project_chart.html', {'chart_uri': uri, 'project': project})


# Vista para exportar el informe a PDF
@login_required
def export_project_pdf(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Configurar el PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_EVM_Report.pdf"'

    # Crear un objeto canvas de ReportLab
    p = canvas.Canvas(response, pagesize=A4)
    width, height = A4

    # Título
    p.setFont("Helvetica-Bold", 16)
    p.drawString(100, height - 50, f"Informe de EVM - Proyecto: {project.name}")

    # Información del proyecto
    p.setFont("Helvetica", 12)
    p.drawString(100, height - 100, f"Costo Planificado (PV): {project.planned_cost}")
    p.drawString(100, height - 120, f"Costo Real (AC): {project.actual_cost}")
    p.drawString(100, height - 140, f"Valor Ganado (EV): {project.earned_value}")
    p.drawString(100, height - 160, f"CPI (Cost Performance Index): {project.cost_performance_index:.2f}" if project.cost_performance_index else "No disponible")
    p.drawString(100, height - 180, f"SPI (Schedule Performance Index): {project.schedule_performance_index:.2f}" if project.schedule_performance_index else "No disponible")

    # Incluir gráfico de EVM
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_filename = temp_file.name
        plt.figure(figsize=(6, 4))
        weeks = list(range(1, 25))
        planned_costs = [float(project.planned_cost) * (week / 24) for week in weeks]
        earned_values = [float(project.earned_value) * (week / 24) for week in weeks]
        plt.plot(weeks, planned_costs, label="Planned Cost (PV)", color='blue', marker='o')
        plt.plot(weeks, earned_values, label="Earned Value (EV)", color='green', marker='o')
        plt.xlabel('Semanas')
        plt.ylabel('Cost / Value')
        plt.title(f'Rendimiento del Proyecto - {project.name}')
        plt.legend()
        plt.savefig(temp_filename)
        plt.close()

    # Dibujar gráfico en el PDF
    p.drawImage(temp_filename, 100, height - 400, width=400, height=200)

    # Cerrar el PDF
    p.showPage()
    p.save()

    # Eliminar la imagen temporal
    os.remove(temp_filename)

    return response


# Vista para exportar un único proyecto a CSV
@login_required
def export_project_csv(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Crear un dataframe con los datos del proyecto
    data = {
        'Nombre del Proyecto': [project.name],
        'Costo Planificado (PV)': [project.planned_cost],
        'Costo Real (AC)': [project.actual_cost],
        'Valor Ganado (EV)': [project.earned_value],
        'CPI': [project.cost_performance_index],
        'SPI': [project.schedule_performance_index],
        'Fecha de Inicio': [project.start_date],
        'Fecha de Fin': [project.end_date],
    }
    
    df = pd.DataFrame(data)

    # Crear la respuesta HTTP con el archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = f'attachment; filename="{project.name}_data.csv"'
    
    # Escribir el DataFrame en el archivo CSV
    df.to_csv(path_or_buf=response, index=False)

    return response

@login_required
def export_all_projects_csv(request):
    projects = Project.objects.all()

    # Crear una lista con los datos de todos los proyectos
    data = {
        'Nombre del Proyecto': [project.name for project in projects],
        'Costo Planificado (PV)': [project.planned_cost for project in projects],
        'Costo Real (AC)': [project.actual_cost for project in projects],
        'Valor Ganado (EV)': [project.earned_value for project in projects],
        'CPI': [project.cost_performance_index for project in projects],
        'SPI': [project.schedule_performance_index for project in projects],
        'Fecha de Inicio': [project.start_date for project in projects],
        'Fecha de Fin': [project.end_date for project in projects],
    }

    df = pd.DataFrame(data)

    # Crear la respuesta HTTP con el archivo CSV
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="all_projects_data.csv"'
    
    # Escribir el DataFrame en el archivo CSV
    df.to_csv(path_or_buf=response, index=False)

    return response
