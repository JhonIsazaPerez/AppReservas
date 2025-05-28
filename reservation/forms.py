from django import forms
from django.utils.translation import gettext_lazy as _
from django.utils import timezone
from datetime import datetime, timedelta, time
from .models import Reservation

class ReservationDateForm(forms.ModelForm):
    """Formulario para seleccionar la fecha de reserva"""
    class Meta:
        model = Reservation
        fields = ['date']
        widgets = {
            'date': forms.DateInput(attrs={
                'type': 'date', 
                'class': 'form-control',
                'id': 'reservation-date', 
                'initial': datetime.now().date().strftime('%Y-%m-%d'), 
                'placeholder': datetime.now().date().strftime('%Y-%m-%d'),
                'value': datetime.now().date().strftime('%d-%m-%y'),
            }),
        }
        labels = {
            'date': _('Fecha de reserva'),
        }

class ReservationTimeForm(forms.Form):
    """Formulario para seleccionar la hora de reserva"""
    

    time = forms.ChoiceField(
        choices=[],
        label=_('Hora'),
        widget=forms.Select(attrs={'class': 'form-control'}),
        help_text=_('Seleccione una hora disponible para su reserva')
    )
    
    def __init__(self, *args, selected_date=None, instance=None, number_of_people=None, **kwargs):
        super().__init__(*args, **kwargs)
        
        if selected_date:
            self._set_available_hours(selected_date, instance, number_of_people)
        else:
            self.fields['time'].choices = []
            self.fields['time'].help_text = _('Seleccione una fecha primero para ver las horas disponibles')
    
    def _set_available_hours(self, selected_date, instance=None, number_of_people=None):
        """Configura las horas disponibles para una fecha seleccionada"""
        # Obtener horas ocupadas para esa fecha
        unavailable_times = Reservation.get_unavailable_times(
            selected_date, 
            number_of_people
        )
        
        # Si estamos editando, permitir la hora actual
        current_time = None
        if instance and instance.pk:
            current_time = instance.time.strftime('%H:%M:%S')
        
        now = timezone.localtime()
        now = now.now()
        today = now.date()
        current_hour_now = now.hour if selected_date == today else 0
        print(selected_date)
        print(today)
        # Crear opciones de hora en intervalos de 1 hora (9:00 a 22:00)
        available_hours = []
        for h in range(9, 23):  # Horario de 9am a 10pm
            current_hour = time(hour=h, minute=0)
            time_str = current_hour.strftime('%H:%M:%S')
            # Verificar si esta hora está disponible (o es la actual en edición)
            if time_str not in unavailable_times or time_str == current_time:
                if current_hour_now <= h < 23: 
                    #print(current_hour_now)# Solo horas futuras
                    formatted_time = f"{h:02d}:00"
                    available_hours.append((time_str, formatted_time))
        
        # Actualizar el campo time para mostrar solo horas disponibles
        self.fields['time'].choices = available_hours
        
        if not available_hours:
            self.fields['time'].help_text = _('No hay horas disponibles para esta fecha. Por favor, seleccione otra fecha.')

class ReservationContactForm(forms.ModelForm):
    """Formulario para el tercer paso: información de contacto"""
    
    class Meta:
        model = Reservation
        fields = ['name', 'email']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control'}),
            'email': forms.EmailInput(attrs={'class': 'form-control'}),
        }
        labels = {
            'name': _('Nombre'),
            'email': _('Correo electrónico'),
        }
        help_texts = {
            'email': _('Recibirá un correo de confirmación con los detalles de su reserva'),
        }