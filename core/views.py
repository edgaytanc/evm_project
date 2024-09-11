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
from django.contrib import messages
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

# Vista para eliminar un proyecto
@login_required
def project_delete(request, pk):
    project = get_object_or_404(Project, pk=pk)
    
    if request.method == 'POST':
        project.delete()
        messages.success(request, 'Proyecto eliminado exitosamente.')
        return redirect('project_list')
    
    return render(request, 'core/project_confirm_delete.html', {'project': project})

# Vista para listar y ver los proyectos
@login_required
def project_list(request):
    projects = Project.objects.all()
    return render(request, 'core/project_list.html', {'projects': projects})

# Nueva vista para ver detalles de un proyecto
@login_required
def project_detail(request, pk):
    project = get_object_or_404(Project, pk=pk)

    # Calcular métricas adicionales
    cv = project.cost_variance  # Cost Variance
    sv = project.schedule_variance  # Schedule Variance
    csi = project.cost_schedule_index  # Cost Schedule Index
    etc = project.estimate_to_complete  # Estimate to Complete
    eac = project.estimate_at_completion  # Estimate at Completion

    context = {
        'project': project,
        'cv': cv,
        'sv': sv,
        'csi': csi,
        'etc': etc,
        'eac': eac,
    }

    return render(request, 'core/project_detail.html', context)





# Vista para el Dashboard


@login_required
def dashboard(request):
    total_projects = Project.objects.count()

    if total_projects > 0:
        avg_cpi = float(Project.objects.aggregate(Avg('earned_value'))['earned_value__avg']) / float(Project.objects.aggregate(Avg('actual_cost'))['actual_cost__avg'])
        avg_spi = float(Project.objects.aggregate(Avg('earned_value'))['earned_value__avg']) / float(Project.objects.aggregate(Avg('planned_cost'))['planned_cost__avg'])
        avg_cv = float(Project.objects.aggregate(Avg('earned_value'))['earned_value__avg']) - float(Project.objects.aggregate(Avg('actual_cost'))['actual_cost__avg'])
        avg_sv = float(Project.objects.aggregate(Avg('earned_value'))['earned_value__avg']) - float(Project.objects.aggregate(Avg('planned_cost'))['planned_cost__avg'])
        avg_etc = (float(Project.objects.aggregate(Avg('planned_cost'))['planned_cost__avg']) - float(Project.objects.aggregate(Avg('earned_value'))['earned_value__avg']))
        avg_eac = avg_etc + float(Project.objects.aggregate(Avg('actual_cost'))['actual_cost__avg'])
    else:
        avg_cpi = avg_spi = avg_cv = avg_sv = avg_etc = avg_eac = None

    # Simulación de datos semanales de rendimiento global
    weeks = list(range(1, 25))  # 24 semanas
    avg_planned_costs = [float(sum(project.planned_cost for project in Project.objects.all())) * (week / 24) for week in weeks]
    avg_earned_values = [float(sum(project.earned_value for project in Project.objects.all())) * (week / 24) for week in weeks]
    avg_actual_costs = [float(sum(project.actual_cost for project in Project.objects.all())) * (week / 24) for week in weeks]

    # Creación de gráficos individuales

    # Gráfico PV, AC y EV
    plt.figure(figsize=(6, 4))
    plt.plot(weeks, avg_planned_costs, label="PV", color='blue', marker='o')
    plt.plot(weeks, avg_actual_costs, label="AC", color='red', marker='o')
    plt.plot(weeks, avg_earned_values, label="EV", color='green', marker='o')
    plt.xlabel('Weeks')
    plt.ylabel('Cost / Value')
    plt.title('PV, AC y EV')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    pv_ac_ev_chart_uri = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Gráfico CV y SV
    plt.figure(figsize=(6, 4))
    avg_cv_values = [ev - ac for ev, ac in zip(avg_earned_values, avg_actual_costs)]
    avg_sv_values = [ev - pv for ev, pv in zip(avg_earned_values, avg_planned_costs)]
    plt.plot(weeks, avg_cv_values, label="CV", color='blue', marker='o', linestyle='--')
    plt.plot(weeks, avg_sv_values, label="SV", color='green', marker='o', linestyle='--')
    plt.xlabel('Weeks')
    plt.ylabel('CV / SV')
    plt.title('CV y SV')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    cv_sv_chart_uri = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Gráfico CPI, SPI y CR
    plt.figure(figsize=(6, 4))
    avg_cpi_values = [ev / ac if ac != 0 else 0 for ev, ac in zip(avg_earned_values, avg_actual_costs)]
    avg_spi_values = [ev / pv if pv != 0 else 0 for ev, pv in zip(avg_earned_values, avg_planned_costs)]
    avg_cr_values = [spi * cpi for spi, cpi in zip(avg_spi_values, avg_cpi_values)]
    plt.plot(weeks, avg_cpi_values, label="CPI", color='blue', marker='o', linestyle='--')
    plt.plot(weeks, avg_spi_values, label="SPI", color='green', marker='o', linestyle='--')
    plt.plot(weeks, avg_cr_values, label="CR", color='red', marker='o', linestyle='--')
    plt.xlabel('Weeks')
    plt.ylabel('CPI / SPI / CR')
    plt.title('CPI, SPI y CR')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    cpi_spi_cr_chart_uri = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Gráfico ETC y EAC
    plt.figure(figsize=(6, 4))
    avg_etc_values = [avg_etc for _ in weeks]
    avg_eac_values = [avg_eac for _ in weeks]
    plt.plot(weeks, avg_etc_values, label="ETC", color='blue', marker='o', linestyle='--')
    plt.plot(weeks, avg_eac_values, label="EAC", color='green', marker='o', linestyle='--')
    plt.xlabel('Weeks')
    plt.ylabel('ETC / EAC')
    plt.title('ETC y EAC')
    plt.legend()
    buf = io.BytesIO()
    plt.savefig(buf, format='png')
    buf.seek(0)
    etc_eac_chart_uri = base64.b64encode(buf.read()).decode('utf-8')
    plt.close()

    # Contexto del template
    context = {
        'project_summary': {
            'total_projects': total_projects,
            'avg_cpi': avg_cpi,
            'avg_spi': avg_spi,
            'avg_cv': avg_cv,
            'avg_sv': avg_sv,
            'avg_etc': avg_etc,
            'avg_eac': avg_eac,
            'pv_ac_ev_chart_uri': pv_ac_ev_chart_uri,  # Gráfico PV, AC y EV
            'cv_sv_chart_uri': cv_sv_chart_uri,        # Gráfico CV y SV
            'cpi_spi_cr_chart_uri': cpi_spi_cr_chart_uri,  # Gráfico CPI, SPI y CR
            'etc_eac_chart_uri': etc_eac_chart_uri,    # Gráfico ETC y EAC
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
    actual_cost = float(project.actual_cost)

    # Simulación de datos semanales de costo planificado (PV) y valor ganado (EV)
    weeks = list(range(1, 25))  # 24 semanas
    planned_costs = [planned_cost * (week / 24) for week in weeks]  # Simular evolución PV
    earned_values = [earned_value * (week / 24) for week in weeks]  # Simular evolución EV
    actual_costs = [actual_cost * (week / 24) for week in weeks]  # Simular evolución AC

    # Calcular Cost Variance (CV) y Schedule Variance (SV) semanalmente
    cost_variances = [earned_values[i] - actual_costs[i] for i in range(len(weeks))]  # CV = EV - AC
    schedule_variances = [earned_values[i] - planned_costs[i] for i in range(len(weeks))]  # SV = EV - PV

    # Crear el gráfico con Matplotlib
    plt.figure(figsize=(10, 6))
    plt.plot(weeks, planned_costs, label="Planned Cost (PV)", color='blue', marker='o')
    plt.plot(weeks, earned_values, label="Earned Value (EV)", color='green', marker='o')
    plt.plot(weeks, actual_costs, label="Actual Cost (AC)", color='red', linestyle='--', marker='x')
    plt.plot(weeks, cost_variances, label="Cost Variance (CV)", color='orange', linestyle='--', marker='s')
    plt.plot(weeks, schedule_variances, label="Schedule Variance (SV)", color='purple', linestyle='--', marker='x')
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

    # Incluir las nuevas métricas en el PDF
    p.drawString(100, height - 160, f"CPI (Cost Performance Index): {project.cost_performance_index:.2f}" if project.cost_performance_index else "No disponible")
    p.drawString(100, height - 180, f"SPI (Schedule Performance Index): {project.schedule_performance_index:.2f}" if project.schedule_performance_index else "No disponible")
    p.drawString(100, height - 200, f"CV (Cost Variance): {project.cost_variance:.2f}" if project.cost_variance else "No disponible")
    p.drawString(100, height - 220, f"SV (Schedule Variance): {project.schedule_variance:.2f}" if project.schedule_variance else "No disponible")
    p.drawString(100, height - 240, f"CSI (Cost Schedule Index): {project.cost_schedule_index:.2f}" if project.cost_schedule_index else "No disponible")
    p.drawString(100, height - 260, f"EAC (Estimate at Completion): {project.estimate_at_completion:.2f}" if project.estimate_at_completion else "No disponible")
    p.drawString(100, height - 280, f"ETC (Estimate to Complete): {project.estimate_to_complete:.2f}" if project.estimate_to_complete else "No disponible")

    # Incluir gráfico de EVM actualizado
    with tempfile.NamedTemporaryFile(suffix=".png", delete=False) as temp_file:
        temp_filename = temp_file.name
        plt.figure(figsize=(6, 4))
        weeks = list(range(1, 25))
        planned_costs = [float(project.planned_cost) * (week / 24) for week in weeks]
        earned_values = [float(project.earned_value) * (week / 24) for week in weeks]
        actual_costs = [float(project.actual_cost) * (week / 24) for week in weeks]  # Simular AC
        cost_variances = [earned_values[i] - actual_costs[i] for i in range(len(weeks))]  # CV = EV - AC
        schedule_variances = [earned_values[i] - planned_costs[i] for i in range(len(weeks))]  # SV = EV - PV

        # Crear el gráfico
        plt.plot(weeks, planned_costs, label="Planned Cost (PV)", color='blue', marker='o')
        plt.plot(weeks, earned_values, label="Earned Value (EV)", color='green', marker='o')
        plt.plot(weeks, actual_costs, label="Actual Cost (AC)", color='red', linestyle='--', marker='x')
        plt.plot(weeks, cost_variances, label="Cost Variance (CV)", color='orange', linestyle='--', marker='s')
        plt.plot(weeks, schedule_variances, label="Schedule Variance (SV)", color='purple', linestyle='--', marker='x')
        plt.xlabel('Semanas')
        plt.ylabel('Cost / Value')
        plt.title(f'Rendimiento del Proyecto - {project.name}')
        plt.legend()

        plt.savefig(temp_filename)
        plt.close()

    # Dibujar gráfico en el PDF
    p.drawImage(temp_filename, 100, height - 500, width=400, height=200)

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

    # Crear un dataframe con los datos del proyecto y las nuevas métricas
    data = {
        'Nombre del Proyecto': [project.name],
        'Costo Planificado (PV)': [project.planned_cost],
        'Costo Real (AC)': [project.actual_cost],
        'Valor Ganado (EV)': [project.earned_value],
        'CPI (Cost Performance Index)': [project.cost_performance_index],
        'SPI (Schedule Performance Index)': [project.schedule_performance_index],
        'CV (Cost Variance)': [project.cost_variance],
        'SV (Schedule Variance)': [project.schedule_variance],
        'CSI (Cost Schedule Index)': [project.cost_schedule_index],
        'EAC (Estimate at Completion)': [project.estimate_at_completion],
        'ETC (Estimate to Complete)': [project.estimate_to_complete],
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

    # Crear una lista con los datos de todos los proyectos, incluyendo las nuevas métricas
    data = {
        'Nombre del Proyecto': [project.name for project in projects],
        'Costo Planificado (PV)': [project.planned_cost for project in projects],
        'Costo Real (AC)': [project.actual_cost for project in projects],
        'Valor Ganado (EV)': [project.earned_value for project in projects],
        'CPI (Cost Performance Index)': [project.cost_performance_index for project in projects],
        'SPI (Schedule Performance Index)': [project.schedule_performance_index for project in projects],
        'CV (Cost Variance)': [project.cost_variance for project in projects],
        'SV (Schedule Variance)': [project.schedule_variance for project in projects],
        'CSI (Cost Schedule Index)': [project.cost_schedule_index for project in projects],
        'EAC (Estimate at Completion)': [project.estimate_at_completion for project in projects],
        'ETC (Estimate to Complete)': [project.estimate_to_complete for project in projects],
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

