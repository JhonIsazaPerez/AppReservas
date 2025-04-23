from django.shortcuts import render, redirect
from django.http import JsonResponse
import json

# Vista para guardar datos en la sesión a través de JavaScript (fetch)
def guardarDatos(request):
    if request.method == 'POST':
        datos = json.loads(request.body)  # Procesa los datos enviados desde JavaScript
        # Guardar número de personas, fecha y hora en la sesión
        if 'numero_personas' in datos:
            request.session['numero_personas'] = datos['numero_personas']
        if 'fecha' in datos:
            request.session['fecha'] = datos['fecha']
        if 'hora' in datos:
            request.session['hora'] = datos['hora']

        return JsonResponse({'mensaje': 'Datos guardados correctamente'})
    return JsonResponse({'error': 'Método no permitido'}, status=405)

# Vista para la página de selección de número de personas
def reserva(request):
        
    return render(request, 'reserva.html')  # Renderiza la plantilla de reservas

# Vista para la página de selección de fecha
def calendario(request):
    if request.method == 'POST':  # Si el formulario se envía con POST
        fecha = request.POST.get('fecha')  # Obtiene el valor del formulario
        request.session['fecha'] = fecha  # Guarda el dato en la sesión
        return redirect('hora')  # Redirige a la vista de selección de hora
    return render(request, 'calendario.html')  # Renderiza la plantilla del calendario

# Vista para la página de selección de hora
def hora(request):
    if request.method == 'POST':  # Si el formulario se envía con POST
        hora = request.POST.get('hora')  # Obtiene el valor del formulario
        request.session['hora'] = hora  # Guarda el dato en la sesión
        return redirect('resumen')  # Redirige a la vista del resumen
    return render(request, 'hora.html')  # Renderiza la plantilla de selección de hora


def infoUser(request):
    numero_personas = request.session.get('numero_personas', 'No especificado')
    fecha = request.session.get('fecha', 'No especificada')
    hora = request.session.get('hora', 'No especificada')
    print(request.session)  # Imprime la sesión en la consola para depuración
    return render(request, 'infoUser.html', {
        'numero_personas': numero_personas,
        'fecha': fecha,
        'hora': hora
    })