from django.urls import path
from . import views

urlpatterns = [
    path('', views.inicio, name='inicio'),
    path('home', views.home, name='home'),
    path('analizar/', views.analizar_imagen, name='analizar_imagen'),
     # Vistas para Finca
    path('finca/ingresar/', views.finca_ingreso, name='ingresar_finca'),
    path('finca/listado/', views.finca_listado, name='listar_fincas'),
    path('finca/editar/<int:finca_id>/', views.finca_editar, name='editar_finca'),

    # Vistas para Vendedor
    path('vendedor/ingresar/', views.vendedor_ingreso, name='ingresar_vendedor'),
    path('vendedor/listado/', views.vendedor_listado, name='listar_vendedores'),
    path('vendedor/editar/<int:vendedor_id>/', views.vendedor_editar, name='editar_vendedor'),

    path('generar_pdf_vendedor/<int:vendedor_id>/', views.generar_pdf_vendedor, name='generar_pdf_vendedor'),
    path('generar_pdf_finca/<int:finca_id>/', views.generar_pdf_finca, name='generar_pdf_finca'),
]
