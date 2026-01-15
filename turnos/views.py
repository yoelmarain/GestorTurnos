from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Turno, Cliente, Profesional, Servicio
from .serializer import TurnoSerializer, ClienteSerializer, ProfesionalSerializer, ServicioSerializer

# Create your views here.
# La vista no se mete con los modelos en un POST, si en un GET (ahi ella llama al modelo para obtener datos y al seria para transformarlos)

class TurnoView(viewsets.ModelViewSet):
    queryset = Turno.objects.all()   #Para obtener todos los turnos para responder un GET
    serializer_class = TurnoSerializer #Para transformar y validar los datos del modelo a JSON y viceversa

class ClienteView(viewsets.ModelViewSet):
    queryset = Cliente.objects.all()
    serializer_class = ClienteSerializer

class ProfesionalView(viewsets.ModelViewSet):
    queryset = Profesional.objects.all()
    serializer_class = ProfesionalSerializer

class ServicioView(viewsets.ModelViewSet):
    queryset = Servicio.objects.all()
    serializer_class = ServicioSerializer

    #action convierte un metodo en un endpoint
    #Detail True es cuando se requiere un ID en la peticion, ira dsp de la primer parte de la ruta
    #methods define que metodos HTTP acepta este endpoint
    @action(detail=True, methods=['get'])  
    #El nombre del metodo define lo que va en la ultima parte de la ruta  
    #request es un objeto que contiene toda la info de la peticion
    #pk es el id que viene en la url, que por defecto aca pone None pero siempre va a tener algo cuando detail=True
    def profesionales(self, request, pk=None):
        """
        Devuelve todos los profesionales que realizan este servicio
        """
        #obtener el objeto servicio actual, toma el pk de la url y lo busca en la bbdd
        servicio = self.get_object() #o servicio = Servicio.objects.get(pk=pk)
        #acedde a la relacion Many to many por definir related_name="profesionales, este permite desde un servicio acceder a sus profesionales
        profesionales = servicio.profesionales.all()
        #serializa los datos de python a json
        #el many es importante para indicar que se va a serializar una lista de objetos, sino serializa uno solo
        serializer = ProfesionalSerializer(profesionales, many=True)
        #La clase response crea una respuesta HTTP
        return Response(serializer.data)
