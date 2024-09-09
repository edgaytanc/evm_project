from django import forms
from .models import Project

class ProjectForm(forms.ModelForm):
    class Meta:
        model = Project
        fields = ['name', 'planned_cost', 'actual_cost', 'earned_value','planned_value', 'start_date', 'end_date']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Nombre del Proyecto'}),
            'planned_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Costo Planificado'}),
            'actual_cost': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Costo Real'}),
            'earned_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor Ganado'}),
            'planned_value': forms.NumberInput(attrs={'class': 'form-control', 'placeholder': 'Valor planificado'}),  # Widget para planned_value
            'start_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
            'end_date': forms.DateInput(attrs={'class': 'form-control', 'type': 'date'}),
        }
