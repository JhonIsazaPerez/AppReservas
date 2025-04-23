from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .models import Reservation
from .forms import ReservationPeopleForm, ReservationDateTimeForm, ReservationContactForm

class ReservationListView(ListView):
    model = Reservation
    context_object_name = 'reservations'
    template_name = 'reservation/reservation_list.html'
    ordering = ['-date', '-time']

class ReservationDetailView(DetailView):
    model = Reservation
    context_object_name = 'reservation'
    template_name = 'reservation/reservation_detail.html'
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = self.get_object()
        # Agregar información sobre las acciones posibles
        context['can_confirm'] = reservation.can_confirm()
        context['can_finish'] = reservation.can_finish()
        context['can_cancel'] = reservation.can_cancel()
        return context

# VISTAS PARA CREACIÓN DE RESERVAS (PROCESO DE 3 PASOS)

class ReservationCreateStep1View(FormView):
    """Paso 1: Selección de número de personas"""
    form_class = ReservationPeopleForm
    template_name = 'reservation/create_step1.html'
    
    def form_valid(self, form):
        # Guardar datos del paso 1 en sesión
        self.request.session['reservation_step1'] = {
            'number_of_people': form.cleaned_data['number_of_people']
        }
        return redirect('reservation_create_step2')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Si hay datos en sesión de una visita anterior, rellenar el formulario
        if 'reservation_step1' in self.request.session:
            instance = Reservation(
                number_of_people=self.request.session['reservation_step1'].get('number_of_people', 1)
            )
            kwargs.update({'instance': instance})
        return kwargs

class ReservationCreateStep2View(FormView):
    """Paso 2: Selección de fecha y hora"""
    form_class = ReservationDateTimeForm
    template_name = 'reservation/create_step2.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si se completó el paso 1
        if 'reservation_step1' not in request.session:
            return redirect('reservation_create_step1')
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        # Guardar datos del paso 2 en sesión
        self.request.session['reservation_step2'] = {
            'date': form.cleaned_data['date'].isoformat(),
            'time': form.cleaned_data['time']
        }
        return redirect('reservation_create_step3')
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Si hay datos en sesión de una visita anterior, rellenar el formulario
        if 'reservation_step2' in self.request.session:
            from datetime import datetime
            
            date_str = self.request.session['reservation_step2'].get('date')
            date_obj = datetime.fromisoformat(date_str).date() if date_str else None
            
            instance = Reservation(
                date=date_obj,
                time=self.request.session['reservation_step2'].get('time')
            )
            kwargs.update({'instance': instance})
        return kwargs

class ReservationCreateStep3View(FormView):
    """Paso 3: Información de contacto y confirmación"""
    form_class = ReservationContactForm
    template_name = 'reservation/create_step3.html'
    success_url = reverse_lazy('reservation_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si se completaron los pasos anteriores
        if 'reservation_step1' not in request.session or 'reservation_step2' not in request.session:
            return redirect('reservation_create_step1')
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        # Añadir información de los pasos anteriores para revisión
        step1_data = self.request.session.get('reservation_step1', {})
        step2_data = self.request.session.get('reservation_step2', {})
        
        context.update({
            'number_of_people': step1_data.get('number_of_people'),
            'date': step2_data.get('date'),
            'time': step2_data.get('time'),
        })
        return context
    
    def form_valid(self, form):
        # Crear una reserva combinando todos los datos de los pasos
        from datetime import datetime
        
        step1_data = self.request.session['reservation_step1']
        step2_data = self.request.session['reservation_step2']
        
        date_str = step2_data.get('date')
        date_obj = datetime.fromisoformat(date_str).date() if date_str else None
        
        reservation = Reservation(
            name=form.cleaned_data['name'],
            phone_number=form.cleaned_data['phone_number'],
            number_of_people=step1_data.get('number_of_people'),
            date=date_obj,
            time=step2_data.get('time'),
            state=Reservation.StateChoices.PENDING
        )
        reservation.save()
        
        # Limpiar datos de sesión
        if 'reservation_step1' in self.request.session:
            del self.request.session['reservation_step1']
        if 'reservation_step2' in self.request.session:
            del self.request.session['reservation_step2']
        if 'reservation_step3' in self.request.session:
            del self.request.session['reservation_step3']
        
        messages.success(self.request, 'Reserva creada con éxito. Estado: Pendiente')
        return super().form_valid(form)
    
    def get_form_kwargs(self):
        kwargs = super().get_form_kwargs()
        # Si hay datos en sesión de una visita anterior, rellenar el formulario
        if 'reservation_step3' in self.request.session:
            instance = Reservation(
                name=self.request.session['reservation_step3'].get('name', ''),
                phone_number=self.request.session['reservation_step3'].get('phone_number', '')
            )
            kwargs.update({'instance': instance})
        return kwargs

# VISTAS PARA ACTUALIZACIÓN DE RESERVAS (PROCESO DE 3 PASOS)

class ReservationUpdateStep1View(UpdateView):
    """Paso 1: Actualizar número de personas"""
    model = Reservation
    form_class = ReservationPeopleForm
    template_name = 'reservation/update_step1.html'
    
    def form_valid(self, form):
        reservation = self.get_object()
        # Guardar el número de personas actualizado
        reservation.number_of_people = form.cleaned_data['number_of_people']
        reservation.save()
        
        # Guardar referencia al ID de la reserva en sesión para los siguientes pasos
        self.request.session['editing_reservation_id'] = reservation.id
        
        return redirect('reservation_update_step2', pk=reservation.id)

class ReservationUpdateStep2View(UpdateView):
    """Paso 2: Actualizar fecha y hora"""
    model = Reservation
    form_class = ReservationDateTimeForm
    template_name = 'reservation/update_step2.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si venimos del paso anterior o es edición directa
        reservation_id = kwargs.get('pk')
        session_id = request.session.get('editing_reservation_id')
        
        if session_id != reservation_id and session_id is not None:
            # Si el ID en sesión es distinto, redirigir al paso 1 con el ID correcto
            return redirect('reservation_update_step1', pk=reservation_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def form_valid(self, form):
        reservation = self.get_object()
        # Guardar la fecha y hora actualizadas
        reservation.date = form.cleaned_data['date']
        reservation.time = form.cleaned_data['time']
        reservation.save()
        
        return redirect('reservation_update_step3', pk=reservation.id)

class ReservationUpdateStep3View(UpdateView):
    """Paso 3: Actualizar información de contacto"""
    model = Reservation
    form_class = ReservationContactForm
    template_name = 'reservation/update_step3.html'
    success_url = reverse_lazy('reservation_list')
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si venimos del paso anterior o es edición directa
        reservation_id = kwargs.get('pk')
        session_id = request.session.get('editing_reservation_id')
        
        if session_id != reservation_id and session_id is not None:
            # Si el ID en sesión es distinto, redirigir al paso 1
            return redirect('reservation_update_step1', pk=reservation_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = self.get_object()
        # Añadir información de los campos ya actualizados para revisión
        context.update({
            'number_of_people': reservation.number_of_people,
            'date': reservation.date,
            'time': reservation.time,
        })
        return context
    
    def form_valid(self, form):
        messages.success(self.request, 'Reserva actualizada con éxito.')
        # Limpiar datos de sesión
        if 'editing_reservation_id' in self.request.session:
            del self.request.session['editing_reservation_id']
            
        return super().form_valid(form)

# Mantener las vistas para los cambios de estado
def confirm_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.confirm():
        messages.success(request, 'Reserva confirmada con éxito')
    else:
        messages.error(request, 'No se puede confirmar la reserva en su estado actual')
    return redirect('reservation_detail', pk=pk)

def finish_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.finish():
        messages.success(request, 'Reserva finalizada con éxito')
    else:
        messages.error(request, 'No se puede finalizar la reserva en su estado actual')
    return redirect('reservation_detail', pk=pk)

def cancel_reservation(request, pk):
    reservation = get_object_or_404(Reservation, pk=pk)
    if reservation.cancel():
        messages.success(request, 'Reserva cancelada con éxito')
    else:
        messages.error(request, 'No se puede cancelar la reserva en su estado actual')
    return redirect('reservation_detail', pk=pk)

# API para cambios de estado (opcional, para uso con AJAX)
# EN CASO DE USAR JAVASCRIPT O AJAX EN EL FRONTEND
"""def api_change_state(request, pk):
    if request.method != 'POST':
        return JsonResponse({'error': 'Método no permitido'}, status=405)
    
    action = request.POST.get('action')
    reservation = get_object_or_404(Reservation, pk=pk)
    result = False
    
    if action == 'confirm':
        result = reservation.confirm()
    elif action == 'finish':
        result = reservation.finish()
    elif action == 'cancel':
        result = reservation.cancel()
    
    if result:
        return JsonResponse({
            'success': True,
            'state': reservation.state,
            'state_display': reservation.get_state_display()
        })
    else:
        return JsonResponse({
            'success': False,
            'error': 'No se pudo cambiar el estado de la reserva'
        })
"""