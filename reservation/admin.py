from django.contrib import admin
from .models import Reservation

class ReservationAdmin(admin.ModelAdmin):
    list_display = ('name', 'date', 'time', 'number_of_people', 'state', 'created_at')
    list_filter = ('state', 'date')
    search_fields = ('name', 'phone_number')
    date_hierarchy = 'date'
    
    actions = ['make_confirmed', 'make_finished', 'make_cancelled']
    
    def make_confirmed(self, request, queryset):
        for reservation in queryset:
            reservation.confirm()
    make_confirmed.short_description = "Marcar reservas seleccionadas como confirmadas"
    
    def make_finished(self, request, queryset):
        for reservation in queryset:
            reservation.finish()
    make_finished.short_description = "Marcar reservas seleccionadas como finalizadas"
    
    def make_cancelled(self, request, queryset):
        for reservation in queryset:
            reservation.cancel()
    make_cancelled.short_description = "Marcar reservas seleccionadas como canceladas"

admin.site.register(Reservation, ReservationAdmin)
