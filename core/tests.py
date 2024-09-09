from django.test import TestCase
from django.urls import reverse
from .models import Project
from datetime import date

from django.contrib.auth.models import User

class ProjectTestCase(TestCase):
    def setUp(self):
        # Crear un proyecto de prueba y un usuario para las pruebas
        self.user = User.objects.create_user(username='testuser', password='12345')
        self.client.login(username='testuser', password='12345')

        self.project = Project.objects.create(
            name="Proyecto de prueba",
            planned_cost=100000,
            actual_cost=90000,
            earned_value=85000,
            start_date=date(2023, 1, 1),
            end_date=date(2023, 12, 31)
        )

    def test_create_project_view(self):
        response = self.client.post(reverse('project_create'), {
            'name': 'Nuevo Proyecto',
            'planned_cost': 120000,
            'actual_cost': 100000,
            'earned_value': 95000,
            'start_date': '2024-01-01',
            'end_date': '2024-12-31'
        })
        self.assertEqual(response.status_code, 302)  # Verifica que la redirección se produjo correctamente
        self.assertTrue(Project.objects.filter(name='Nuevo Proyecto').exists())  # Verifica si el proyecto fue creado
    
    def test_edit_project_view(self):
        response = self.client.post(reverse('project_edit', args=[self.project.id]), {
            'name': 'Proyecto Modificado',
            'planned_cost': 120000,
            'actual_cost': 95000,
            'earned_value': 90000,
            'start_date': '2023-01-01',
            'end_date': '2023-12-31'
        })
        self.assertEqual(response.status_code, 302)  # Verifica que la redirección se produjo correctamente
        project = Project.objects.get(id=self.project.id)
        self.assertEqual(project.name, 'Proyecto Modificado')  # Verifica que el nombre fue actualizado

    def test_evm_calculations(self):
        project = Project.objects.get(name="Proyecto de prueba")
        cpi = float(project.cost_performance_index)  # Convertir a float
        spi = float(project.schedule_performance_index)  # Convertir a float

        # CPI = EV / AC
        self.assertAlmostEqual(cpi, 85000 / 90000, places=5)

        # SPI = EV / PV
        self.assertAlmostEqual(spi, 85000 / 100000, places=5)


