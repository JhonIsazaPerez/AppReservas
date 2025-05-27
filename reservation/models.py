from django.db import models
from django.utils.translation import gettext_lazy as _
from abc import ABC, abstractmethod
from django.core.validators import EmailValidator
from django.utils import timezone  # Importar timezone para comparar fechas y horas actuales
from django.contrib.auth.models import User
from datetime import datetime, timedelta
from .utils import send_reservation_email  # Importar la función para enviar correos electrónicos

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
        reservation.delete()
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
        reservation.delete()
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
    
class Coupon(models.Model):
    code = models.CharField(max_length=20, unique=True)
    is_used = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def apply_coupon(self):
        self.is_used = True
        self.save()

# Modelo Reservation modificado
class Reservation(models.Model):
    # Estados posibles para la reserva (mantener para compatibilidad con Django)
    class StateChoices(models.TextChoices):
        PENDING = 'pending', _('Pendiente')
        CONFIRMED = 'confirmed', _('Confirmada')
        FINISHED = 'finished', _('Finalizada')
        CANCELLED = 'cancelled', _('Cancelada')
    
    name = models.CharField(max_length=100)
    email = models.EmailField(validators=[EmailValidator()], default="example@gmail.com")  # Cambiado desde phone_number
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
    usuario = models.ForeignKey(User, on_delete=models.CASCADE)
    
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
    
    
    def generate_coupon_if_needed():
        confirmed_reservations = Reservation.objects.filter(state='confirmed').count()
        if confirmed_reservations % 5 == 0:  # Cada 5 reservas confirmadas, generar un cupón
            Coupon.objects.create(code=f'COUPON-{confirmed_reservations}')

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
        send_reservation_email(self)#cuando se cambia el estado, enviar un correo electrónico

    def __str__(self):
        return f"{self.name} - {self.date} {self.time} - {self.state}"
    
    def confirm(self):
        """Confirma la reserva si es posible según su estado actual"""
        if self._state_object.confirm(self):
            Reservation.generate_coupon_if_needed()
            return True
        return False
    
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
    def get_unavailable_times(date, number_of_people=None):
        """
        Retorna una lista de horas que ya están reservadas para una fecha específica,
        considerando el tamaño de la mesa/grupo.
        
        Args:
            date: La fecha para verificar disponibilidad
            number_of_people: El tamaño del grupo que desea reservar (opcional)
        """
        # Definir capacidad del restaurante por tamaño de mesa
        # Por ejemplo, podríamos tener:
        # - 5 mesas para 2 personas
        # - 4 mesas para 4 personas
        # - 3 mesas para 6 personas
        # - 2 mesas para 8 personas
        table_capacity = {
            2: 5,  # 5 mesas para 2 personas
            4: 4,  # 4 mesas para 4 personas
            6: 3,  # 3 mesas para 6 personas
            8: 2,  # 2 mesas para 8+ personas
        }
        
        # Si no se especifica número de personas, usar el método original
        if number_of_people is None:
            # Obtener reservas confirmadas/pendientes para esa fecha
            confirmed_reservations = Reservation.objects.filter(
                date=date,
                state__in=[
                    Reservation.StateChoices.CONFIRMED,
                    Reservation.StateChoices.PENDING
                ]
            )
            # Extraer las horas de las reservas existentes
            unavailable_times = [
                reservation.time.strftime('%H:%M:%S') 
                for reservation in confirmed_reservations
            ]
            return unavailable_times
        
        # Determinar qué tipo de mesa necesita según el número de personas
        table_size = None
        for size in sorted(table_capacity.keys()):
            if number_of_people <= size:
                table_size = size
                break
        
        # Si es un grupo muy grande que excede nuestras categorías predefinidas
        if table_size is None:
            table_size = max(table_capacity.keys())  # Usar la mesa más grande disponible
        
        # Obtener todas las reservas para esa fecha
        all_reservations = Reservation.objects.filter(
            date=date,
            state__in=[
                Reservation.StateChoices.CONFIRMED,
                Reservation.StateChoices.PENDING
            ]
        )
        
        # Agrupar reservas por hora
        reservations_by_time = {}
        for reservation in all_reservations:
            time_str = reservation.time.strftime('%H:%M:%S')
            if time_str not in reservations_by_time:
                reservations_by_time[time_str] = []
            reservations_by_time[time_str].append(reservation)
        
        # Determinar horas no disponibles
        unavailable_times = []
        for time_str, reservations in reservations_by_time.items():
            # Contar cuántas mesas de cada tipo están ocupadas a esta hora
            tables_in_use = {size: 0 for size in table_capacity.keys()}
            
            for res in reservations:
                # Determinar qué tipo de mesa está usando cada reserva
                res_size = None
                for size in sorted(table_capacity.keys()):
                    if res.number_of_people <= size:
                        res_size = size
                        break
                if res_size is None:
                    res_size = max(table_capacity.keys())
                    
                tables_in_use[res_size] += 1
            
            # Verificar si hay mesas disponibles del tamaño requerido
            if tables_in_use[table_size] >= table_capacity[table_size]:
                unavailable_times.append(time_str)
        
        return unavailable_times
    
    def check_if_should_finish(self):
        """
        Verifica si la reserva debería pasar a estado FINISHED basado en la fecha y hora actuales.
        Devuelve True si la reserva fue actualizada, False en caso contrario.
        """
        if self.state != self.StateChoices.CONFIRMED:
            return False  # Solo las reservas confirmadas pueden pasar a finalizadas automáticamente
            
        now = timezone.now()
        # Combinamos fecha y hora de la reserva para comparar
        reservation_datetime = datetime.combine(self.date, self.time)
        reservation_datetime = timezone.make_aware(reservation_datetime)
        
        # Si la fecha y hora actuales superan la de la reserva
        if now > reservation_datetime:
            # Pasar a estado finalizado
            self.finish()
            return True
            
        return False
    
    def refresh_state(self):
        """
        Actualiza el estado de la reserva si es necesario basado en la fecha/hora actual.
        """
        # Solo revisar si debe finalizar si está confirmada
        if self.state == self.StateChoices.CONFIRMED:
            return self.check_if_should_finish()
        return False

    # Sobreescribir el método save para verificar el estado cuando se guarde
    def save(self, *args, **kwargs):
        # Primero guardamos para asegurarnos de tener un ID
        super().save(*args, **kwargs)
        # Luego verificamos si el estado debe cambiar
        self.refresh_state()