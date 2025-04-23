from django import forms
from django.utils.translation import gettext_lazy as _
from datetime import time
from .models import Reservation

class ReservationDateTimeForm(forms.ModelForm):
    """Formulario para el segundo paso: selección de fecha y hora"""
    
    class Meta:
        model = Reservation
        fields = ['date', 'time']
        widgets = {
            'date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        
        # Si tenemos una fecha seleccionada, filtramos las horas disponibles
        if 'date' in self.data:
            selected_date = self.data.get('date')
            if selected_date:
                self._set_available_hours(selected_date)
        
        # En caso de edición, también mostrar las horas disponibles
        elif self.instance and self.instance.pk and self.instance.date:
            self._set_available_hours(self.instance.date)
        else:
            # Si no hay fecha seleccionada, mostrar mensaje para seleccionar fecha primero
            self.fields['time'] = forms.ChoiceField(
                choices=[],
                label=_('Hora'),
                help_text=_('Seleccione una fecha primero para ver las horas disponibles')
            )
    
    def _set_available_hours(self, selected_date):
        """Configura las horas disponibles para una fecha seleccionada"""
        # Obtener horas ocupadas para esa fecha
        unavailable_times = Reservation.get_unavailable_times(selected_date)
        
        # Si estamos editando, permitir la hora actual
        current_time = None
        if self.instance and self.instance.pk:
            current_time = self.instance.time.strftime('%H:%M:%S')
        
        # Crear opciones de hora en intervalos de 1 hora (9:00 a 22:00)
        available_hours = []
        for h in range(9, 23):  # Horario de 9am a 10pm
            current_hour = time(hour=h, minute=0)
            time_str = current_hour.strftime('%H:%M:%S')
            
            # Verificar si esta hora está disponible (o es la actual en edición)
            if time_str not in unavailable_times or time_str == current_time:
                formatted_time = f"{h:02d}:00"
                available_hours.append((time_str, formatted_time))
        
        # Actualizar el campo time para mostrar solo horas disponibles
        self.fields['time'] = forms.ChoiceField(
            choices=available_hours,
            label=_('Hora'),
            widget=forms.Select(attrs={'class': 'form-control'}),
            help_text=_('Seleccione una hora disponible para su reserva')
        )

class ReservationContactForm(forms.ModelForm):
    """Formulario para el tercer paso: información de contacto"""
    
    class Meta:
        model = Reservation
        fields = ['name', 'phone_number']
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Nombre completo'
            }),
            'phone_number': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Número telefónico',
                'pattern': '[0-9]{10}'  # Patrón para 10 dígitos
            }),
        }
        labels = {
            'name': _('Nombre'),
            'phone_number': _('Teléfono de contacto'),
        }
        help_texts = {
            'phone_number': _('Ingrese un número telefónico válido sin espacios ni guiones'),
        }