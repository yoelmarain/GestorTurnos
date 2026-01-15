from django.urls import path, include
from rest_framework import routers
from .views import TurnoView, ClienteView, ProfesionalView, ServicioView

router = routers.DefaultRouter()
router.register(r'turnos', TurnoView, basename='turno')
router.register(r'clientes', ClienteView, basename='cliente')
router.register(r'profesionales', ProfesionalView, basename='profesional')
router.register(r'servicios', ServicioView, basename='servicio')

urlpatterns = [
    path('', include(router.urls)),
]

