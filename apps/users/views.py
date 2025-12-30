"""
Views for User authentication and management.
"""
from rest_framework import status, viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.authtoken.models import Token

from .models import User
from .serializers import (
    UserRegistrationSerializer,
    UserLoginSerializer,
    UserSerializer,
    ChangePasswordSerializer
)


class UserViewSet(viewsets.ModelViewSet):
    """
    ViewSet for user registration, login, and profile management.
    """
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsAuthenticated]
    
    def get_permissions(self):
        """Allow unauthenticated users for registration and login."""
        if self.action in ['register', 'login']:
            return [AllowAny()]
        return super().get_permissions()
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def register(self, request):
        """
        User registration endpoint.
        Automatically creates a trainer profile for new users.
        
        POST /api/users/register/
        {
            "email": "trainer@example.com",
            "first_name": "John",
            "last_name": "Doe",
            "password": "securepassword123",
            "password_confirm": "securepassword123",
            "business_name": "John's Fitness Studio",
            "phone_number": "+1234567890"
        }
        """
        serializer = UserRegistrationSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.save()
            
            token, created = Token.objects.get_or_create(user=user)
            
            # Get trainer profile (created automatically in serializer)
            trainer = user.trainer_profile
            
            # Serialize user and trainer for response
            from apps.trainers.serializers import TrainerSerializer
            from .serializers import UserSerializer
            
            user_serializer = UserSerializer(user)
            trainer_serializer = TrainerSerializer(trainer)
            
            return Response({
                'user': user_serializer.data,
                'trainer': trainer_serializer.data,
                'token': token.key
            }, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[AllowAny])
    def login(self, request):
        """
        User login endpoint.
        
        POST /api/users/login/
        {
            "email": "trainer@example.com",
            "password": "securepassword123"
        }
        """
        serializer = UserLoginSerializer(data=request.data)
        if serializer.is_valid():
            user = serializer.validated_data['user']
            token, created = Token.objects.get_or_create(user=user)
            
            # Get trainer profile if exists
            trainer_data = None
            try:
                trainer = user.trainer_profile
                from apps.trainers.serializers import TrainerSerializer
                trainer_serializer = TrainerSerializer(trainer)
                trainer_data = trainer_serializer.data
            except:
                pass
            
            from .serializers import UserSerializer
            user_serializer = UserSerializer(user)
            
            return Response({
                'user': user_serializer.data,
                'trainer': trainer_data,
                'token': token.key
            }, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def logout(self, request):
        """
        User logout endpoint (delete token).
        
        POST /api/users/logout/
        """
        try:
            request.user.auth_token.delete()
        except:
            pass
        return Response({'message': 'Logged out successfully'}, status=status.HTTP_200_OK)
    
    @action(detail=False, methods=['get', 'patch'], permission_classes=[IsAuthenticated])
    def me(self, request):
        """
        Get or update current user profile.
        
        GET /api/users/me/
        PATCH /api/users/me/
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "+1234567890"
        }
        """
        if request.method == 'PATCH':
            user = request.user
            serializer = self.get_serializer(user, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                user_serializer = self.get_serializer(user)
                
                # Include trainer profile if exists
                trainer_data = None
                try:
                    trainer = user.trainer_profile
                    from apps.trainers.serializers import TrainerSerializer
                    trainer_serializer = TrainerSerializer(trainer)
                    trainer_data = trainer_serializer.data
                except:
                    pass
                
                return Response({
                    'user': user_serializer.data,
                    'trainer': trainer_data
                })
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        else:
            user_serializer = self.get_serializer(request.user)
            
            # Include trainer profile if exists
            trainer_data = None
            try:
                trainer = request.user.trainer_profile
                from apps.trainers.serializers import TrainerSerializer
                trainer_serializer = TrainerSerializer(trainer)
                trainer_data = trainer_serializer.data
            except:
                pass
            
            return Response({
                'user': user_serializer.data,
                'trainer': trainer_data
            })
    
    @action(detail=False, methods=['post'], permission_classes=[IsAuthenticated])
    def change_password(self, request):
        """
        Change user password.
        
        POST /api/users/change-password/
        {
            "old_password": "currentpassword",
            "new_password": "newpassword123",
            "new_password_confirm": "newpassword123"
        }
        """
        serializer = ChangePasswordSerializer(
            data=request.data,
            context={'request': request}
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                {'message': 'Password changed successfully'},
                status=status.HTTP_200_OK
            )
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=False, methods=['patch'], permission_classes=[IsAuthenticated])
    def update_profile(self, request):
        """
        Update user profile.
        
        PATCH /api/users/update-profile/
        {
            "first_name": "Jane",
            "last_name": "Smith",
            "phone_number": "+1234567890"
        }
        """
        user = request.user
        serializer = self.get_serializer(user, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
