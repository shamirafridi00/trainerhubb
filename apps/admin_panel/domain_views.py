"""
Domain Management Views for Admin Panel
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.utils import timezone
from datetime import timedelta

from .domain_models import CustomDomain, DomainVerificationLog
from .domain_serializers import (
    CustomDomainSerializer,
    DomainVerificationLogSerializer,
    DomainApprovalSerializer,
    DomainVerifySerializer
)
from .domain_verification import DomainVerifier, SSLProvisioner, generate_verification_token
from .permissions import IsSuperUser
from .utils import log_admin_action


class DomainAdminViewSet(viewsets.ModelViewSet):
    """
    Admin endpoints for domain management.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]
    queryset = CustomDomain.objects.select_related(
        'trainer', 'trainer__user', 'approved_by'
    ).all()
    serializer_class = CustomDomainSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List all custom domains with filters.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by status
        status_filter = request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        # Filter by verification status
        verified = request.query_params.get('verified')
        if verified is not None:
            if verified.lower() == 'true':
                queryset = queryset.filter(dns_verified_at__isnull=False)
            else:
                queryset = queryset.filter(dns_verified_at__isnull=True)
        
        # Filter by SSL status
        ssl_status = request.query_params.get('ssl_status')
        if ssl_status:
            queryset = queryset.filter(ssl_status=ssl_status)
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def verify(self, request, pk=None):
        """
        Manually trigger domain verification.
        
        POST /api/admin/domains/{id}/verify/
        {
            "force": false
        }
        """
        domain = self.get_object()
        serializer = DomainVerifySerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        force = serializer.validated_data.get('force', False)
        
        # Check if already verified
        if domain.is_verified and not force:
            return Response({
                'status': 'already_verified',
                'message': 'Domain is already verified. Use force=true to re-verify.'
            })
        
        # Perform verification
        verifier = DomainVerifier(domain.domain, domain.verification_token)
        success, message, details = verifier.verify_domain(domain.verification_method)
        
        # Update domain
        domain.last_verification_attempt = timezone.now()
        domain.verification_attempts += 1
        
        if success:
            domain.mark_verified()
            domain.status = 'provisioning_ssl'
            domain.save()
            
            # Log successful verification
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='dns',
                status='success',
                details=details
            )
            
            # Log admin action
            log_admin_action(
                admin_user=request.user,
                action='approve_domain',
                target_trainer=domain.trainer,
                details={'domain': domain.domain, 'action': 'verify'},
                request=request
            )
            
            return Response({
                'status': 'verified',
                'message': message,
                'details': details,
                'next_step': 'SSL provisioning'
            })
        else:
            domain.save()
            
            # Log failed verification
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='dns',
                status='failed',
                error_message=message,
                details=details
            )
            
            return Response({
                'status': 'failed',
                'message': message,
                'details': details,
                'attempts': domain.verification_attempts
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def provision_ssl(self, request, pk=None):
        """
        Manually trigger SSL provisioning.
        
        POST /api/admin/domains/{id}/provision-ssl/
        """
        domain = self.get_object()
        
        # Check if DNS is verified
        if not domain.is_verified:
            return Response({
                'error': 'Domain must be DNS verified before SSL provisioning'
            }, status=status.HTTP_400_BAD_REQUEST)
        
        # Provision SSL
        provisioner = SSLProvisioner(domain.domain)
        success, message, details = provisioner.provision_certificate()
        
        if success:
            domain.ssl_status = 'provisioned'
            domain.ssl_provisioned_at = timezone.now()
            
            # Set expiry (Let's Encrypt certs are valid for 90 days)
            if 'expires_at' in details:
                from dateutil import parser
                domain.ssl_expires_at = parser.parse(details['expires_at'])
            else:
                domain.ssl_expires_at = timezone.now() + timedelta(days=90)
            
            domain.mark_active()
            
            # Log successful provisioning
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='ssl',
                status='success',
                details=details
            )
            
            # Log admin action
            log_admin_action(
                admin_user=request.user,
                action='approve_domain',
                target_trainer=domain.trainer,
                details={'domain': domain.domain, 'action': 'provision_ssl'},
                request=request
            )
            
            return Response({
                'status': 'success',
                'message': message,
                'details': details,
                'ssl_expires_at': domain.ssl_expires_at
            })
        else:
            domain.ssl_status = 'failed'
            domain.save()
            
            # Log failed provisioning
            DomainVerificationLog.objects.create(
                domain=domain,
                verification_type='ssl',
                status='failed',
                error_message=message,
                details=details
            )
            
            return Response({
                'status': 'failed',
                'message': message,
                'details': details
            }, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, methods=['post'])
    def approve_reject(self, request, pk=None):
        """
        Approve or reject domain request.
        
        POST /api/admin/domains/{id}/approve-reject/
        {
            "action": "approve|reject",
            "reason": "Optional reason for rejection"
        }
        """
        domain = self.get_object()
        serializer = DomainApprovalSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        if action_type == 'approve':
            domain.approved_by = request.user
            domain.approved_at = timezone.now()
            domain.status = 'verifying'
            domain.save()
            
            # Trigger verification
            verifier = DomainVerifier(domain.domain, domain.verification_token)
            success, message, details = verifier.verify_domain(domain.verification_method)
            
            if success:
                domain.mark_verified()
                domain.status = 'provisioning_ssl'
                domain.save()
            
            log_action = 'approve_domain'
            response_message = 'Domain approved and verification triggered'
            
        else:  # reject
            domain.status = 'failed'
            domain.rejection_reason = reason
            domain.save()
            
            log_action = 'reject_domain'
            response_message = f'Domain rejected: {reason}'
        
        # Log admin action
        log_admin_action(
            admin_user=request.user,
            action=log_action,
            target_trainer=domain.trainer,
            details={'domain': domain.domain, 'reason': reason},
            request=request
        )
        
        return Response({
            'status': action_type,
            'message': response_message,
            'domain': CustomDomainSerializer(domain).data
        })
    
    @action(detail=False, methods=['get'])
    def pending(self, request):
        """
        Get all pending domain requests.
        
        GET /api/admin/domains/pending/
        """
        queryset = self.get_queryset().filter(status='pending')
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })
    
    @action(detail=False, methods=['get'])
    def needs_ssl_renewal(self, request):
        """
        Get domains that need SSL renewal.
        
        GET /api/admin/domains/needs-ssl-renewal/
        """
        # Domains expiring in next 30 days
        expiry_threshold = timezone.now() + timedelta(days=30)
        queryset = self.get_queryset().filter(
            ssl_status='provisioned',
            ssl_expires_at__lte=expiry_threshold
        )
        
        serializer = self.get_serializer(queryset, many=True)
        return Response({
            'count': queryset.count(),
            'results': serializer.data
        })


class DomainVerificationLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View domain verification logs.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]
    queryset = DomainVerificationLog.objects.select_related('domain').all()
    serializer_class = DomainVerificationLogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by domain
        domain_id = self.request.query_params.get('domain_id')
        if domain_id:
            queryset = queryset.filter(domain_id=domain_id)
        
        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)
        
        return queryset

