from rest_framework import serializers, viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import FCMDevice


class FCMDeviceSerializer(serializers.ModelSerializer):
    class Meta:
        model = FCMDevice
        fields = ('id', 'registration_id', 'tipo_dispositivo', 'nombre', 'activo')


class FCMDeviceViewSet(viewsets.ModelViewSet):
    queryset = FCMDevice.objects.all()
    serializer_class = FCMDeviceSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        perfil = getattr(self.request.user, 'perfil', None)
        if not perfil:
            return FCMDevice.objects.none()
        return FCMDevice.objects.filter(usuario=perfil)

    def perform_create(self, serializer):
        perfil = getattr(self.request.user, 'perfil', None)
        serializer.save(usuario=perfil)

    @action(detail=False, methods=['post'])
    def registrar(self, request):
        perfil = getattr(request.user, 'perfil', None)
        token = request.data.get('registration_id')
        tipo = request.data.get('tipo_dispositivo', 'web')
        nombre = request.data.get('nombre')
        if not token or not perfil:
            return Response({'error': 'registration_id y autenticación requeridos'}, status=400)
        obj, creado = FCMDevice.objects.update_or_create(
            registration_id=token,
            defaults={'usuario': perfil, 'tipo_dispositivo': tipo, 'nombre': nombre, 'activo': True}
        )
        return Response({'creado': creado})
