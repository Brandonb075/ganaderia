from PIL import Image
import pytesseract
from PyPDF2 import PdfReader

def analizar_imagen(file):
    # Lógica básica para imágenes
    if file.content_type.startswith('image'):
        # Usar PIL y pytesseract para el análisis de la imagen
        image = Image.open(file)
        texto = pytesseract.image_to_string(image)
        resultado = "Imagen procesada"
        porcentaje = 95  # Aquí puedes ajustar el porcentaje de similitud
    elif file.content_type == 'application/pdf':
        # Procesar PDF (por ejemplo, extraer texto)
        reader = PdfReader(file)
        texto_pdf = ''
        for page in reader.pages:
            texto_pdf += page.extract_text()
        resultado = "PDF procesado"
        porcentaje = 80  # Ajusta según sea necesario
    else:
        resultado = "Tipo de archivo no soportado"
        porcentaje = 0
    
    return resultado, porcentaje
