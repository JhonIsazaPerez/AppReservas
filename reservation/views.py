from datetime import datetime, time
from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views import View
from django.views.generic import ListView, DetailView, CreateView, UpdateView, FormView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy, reverse
from django.http import JsonResponse
from .models import Reservation, Coupon
from .forms import ReservationDateForm, ReservationContactForm, ReservationTimeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from usuarios.views import login_view

def coupon_list(request):
    coupons = Coupon.objects.filter(is_used=False)
    return render(request, 'coupon_list.html', {'coupons': coupons})

def apply_coupon(request, coupon_id):
    coupon = get_object_or_404(Coupon, id=coupon_id)
    coupon.apply_coupon()       
    return redirect('reservation_list')


class ReservationListView(ListView):
    model = Reservation
    context_object_name = 'reservations'
    template_name = 'reservation/reservation_list.html'
    ordering = ['-date', '-time']

    def get_queryset(self):
        # Obtener todas las reservas
        reservations = super().get_queryset().filter(usuario=self.request.user)
        # Actualizar el estado de todas las reservas confirmadas
        for reservation in reservations:
            if reservation.state == Reservation.StateChoices.PENDING or reservation.state == Reservation.StateChoices.CONFIRMED:
                reservation.refresh_state()
        return reservations

class ReservationDetailView(DetailView):
    model = Reservation
    context_object_name = 'reservation'
    template_name = 'reservation/reservation_detail.html'
    
    def get_object(self, queryset=None):
        try:
            reservation = super().get_object(queryset)
            reservation.refresh_state()
            return reservation
        except Reservation.DoesNotExist:
            return None
    
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        reservation = self.get_object()
        # Agregar información sobre las acciones posibles
        context['can_confirm'] = reservation.can_confirm()
        context['can_finish'] = reservation.can_finish()
        context['can_cancel'] = reservation.can_cancel()
        return context

# VISTAS PARA CREACIÓN DE RESERVAS (PROCESO DE 3 PASOS)

class ReservationCreateStep1View(View):
    """Paso 1: Selección de número de personas usando el template reserva.html"""
    
    def get(self, request):
        # Renderizar el template reserva.html
        return render(request, 'reservation/reserva.html')
    
    def post(self, request):
        # Procesar los datos enviados desde el formulario/JavaScript
        number_of_people = request.POST.get('number_of_people')
        
        if number_of_people and number_of_people.isdigit():
            # Guardar en sesión
            self.request.session['reservation_step1'] = {
                'number_of_people': int(number_of_people),
                'initial_state': Reservation.StateChoices.PENDING  # Inicializar estado como pendiente
            }
            return redirect('reservation_create_step2')
        else:
            # Si hay error, volver al formulario con un mensaje
            messages.error(request, 'Por favor, seleccione un número válido de personas')
            return render(request, 'reservation/reserva.html')

class ReservationCreateStep2View(View):
    """Paso 2: Selección de fecha (primera parte)"""
    template_name = 'reservation/calendario.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si se completó el paso 1
        if 'reservation_step1' not in request.session:
            return redirect('reservation_create_step1')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        # Crear formulario de fecha
        initial_data = {}  
        # Si hay datos en sesión, cargarlos en el formulario
        if 'reservation_step2' in request.session and 'date' in request.session['reservation_step2']:
            date_str = request.session['reservation_step2']['date']
            date_obj = datetime.fromisoformat(date_str).date() if date_str else None
            if date_obj:
                initial_data['date'] = date_obj
        
        form = ReservationDateForm(initial=initial_data)
        return render(request, self.template_name, {'form': form})
    
    def post(self, request):
        form = ReservationDateForm(request.POST)
        
        if form.is_valid():
            date = form.cleaned_data['date']
            
            # Guardar fecha en sesión
            if 'reservation_step2' not in request.session:
                request.session['reservation_step2'] = {}
            
            request.session['reservation_step2']['date'] = date.isoformat()
            
            # Redireccionar al siguiente paso (selección de hora)
            return redirect('reservation_create_step2_time')
        
        return render(request, self.template_name, {'form': form})

class ReservationCreateStep2TimeView(View):
    """Paso 2: Selección de hora (segunda parte)"""
    template_name = 'reservation/time.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si se completaron los pasos anteriores
        if 'reservation_step1' not in request.session:
            return redirect('reservation_create_step1')
        
        if 'reservation_step2' not in request.session or 'date' not in request.session['reservation_step2']:
            return redirect('reservation_create_step2')
            
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        # Obtener la fecha seleccionada
        date_str = request.session['reservation_step2']['date']
        date_obj = datetime.fromisoformat(date_str).date()

        # Obtener el número de personas del paso 1
        number_of_people = request.session['reservation_step1'].get('number_of_people')
        
        # Obtener hora actual si existe
        current_time = None
        if 'time' in request.session['reservation_step2']:
            current_time = request.session['reservation_step2']['time']
        
        # Crear instancia temporal para el formulario
        instance = None
        if current_time:
            instance = Reservation(time=current_time)
        
        # Crear formulario de hora
        form = ReservationTimeForm(
            selected_date=date_obj,
            instance=instance, 
            number_of_people=number_of_people
            )
        
        context = {
            'form': form,
            'selected_date': date_obj,
            'number_of_people': number_of_people
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Obtener la fecha seleccionada
        date_str = request.session['reservation_step2']['date']
        date_obj = datetime.fromisoformat(date_str).date()

        # Obtener el número de personas
        number_of_people = request.session['reservation_step1'].get('number_of_people')
        
        # Procesar formulario
        form = ReservationTimeForm(request.POST, selected_date=date_obj, number_of_people=number_of_people)
        
        if form.is_valid():
            time = form.cleaned_data['time']
            print(f"DEBUG - Guardando hora en sesión: {time}")
            
            # Guardar hora en sesión
            request.session['reservation_step2']['time'] = time
            print(f"DEBUG - Sesión después de guardar: {request.session['reservation_step2']}")
            
            # Modificar para que la sesión se guarde inmediatamente
            request.session.modified = True

            # Redireccionar al siguiente paso
            return redirect('reservation_create_step3')
        
        context = {
            'form': form,
            'selected_date': date_obj
        }
        return render(request, self.template_name, context)

class ReservationCreateStep3View(View):
    """Paso 3: Información de contacto y confirmación"""
    template_name = 'reservation/infoUser.html'
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si se completaron los pasos anteriores
        if 'reservation_step1' not in request.session or 'reservation_step2' not in request.session:
            return redirect('reservation_create_step1')
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request):
        # Obtener datos de los pasos anteriores
        step1_data = request.session.get('reservation_step1', {})
        step2_data = request.session.get('reservation_step2', {})
        
        # Crear formulario
        form = ReservationContactForm()
        
        # Si hay datos en sesión de una visita anterior, rellenar el formulario
        if 'reservation_step3' in request.session:
            instance = Reservation(
                name=request.session['reservation_step3'].get('name', ''),
                email=request.session['reservation_step3'].get('email', '')
            )
            form = ReservationContactForm(instance=instance)
        
        context = {
            'form': form,
            'number_of_people': step1_data.get('number_of_people'),
            'date': step2_data.get('date'),
            'time': step2_data.get('time'),
        }
        return render(request, self.template_name, context)
    
    def post(self, request):
        # Obtener datos de los pasos anteriores
        step1_data = request.session.get('reservation_step1', {})
        step2_data = request.session.get('reservation_step2', {})
        
        # Procesar el formulario
        form = ReservationContactForm(request.POST)
            # Validar que tengamos una hora válida antes de proceder
        time_str = step2_data.get('time')
        if not time_str:
            messages.error(request, 'No se ha seleccionado una hora válida. Por favor vuelva al paso anterior.')
            return redirect('reservation_create_step2_time')
        
        if form.is_valid():
            # Crear una reserva combinando todos los datos de los pasos
            from datetime import datetime
            
            date_str = step2_data.get('date')
            date_obj = datetime.fromisoformat(date_str).date() if date_str else None
            # Convertir el string de tiempo a un objeto time
            time_str = step2_data.get('time')
            time_obj = None
            if time_str:
                # El formato es 'HH:MM:SS'
                hour, minute, second = map(int, time_str.split(':'))
                time_obj = time(hour=hour, minute=minute, second=second)

            reservation = Reservation(
                name=form.cleaned_data['name'],
                email=form.cleaned_data['email'],
                number_of_people=step1_data.get('number_of_people'),
                date=date_obj,
                time=time_obj,
                state=Reservation.StateChoices.PENDING,
                usuario=request.user
            )
            reservation.save()

            
            # Limpiar datos de sesión
            if 'reservation_step1' in request.session:
                del request.session['reservation_step1']
            if 'reservation_step2' in request.session:
                del request.session['reservation_step2']
            if 'reservation_step3' in request.session:
                del request.session['reservation_step3']
            
            messages.success(request, 'Reserva creada con éxito. Estado: Pendiente')
            return redirect('reservation_list')
        
        # Si el formulario no es válido, volver a mostrar con errores
        context = {
            'form': form,
            'number_of_people': step1_data.get('number_of_people'),
            'date': step2_data.get('date'),
            'time': step2_data.get('time'),
        }
        return render(request, self.template_name, context)

# VISTAS PARA ACTUALIZACIÓN DE RESERVAS (PROCESO DE 3 PASOS)

class ReservationUpdateStep1View(View):  # Cambiamos de UpdateView a View
    """Paso 1: Actualizar número de personas"""
    template_name = 'reservation/reserva.html'  # Usar el mismo template que en creación
    
    def get(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Guardar ID en sesión para el flujo de edición
        request.session['editing_reservation_id'] = reservation.id
        
        # Pasar el valor actual para pre-seleccionar en la interfaz
        context = {
            'object': reservation,
            'initial_value': reservation.number_of_people
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Procesar los datos enviados desde el formulario
        number_of_people = request.POST.get('number_of_people')
        
        if number_of_people and number_of_people.isdigit():
            # Actualizar número de personas
            reservation.number_of_people = int(number_of_people)
            reservation.save()
            
            # Guardar ID en sesión para siguientes pasos
            request.session['editing_reservation_id'] = reservation.id
            
            # Redirigir al siguiente paso
            return redirect('reservation_update_step2', pk=reservation.id)
        else:
            # Si hay error, volver al formulario con un mensaje
            messages.error(request, 'Por favor, seleccione un número válido de personas')
            return render(request, self.template_name, {'object': reservation})

class ReservationUpdateStep2View(View):
    """Paso 2: Actualizar fecha (primera parte)"""
    template_name = 'reservation/calendario.html'  # Usar el mismo template que en creación
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si venimos del paso anterior o es edición directa
        reservation_id = kwargs.get('pk')
        session_id = request.session.get('editing_reservation_id')
        
        if session_id != reservation_id and session_id is not None:
            # Si el ID en sesión es distinto, redirigir al paso 1 con el ID correcto
            print("hola")
            return redirect('reservation_update_step1', pk=reservation_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Crear formulario con la fecha actual
        initial_data = {'date': reservation.date}
        form = ReservationDateForm(initial=initial_data)
        
        # Guardar datos temporales en sesión
        if 'editing_reservation_step2' not in request.session:
            request.session['editing_reservation_step2'] = {}
            
        request.session['editing_reservation_step2']['date'] = reservation.date.isoformat()
        
        return render(request, self.template_name, {'form': form, 'object': reservation})
    
    def post(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Procesar el formulario
        form = ReservationDateForm(request.POST)
        
        if form.is_valid():
            date = form.cleaned_data['date']
            
            # Guardar fecha en sesión
            if 'editing_reservation_step2' not in request.session:
                request.session['editing_reservation_step2'] = {}
                
            request.session['editing_reservation_step2']['date'] = date.isoformat()
            
            # Redireccionar al siguiente paso (selección de hora)
            return redirect('reservation_update_step2_time', pk=pk)
        
        return render(request, self.template_name, {'form': form, 'object': reservation})

class ReservationUpdateStep2TimeView(View):
    """Paso 2: Actualizar hora (segunda parte)"""
    template_name = 'reservation/time.html'  # Usar el mismo template que en creación
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si se completaron los pasos anteriores
        reservation_id = kwargs.get('pk')
        session_id = request.session.get('editing_reservation_id')
        
        if session_id != reservation_id:
            return redirect('reservation_update_step1', pk=reservation_id)
        
        if 'editing_reservation_step2' not in request.session or 'date' not in request.session['editing_reservation_step2']:
            return redirect('reservation_update_step2', pk=reservation_id)
            
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Obtener la fecha seleccionada
        date_str = request.session['editing_reservation_step2']['date']
        date_obj = datetime.fromisoformat(date_str).date()
        
        # Crear formulario de hora con la hora actual
        form = ReservationTimeForm(selected_date=date_obj, instance=reservation)
        
        context = {
            'form': form,
            'selected_date': date_obj,
            'object': reservation
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Obtener la fecha seleccionada
        date_str = request.session['editing_reservation_step2']['date']
        date_obj = datetime.fromisoformat(date_str).date()
        
        # Procesar formulario
        form = ReservationTimeForm(request.POST, selected_date=date_obj, instance=reservation)
        
        if form.is_valid():
            time_str = form.cleaned_data['time']
            
            # Convertir string de tiempo a objeto time
            hour, minute, second = map(int, time_str.split(':'))
            time_obj = time(hour=hour, minute=minute, second=second)
            
            # Actualizar la reserva con los nuevos valores
            reservation.date = date_obj
            reservation.time = time_obj  # Ahora sí es un objeto time
            reservation.save()
            
            # Redireccionar al siguiente paso
            return redirect('reservation_update_step3', pk=reservation.id)


class ReservationUpdateStep3View(View):
    """Paso 3: Actualizar información de contacto"""
    template_name = 'reservation/infoUser.html'  # Usar el mismo template que en creación
    
    def dispatch(self, request, *args, **kwargs):
        # Verificar si venimos del paso anterior o es edición directa
        reservation_id = kwargs.get('pk')
        session_id = request.session.get('editing_reservation_id')
        
        if session_id != reservation_id and session_id is not None:
            # Si el ID en sesión es distinto, redirigir al paso 1
            return redirect('reservation_update_step1', pk=reservation_id)
        
        return super().dispatch(request, *args, **kwargs)
    
    def get(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Crear formulario con los datos actuales de la reserva
        form = ReservationContactForm(instance=reservation)
        
        context = {
            'form': form,
            'object': reservation,
            'number_of_people': reservation.number_of_people,
            'date': reservation.date,
            'time': reservation.time,
        }
        return render(request, self.template_name, context)
    
    def post(self, request, pk):
        # Obtener la reserva existente
        reservation = get_object_or_404(Reservation, pk=pk)
        
        # Procesar el formulario
        form = ReservationContactForm(request.POST, instance=reservation)
        
        if form.is_valid():
            # Guardar el formulario
            form.save()
            
            # Limpiar datos de sesión
            if 'editing_reservation_id' in request.session:
                del request.session['editing_reservation_id']
            if 'editing_reservation_step2' in request.session:
                del request.session['editing_reservation_step2']
            
            messages.success(request, 'Reserva actualizada con éxito.')
            return redirect('reservation_list')
        
        # Si el formulario no es válido, volver a mostrar con errores
        context = {
            'form': form,
            'object': reservation,
            'number_of_people': reservation.number_of_people,
            'date': reservation.date,
            'time': reservation.time,
        }
        return render(request, self.template_name, context)

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
    reservation = get_object_or_404(Reservation, pk=pk, usuario=request.user)
    if reservation.cancel():
        messages.success(request, 'Reserva cancelada con éxito')
    else:
        messages.error(request, 'No se puede cancelar la reserva en su estado actual')
    return redirect('reservation_list')

