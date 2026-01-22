from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta, datetime, time
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

    @action(detail=True, methods=['get'])
    def turnos(self, request, pk=None):
        """
        Devuelve todos los turnos de un cliente específico
        """
        cliente = self.get_object()  #obtiene el cliente actual segun el pk
        turnos = Turno.objects.filter(cliente=cliente)  #filtra los turnos por el cliente actual
        serializer = TurnoSerializer(turnos, many=True)  #serializa la lista de turnos
        return Response(serializer.data)  #devuelve la respuesta con los datos serializados

class ProfesionalView(viewsets.ModelViewSet):
    queryset = Profesional.objects.all()
    serializer_class = ProfesionalSerializer

    #con urlpath se puede personalizar la ruta del endpoint
    @action(detail=False, methods=['get'], url_path='(?P<profesional_id>[^/.]+)/turnosLibres/(?P<servicio_id>[^/.]+)')
    def turnosLibres(self, request, profesional_id=None, servicio_id=None):   #se agrega los nombres de la url como parametros del metodo
        """
        Devuelve todos los turnos libres de un profesional para un servicio específico
        URL: /profesionales/profesional_id/turnosLibres/servicio_id
        """
        try:
            profesional = Profesional.objects.get(pk=profesional_id)
            servicio = Servicio.objects.get(pk=servicio_id)
        except Profesional.DoesNotExist:
            return Response({'error': 'Profesional no encontrado'}, status=404)
        except Servicio.DoesNotExist:
            return Response({'error': 'Servicio no encontrado'}, status=404)
        
# Obtener turnos reservados del profesional con el servicio específico
        turnos_reservados = profesional.turnos.filter(
            estado='Reservado'
        )
        
        fecha_hoy = timezone.now()
        fecha_limite = fecha_hoy + timedelta(days=7)
        duracion_minutos = servicio.duracion_minutos
        
        # Horario laboral (puedes ajustar estos valores)
        hora_inicio = time(9, 0)  # 9:00 AM
        hora_fin = time(18, 0)    # 6:00 PM
        intervalo_minutos = duracion_minutos  # Slots según la duración del servicio
        
        slots_disponibles = []
        
        # Iterar por cada día desde hoy hasta una semana
        dia_actual = fecha_hoy.date()
        while dia_actual <= fecha_limite.date():
            # Generar slots para el día actual (con zona horaria)
            hora_slot = timezone.make_aware(datetime.combine(dia_actual, hora_inicio))  #combina la fecha del dia actual con la hora de inicio
            hora_final_dia = timezone.make_aware(datetime.combine(dia_actual, hora_fin)) #combina la fecha del dia actual con la hora de fin
            
            #bucle interno para recorrer un dia
            while hora_slot < hora_final_dia:
                slot_end = hora_slot + timedelta(minutes=intervalo_minutos)  #guarda fecha y hora del fin del slot
                
                # Verificar si este slot NO está reservado
                slot_ocupado = False
                for turno in turnos_reservados:   #recorre los turnos reservados del profesional
                    turno_inicio = turno.fecha_turno
                    turno_fin = turno.fecha_turno + timedelta(minutes=duracion_minutos)
                    
                    # Verificar si hay solapamiento
                    if (hora_slot < turno_fin and slot_end > turno_inicio):
                        slot_ocupado = True
                        break
                
                # Si el slot no está ocupado y es posterior a la hora actual, agregarlo
                if not slot_ocupado and hora_slot >= fecha_hoy:
                    slots_disponibles.append({
                        "start": hora_slot.isoformat(),
                        "end": slot_end.isoformat()
                    })
                
                # Avanzar al siguiente slot
                hora_slot = slot_end
            
            # Avanzar al siguiente día
            dia_actual += timedelta(days=1)
        
        return Response({
            'profesional_id': profesional_id,
            'servicio_id': servicio_id,
            'slots_disponibles': slots_disponibles
        })


        
       


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
