from django.shortcuts import render

def reserva(request):
    return render(request, 'reserva.html')