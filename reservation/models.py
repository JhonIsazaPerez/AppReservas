from django.db import models
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractmethod

# Clase abstracta base para los estados
class ReservationState(ABC):
    @abstractmethod
    def confirm(self, reservation):
        pass
    
    @abstractmethod
    def finish(self, reservation):
        pass
    
    @abstractmethod
    def cancel(self, reservation):
        pass
    
    @abstractmethod
    def can_confirm(self):
        pass
    
    @abstractmethod
    def can_finish(self):
        pass
    
    @abstractmethod
    def can_cancel(self):
        pass

# Implementaciones concretas de cada estado
class PendingState(ReservationState):
    def confirm(self, reservation):
        reservation._change_state(ConfirmedState())
        return True
    
    def finish(self, reservation):
        return False
    
    def cancel(self, reservation):
        reservation._change_state(CancelledState())
        return True
    
    def can_confirm(self):
        return True
    
    def can_finish(self):
        return False
    
    def can_cancel(self):
        return True

class ConfirmedState(ReservationState):
    def confirm(self, reservation):
        return False
    
    def finish(self, reservation):
        reservation._change_state(FinishedState())
        return True
    
    def cancel(self, reservation):
        reservation._change_state(CancelledState())
        return True
    
    def can_confirm(self):
        return False
    
    def can_finish(self):
        return True
    
    def can_cancel(self):
        return True

class FinishedState(ReservationState):
    def confirm(self, reservation):
        return False
    
    def finish(self, reservation):
        return False
    
    def cancel(self, reservation):
        return False
    
    def can_confirm(self):
        return False
    
    def can_finish(self):
        return False
    
    def can_cancel(self):
        return False

class CancelledState(ReservationState):
    def confirm(self, reservation):
        return False
    
    def finish(self, reservation):
        return False
    
    def cancel(self, reservation):
        return False
    
    def can_confirm(self):
        return False
    
    def can_finish(self):
        return False
    
    def can_cancel(self):
        return False

# Modelo Reservation modificado
class Reservation(models.Model):
    # Estados posibles para la reserva (mantener para compatibilidad con Django)
    class StateChoices(models.TextChoices):
        PENDING = 'pending', _('Pendiente')
        CONFIRMED = 'confirmed', _('Confirmada')
        FINISHED = 'finished', _('Finalizada')
        CANCELLED = 'cancelled', _('Cancelada')
    
    name = models.CharField(max_length=100)
    phone_number = models.CharField(max_length=15)
    date = models.DateField()
    time = models.TimeField()
    number_of_people = models.IntegerField()
    state = models.CharField(
        max_length=20,
        choices=StateChoices.choices,
        default=StateChoices.PENDING,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._state_object = self._get_state_object()
    
    def _get_state_object(self):
        if self.state == self.StateChoices.PENDING:
            return PendingState()
        elif self.state == self.StateChoices.CONFIRMED:
            return ConfirmedState()
        elif self.state == self.StateChoices.FINISHED:
            return FinishedState()
        elif self.state == self.StateChoices.CANCELLED:
            return CancelledState()
        else:
            return PendingState()  # Estado por defecto
    
    def _change_state(self, new_state):
        self._state_object = new_state
        # Actualizar el campo state para la base de datos
        if isinstance(new_state, PendingState):
            self.state = self.StateChoices.PENDING
        elif isinstance(new_state, ConfirmedState):
            self.state = self.StateChoices.CONFIRMED
        elif isinstance(new_state, FinishedState):
            self.state = self.StateChoices.FINISHED
        elif isinstance(new_state, CancelledState):
            self.state = self.StateChoices.CANCELLED
        self.save()

    def __str__(self):
        return f"{self.name} - {self.date} {self.time} - {self.state}"
    
    def confirm(self):
        """Confirma la reserva si es posible según su estado actual"""
        return self._state_object.confirm(self)
    
    def finish(self):
        """Finaliza la reserva si es posible según su estado actual"""
        return self._state_object.finish(self)
    
    def cancel(self):
        """Cancela la reserva si es posible según su estado actual"""
        return self._state_object.cancel(self)
    
    def can_confirm(self):
        """Verifica si la reserva puede ser confirmada"""
        return self._state_object.can_confirm()
    
    def can_finish(self):
        """Verifica si la reserva puede ser finalizada"""
        return self._state_object.can_finish()
    
    def can_cancel(self):
        """Verifica si la reserva puede ser cancelada"""
        return self._state_object.can_cancel()
    

    @staticmethod
    def get_unavailable_times(date):
        """Retorna una lista de horas que ya están reservadas para una fecha específica"""
        # Obtener reservas confirmadas para esa fecha
        confirmed_reservations = Reservation.objects.filter(
            date=date,
            state__in=[
                Reservation.StateChoices.CONFIRMED,
                Reservation.StateChoices.PENDING  # Opcional: también considerar pendientes
            ]
        )
        # Extraer las horas de las reservas existentes
        unavailable_times = [
            reservation.time.strftime('%H:%M:%S') 
            for reservation in confirmed_reservations
        ]
        return unavailable_times