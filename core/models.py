from django.db import models

class Project(models.Model):
    name = models.CharField(max_length=100)
    planned_cost = models.DecimalField(max_digits=10, decimal_places=2)
    actual_cost = models.DecimalField(max_digits=10, decimal_places=2)
    earned_value = models.DecimalField(max_digits=10, decimal_places=2)
    planned_value = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    start_date = models.DateField()
    end_date = models.DateField()

    def __str__(self):
        return self.name

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

    @property
    def cost_variance(self):
        """Calcula el CV: CV = EV - AC"""
        return self.earned_value - self.actual_cost

    @property
    def schedule_variance(self):
        """Calcula el SV: SV = EV - PV"""
        return self.earned_value - self.planned_cost

    @property
    def cost_schedule_index(self):
        """Calcula el CSI: CSI = CPI * SPI"""
        cpi = self.cost_performance_index
        spi = self.schedule_performance_index
        if cpi is not None and spi is not None:
            return cpi * spi
        return None

    @property
    def estimate_to_complete(self):
        """Calcula el ETC: ETC = (BAC - EV) / CPI"""
        cpi = self.cost_performance_index
        if cpi and cpi > 0:
            return (self.planned_cost - self.earned_value) / cpi
        return None

    @property
    def estimate_at_completion(self):
        """Calcula el EAC: EAC = AC + ETC"""
        etc = self.estimate_to_complete
        if etc is not None:
            return self.actual_cost + etc
        return None
