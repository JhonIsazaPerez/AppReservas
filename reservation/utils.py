from django.core.mail import send_mail
from django.conf import settings

def send_reservation_email(reservation):
    subject = f"Estado actualizado: {reservation.state.title()}"
    message = f"""
    Hola {reservation.name},

    Tu reserva ha cambiado a: {reservation.state.title()}.

    Detalles:
    - Fecha: {reservation.date}
    - Hora: {reservation.time}
    - Personas: {reservation.number_of_people}

    Gracias por confiar en nuestro servicio.
    """

    send_mail(
        subject,
        message,
        settings.DEFAULT_FROM_EMAIL,
        [reservation.email],
        fail_silently=False
    )