# views.py
from .models import *
from .forms import *
from django.shortcuts import render, redirect
from django.http import HttpResponse
from django.conf import settings
import os
import cv2
import numpy as np
from skimage.metrics import structural_similarity as ssim
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# Función para verificar si la imagen de referencia existe
def verificar_imagen_referencia():
    ruta_imagen_referencia = os.path.join(settings.MEDIA_ROOT, 'uploads', 'reference_image.jpg')
    if not os.path.exists(ruta_imagen_referencia):
        return False, "La imagen de referencia no existe."
    return True, ruta_imagen_referencia

def comparar_imagenes_ssim(imagen1_path, imagen2_path):
    # Cargar las imágenes en escala de grises
    imagen1 = cv2.imread(imagen1_path, cv2.IMREAD_GRAYSCALE)
    imagen2 = cv2.imread(imagen2_path, cv2.IMREAD_GRAYSCALE)

    # Asegúrate de que las imágenes tienen el mismo tamaño
    if imagen1.shape != imagen2.shape:
        raise ValueError("Las imágenes deben tener el mismo tamaño")

    # Calcular el índice SSIM
    similitud, _ = ssim(imagen1, imagen2, full=True)
    return similitud

def comparar_imagenes_histograma(imagen1_path, imagen2_path):
    # Cargar las imágenes
    imagen1 = cv2.imread(imagen1_path)
    imagen2 = cv2.imread(imagen2_path)

    # Convertir las imágenes a escala de grises
    imagen1_gray = cv2.cvtColor(imagen1, cv2.COLOR_BGR2GRAY)
    imagen2_gray = cv2.cvtColor(imagen2, cv2.COLOR_BGR2GRAY)

    # Calcular los histogramas de las imágenes
    hist1 = cv2.calcHist([imagen1_gray], [0], None, [256], [0, 256])
    hist2 = cv2.calcHist([imagen2_gray], [0], None, [256], [0, 256])

    # Normalizar los histogramas
    hist1 /= hist1.sum()
    hist2 /= hist2.sum()

    # Calcular la distancia entre los histogramas usando correlación
    similitud = cv2.compareHist(hist1, hist2, cv2.HISTCMP_CORREL)
    return similitud

# Función para comparar las imágenes (SSIM, Histograma y HOG)
def comparar_imagenes(ruta_imagen_subida, ruta_imagen_referencia):
    # Cargar las imágenes usando OpenCV
    img_subida = cv2.imread(ruta_imagen_subida)
    img_referencia = cv2.imread(ruta_imagen_referencia)

    # Verificar si las imágenes se cargaron correctamente
    if img_subida is None or img_referencia is None:
        raise ValueError("Error al cargar las imágenes.")

    # Redimensionar las imágenes a un tamaño común para evitar discrepancias
    img_subida_resized = cv2.resize(img_subida, (256, 256))
    img_referencia_resized = cv2.resize(img_referencia, (256, 256))

    # Convertir las imágenes a escala de grises para SSIM
    img_subida_gray = cv2.cvtColor(img_subida_resized, cv2.COLOR_BGR2GRAY)
    img_referencia_gray = cv2.cvtColor(img_referencia_resized, cv2.COLOR_BGR2GRAY)

    # Comparar la similitud estructural usando SSIM
    similitud_ssim, _ = ssim(img_subida_gray, img_referencia_gray, full=True)

    # Histograma de color (usando histograma de 3 canales: R, G, B)
    hist_subida = cv2.calcHist([img_subida_resized], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
    hist_referencia = cv2.calcHist([img_referencia_resized], [0, 1, 2], None, [256, 256, 256], [0, 256, 0, 256, 0, 256])
    
    # Normalizar los histogramas
    hist_subida /= hist_subida.sum()
    hist_referencia /= hist_referencia.sum()

    # Comparar los histogramas usando la distancia de Chi-cuadrado
    distancia_histograma = cv2.compareHist(hist_subida, hist_referencia, cv2.HISTCMP_CHISQR)

    # Normalizar el valor del histograma
    similitud_histograma = max(0, 1 - distancia_histograma / 300)  # Ajuste de escala para la similitud

    # Características HOG
    hog = cv2.HOGDescriptor()
    descriptor_subida = hog.compute(img_subida_resized)
    descriptor_referencia = hog.compute(img_referencia_resized)

    # Comparar las características HOG usando la distancia Euclidiana
    distancia_hog = np.linalg.norm(descriptor_subida - descriptor_referencia)
    similitud_hog = max(0, 1 - distancia_hog / 1000)  # Ajuste de escala

    # Promedio de similitudes
    similitud_promedio = (similitud_ssim + similitud_histograma + similitud_hog) / 3

    # Retornar solo el valor de similitud promedio
    return similitud_promedio


# Vista para manejar la carga de imagen y análisis
def analizar_imagen(request):
    if request.method == 'POST' and request.FILES.get('imagen'):
        # Guardar la imagen subida
        imagen_subida = request.FILES['imagen']
        ruta_imagen_subida = os.path.join(settings.MEDIA_ROOT, 'uploads', imagen_subida.name)
        with open(ruta_imagen_subida, 'wb+') as destino:
            for chunk in imagen_subida.chunks():
                destino.write(chunk)

        # Verificar la imagen de referencia
        imagen_referencia_valida, resultado_referencia = verificar_imagen_referencia()

        if not imagen_referencia_valida:
            return HttpResponse(resultado_referencia, status=404)  # Devuelve error si no se encuentra la imagen de referencia

        # Si la imagen de referencia está cargada correctamente, continuar con la comparación
        ruta_imagen_referencia = resultado_referencia

        try:
            # Comparar las imágenes usando la función global para SSIM, Histograma y HOG
            similitud_promedio = comparar_imagenes(ruta_imagen_subida, ruta_imagen_referencia)

            # Pasar los resultados a la plantilla
            return render(request, 'resultado_analisis.html', {
                'porcentaje_similitud': round(similitud_promedio * 100, 2),
                'imagen_subida': f"/media/uploads/{imagen_subida.name}",
                'imagen_muestra': "/media/uploads/reference_image.jpg"
            })
        except ValueError as e:
            return HttpResponse(f"Error al analizar las imágenes: {str(e)}", status=500)

    else:
        return HttpResponse("Método no permitido", status=405)

############################################################################################################3

# Vista principal (home)
def home(request):
    return render(request, 'home.html')

def inicio(request):
    return render(request, 'inicio.html')


#############################################################################################################

def finca_ingreso(request):
    if request.method == 'POST':
        form = FincaForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_fincas')
    else:
        form = FincaForm()
    return render(request, 'Finca_ingreso.html', {'form': form})

# Vista para ver el listado de fincas
def finca_listado(request):
    fincas = Finca.objects.all()
    return render(request, 'Finca_listado.html', {'fincas': fincas})

# Vista para editar una finca existente
def finca_editar(request, finca_id):
    finca = Finca.objects.get(id=finca_id)
    if request.method == 'POST':
        form = FincaForm(request.POST, instance=finca)
        if form.is_valid():
            form.save()
            return redirect('listar_fincas')
    else:
        form = FincaForm(instance=finca)
    return render(request, 'Finca_editar.html', {'form': form})



############################################################################################################

# Vista para ingresar un nuevo vendedor
def vendedor_ingreso(request):
    if request.method == 'POST':
        form = VendedorForm(request.POST)
        if form.is_valid():
            form.save()
            return redirect('listar_vendedores')
    else:
        form = VendedorForm()
    return render(request, 'Vendedor_ingreso.html', {'form': form})

# Vista para ver el listado de vendedores
def vendedor_listado(request):
    vendedores = Vendedor.objects.all()
    return render(request, 'Vendedor_listado.html', {'vendedores': vendedores})

# Vista para editar un vendedor existente
def vendedor_editar(request, vendedor_id):
    vendedor = Vendedor.objects.get(id=vendedor_id)
    if request.method == 'POST':
        form = VendedorForm(request.POST, instance=vendedor)
        if form.is_valid():
            form.save()
            return redirect('listar_vendedores')
    else:
        form = VendedorForm(instance=vendedor)
    return render(request, 'Vendedor_editar.html', {'form': form})



##############################################################################################################
def generar_pdf_vendedor(request, vendedor_id):
    # Obtener los datos del vendedor
    vendedor = Vendedor.objects.get(id=vendedor_id)

    # Crear la respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="vendedor_{vendedor_id}.pdf"'

    # Crear el PDF
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Establecer las dimensiones de la página

    # Estilo del PDF
    c.setFont("Helvetica", 12)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 40, "Datos del Vendedor")

    # Datos del vendedor
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Nombre: {vendedor.nombre}")
    c.drawString(50, height - 100, f"Correo: {vendedor.correo}")
    c.drawString(50, height - 120, f"Teléfono: {vendedor.telefono}")
    c.drawString(50, height - 140, f"Finca: {vendedor.finca.nombre}")

    # Guardar el PDF
    c.showPage()
    c.save()

    return response


def generar_pdf_finca(request, finca_id):
    # Obtener los datos de la finca
    finca = Finca.objects.get(id=finca_id)

    # Crear la respuesta HTTP con el tipo de contenido de PDF
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="finca_{finca_id}.pdf"'

    # Crear el PDF
    c = canvas.Canvas(response, pagesize=letter)
    width, height = letter  # Establecer las dimensiones de la página

    # Estilo del PDF
    c.setFont("Helvetica", 12)

    # Título
    c.setFont("Helvetica-Bold", 16)
    c.drawString(200, height - 40, "Datos de la Finca")

    # Datos de la finca
    c.setFont("Helvetica", 12)
    c.drawString(50, height - 80, f"Nombre: {finca.nombre}")
    c.drawString(50, height - 100, f"Ubicación: {finca.direccion}") 
    c.drawString(50, height - 120, f"Área: {finca.tamano} hectáreas")

    # Guardar el PDF
    c.showPage()
    c.save()

    return response
