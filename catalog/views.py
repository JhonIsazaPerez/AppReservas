from django.shortcuts import render
from .models import Producto
from django.template.loader import get_template
from django.http import HttpResponse
from xhtml2pdf import pisa
from .models import Producto

def lista_productos(request):
    productos = Producto.objects.filter(disponible=True)
    return render(request, 'lista_productos.html', {'productos': productos})


def descargar_productos_pdf(request):

    productos = Producto.objects.filter(disponible=True)
    template = get_template('pdf_productos.html')
    html = template.render({'productos': productos, 'base_url': request.build_absolute_uri('/')})
    
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = 'attachment; filename="productos.pdf"'
    
    pisa_status = pisa.CreatePDF(html, dest=response)
    if pisa_status.err:
        return HttpResponse("Error al generar PDF", status=500)
    
    return response
