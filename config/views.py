"""
API root view for TrainerHub
"""
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import AllowAny
from rest_framework.response import Response


@api_view(['GET'])
@permission_classes([AllowAny])
def api_root(request):
    """
    TrainerHub API Root - Welcome endpoint
    """
    return Response({
        'message': 'Welcome to TrainerHub API',
        'version': '1.0.0',
        'status': 'running',
        'endpoints': {
            'authentication': {
                'register': '/api/users/register/',
                'login': '/api/users/login/',
                'logout': '/api/users/logout/',
                'profile': '/api/users/me/',
                'change_password': '/api/users/change-password/',
                'update_profile': '/api/users/update-profile/',
            },
            'admin': '/admin/',
            'documentation': '/api/',
        },
        'documentation': {
            'github': 'https://github.com/shamirafridi00/trainerhubb',
            'postman': 'Coming soon',
        }
    })

