from django.shortcuts import render, get_object_or_404, redirect
from django.contrib import messages
from django.views.generic import ListView, DetailView, CreateView, UpdateView
from django.contrib.auth.mixins import LoginRequiredMixin
from django.urls import reverse_lazy
from django.http import JsonResponse
from .models import Reservation

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

class ReservationCreateView(CreateView):
    model = Reservation
    fields = ['name', 'phone_number', 'date', 'time', 'number_of_people']
    template_name = 'reservation/reservation_form.html'
    success_url = reverse_lazy('reservation_list')

    def form_valid(self, form):
        messages.success(self.request, 'Reserva creada con éxito. Estado: Pendiente')
        return super().form_valid(form)

class ReservationUpdateView(UpdateView):
    model = Reservation
    fields = ['name', 'phone_number', 'date', 'time', 'number_of_people']
    template_name = 'reservation/reservation_form.html'
    success_url = reverse_lazy('reservation_list')

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
def api_change_state(request, pk):
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
