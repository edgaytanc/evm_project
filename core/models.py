from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100)
    planned_cost = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    earned_value = models.DecimalField(max_digits=10, decimal_places=2)
    planned_value = models.DecimalField(max_digits=10, decimal_places=2,null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

    # Métodos para cálculos adicionales (opcional)
    @property
    def cost_performance_index(self):
        """Calcula el CPI: CPI = EV / AC"""
        if self.actual_cost > 0:
            return self.earned_value / self.actual_cost
        return None

    @property
    def schedule_performance_index(self):
        """Calcula el SPI: SPI = EV / PV"""
        if self.planned_cost > 0:
            return self.earned_value / self.planned_cost
        return None
