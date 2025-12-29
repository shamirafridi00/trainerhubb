from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated

from .models import SessionPackage, ClientPackage
from .serializers import SessionPackageSerializer, ClientPackageSerializer
from apps.trainers.models import Trainer


class SessionPackageViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing session packages.
    """
    serializer_class = SessionPackageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only packages for current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return SessionPackage.objects.filter(trainer=trainer)
        except Trainer.DoesNotExist:
            return SessionPackage.objects.none()
    
    def perform_create(self, serializer):
        """Create package for current trainer."""
        trainer = self.request.user.trainer_profile
        serializer.save(trainer=trainer)
    
    @action(detail=True, methods=['post'], url_path='assign-to-client')
    def assign_to_client(self, request, pk=None):
        """
        Assign package to a client.
        
        POST /api/packages/{id}/assign-to-client/
        {
            "client_id": 1,
            "expiry_date": "2025-12-31"
        }
        """
        package = self.get_object()
        client_id = request.data.get('client_id')
        expiry_date = request.data.get('expiry_date')
        
        if not client_id:
            return Response(
                {'error': 'client_id is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Check if client belongs to this trainer
        if not package.trainer.clients.filter(id=client_id).exists():
            return Response(
                {'error': 'Client not found for this trainer'},
                status=status.HTTP_404_NOT_FOUND
            )
        
        client = package.trainer.clients.get(id=client_id)
        
        client_package = ClientPackage.objects.create(
            client=client,
            session_package=package,
            sessions_remaining=package.sessions_count,
            expiry_date=expiry_date
        )
        
        serializer = ClientPackageSerializer(client_package)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    
    @action(detail=True, methods=['get'], url_path='client-packages')
    def client_packages(self, request, pk=None):
        """
        Get all client packages for this package.
        
        GET /api/packages/{id}/client-packages/
        """
        package = self.get_object()
        client_packages = package.client_packages.all()
        serializer = ClientPackageSerializer(client_packages, many=True)
        return Response(serializer.data)


class ClientPackageViewSet(viewsets.ReadOnlyModelViewSet):
    """
    ViewSet for viewing client packages.
    Read-only except for use_session action.
    """
    serializer_class = ClientPackageSerializer
    permission_classes = [IsAuthenticated]
    
    def get_queryset(self):
        """Get only packages for clients of current trainer."""
        try:
            trainer = self.request.user.trainer_profile
            return ClientPackage.objects.filter(
                client__trainer=trainer
            ).select_related('client', 'session_package')
        except Trainer.DoesNotExist:
            return ClientPackage.objects.none()
    
    @action(detail=True, methods=['post'], url_path='use-session')
    def use_session(self, request, pk=None):
        """
        Use one session from a package.
        
        POST /api/client-packages/{id}/use-session/
        """
        package = self.get_object()
        
        if package.sessions_remaining <= 0:
            return Response(
                {'error': 'No sessions remaining'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if package.is_expired:
            return Response(
                {'error': 'Package has expired'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        package.sessions_remaining -= 1
        package.save()
        
        serializer = self.get_serializer(package)
        return Response(serializer.data)
