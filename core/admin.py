from django.contrib import admin
from .models import Project

@admin.register(Project)
class ProjectAdmin(admin.ModelAdmin):
    list_display = ['name', 'planned_cost', 'actual_cost', 'earned_value', 'start_date', 'end_date']
