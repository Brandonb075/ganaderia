from django import forms
from .models import *

# Formulario para cargar una imagen
class ImageUploadForm(forms.Form):
    image = forms.ImageField()

class VendedorForm(forms.ModelForm):
    class Meta:
        model = Vendedor
        fields = ['nombre', 'dni', 'telefono', 'direccion', 'correo', 'finca']

class FincaForm(forms.ModelForm):
    class Meta:
        model = Finca
        fields = ['nombre', 'direccion', 'tamano', 'propietario', 'telefono']