"""
Admin Panel Views
API endpoints for super admin functionality.
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.contrib.auth import get_user_model
from django.db.models import Count, Q, Sum
from django.utils import timezone
from datetime import timedelta

from apps.trainers.models import Trainer
from apps.clients.models import Client
from apps.bookings.models import Booking
from .models import AdminActionLog, PlatformSettings
from .serializers import (
    TrainerAdminSerializer,
    TrainerDetailAdminSerializer,
    AdminActionLogSerializer,
    PlatformStatsSerializer,
    TrainerAccountActionSerializer,
    ImpersonateSerializer,
    RevenueTrendSerializer,
    SignupTrendSerializer,
    ActiveUsersTrendSerializer,
    GeographicDistributionSerializer,
    BookingTrendSerializer,
    ClientGrowthTrendSerializer,
    TopPerformingTrainerSerializer,
    AnalyticsDashboardSerializer
)
from .permissions import IsSuperUser
from .utils import log_admin_action, get_client_ip
from .export_utils import (
    export_trainers_csv,
    export_trainer_detail_csv,
    export_platform_stats_csv
)
from .bulk_actions import (
    bulk_suspend_trainers,
    bulk_activate_trainers,
    bulk_verify_trainers,
    bulk_delete_trainers
)
from .analytics_utils import (
    get_revenue_trends,
    get_signup_trends,
    get_active_users_over_time,
    get_geographic_distribution,
    get_revenue_by_plan,
    get_booking_trends,
    get_client_growth_trends,
    get_top_performing_trainers
)

User = get_user_model()


class AdminDashboardViewSet(viewsets.ViewSet):
    """
    Admin dashboard endpoints for platform overview.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]
    
    @action(detail=False, methods=['get'])
    def stats(self, request):
        """
        Get platform-wide statistics.
        """
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        last_month_start = (this_month_start - timedelta(days=1)).replace(day=1)
        
        # Basic counts
        total_trainers = Trainer.objects.count()
        active_trainers = Trainer.objects.filter(user__is_active=True).count()
        total_clients = Client.objects.filter(is_active=True).count()
        total_bookings = Booking.objects.count()
        
        # New signups this month
        new_signups = Trainer.objects.filter(
            created_at__gte=this_month_start
        ).count()
        
        # Subscription breakdown
        try:
            from apps.payments.models import Subscription
            subscription_breakdown = Subscription.objects.filter(
                status='active'
            ).values('plan').annotate(count=Count('id'))
            subscription_breakdown = {
                item['plan']: item['count'] 
                for item in subscription_breakdown
            }
        except:
            subscription_breakdown = {}
        
        # Revenue calculations (placeholder - will be populated by Paddle webhooks)
        try:
            from apps.payments.models import Payment
            this_month_revenue = Payment.objects.filter(
                created_at__gte=this_month_start,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            # Simple MRR calculation
            active_subs = Subscription.objects.filter(status='active')
            mrr = sum([self._get_plan_price(sub.plan) for sub in active_subs])
            
            # Churn calculation
            churned_this_month = Subscription.objects.filter(
                status='cancelled',
                updated_at__gte=this_month_start
            ).count()
            active_last_month = Subscription.objects.filter(
                created_at__lt=this_month_start
            ).count()
            churn_rate = (churned_this_month / active_last_month * 100) if active_last_month > 0 else 0
            
        except:
            this_month_revenue = 0
            mrr = 0
            churn_rate = 0
        
        data = {
            'total_trainers': total_trainers,
            'active_trainers': active_trainers,
            'total_clients': total_clients,
            'total_bookings': total_bookings,
            'new_signups_this_month': new_signups,
            'total_revenue_this_month': this_month_revenue,
            'mrr': mrr,
            'churn_rate': round(churn_rate, 2),
            'subscription_breakdown': subscription_breakdown
        }
        
        serializer = PlatformStatsSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def export_stats(self, request):
        """
        Export platform statistics to CSV.
        
        GET /api/admin/dashboard/export-stats/
        """
        # Get the same stats as the stats endpoint
        now = timezone.now()
        this_month_start = now.replace(day=1, hour=0, minute=0, second=0, microsecond=0)
        
        total_trainers = Trainer.objects.count()
        active_trainers = Trainer.objects.filter(user__is_active=True).count()
        total_clients = Client.objects.filter(is_active=True).count()
        total_bookings = Booking.objects.count()
        new_signups = Trainer.objects.filter(created_at__gte=this_month_start).count()
        
        try:
            from apps.payments.models import Subscription, Payment
            this_month_revenue = Payment.objects.filter(
                created_at__gte=this_month_start,
                status='completed'
            ).aggregate(total=Sum('amount'))['total'] or 0
            
            active_subs = Subscription.objects.filter(status='active')
            mrr = sum([self._get_plan_price(sub.plan) for sub in active_subs])
            
            churned_this_month = Subscription.objects.filter(
                status='cancelled',
                updated_at__gte=this_month_start
            ).count()
            active_last_month = Subscription.objects.filter(
                created_at__lt=this_month_start
            ).count()
            churn_rate = (churned_this_month / active_last_month * 100) if active_last_month > 0 else 0
            
            subscription_breakdown = Subscription.objects.filter(
                status='active'
            ).values('plan').annotate(count=Count('id'))
            subscription_breakdown = {
                item['plan']: item['count'] 
                for item in subscription_breakdown
            }
        except:
            this_month_revenue = 0
            mrr = 0
            churn_rate = 0
            subscription_breakdown = {}
        
        stats_data = {
            'total_trainers': total_trainers,
            'active_trainers': active_trainers,
            'total_clients': total_clients,
            'total_bookings': total_bookings,
            'new_signups_this_month': new_signups,
            'total_revenue_this_month': this_month_revenue,
            'mrr': mrr,
            'churn_rate': round(churn_rate, 2),
            'subscription_breakdown': subscription_breakdown
        }
        
        # Log the export action
        log_admin_action(
            admin_user=request.user,
            action='view_trainer',
            details={'action': 'export_stats'},
            request=request
        )
        
        return export_platform_stats_csv(stats_data)
    
    def _get_plan_price(self, plan):
        """Get monthly price for a plan."""
        prices = {
            'free': 0,
            'pro': 29,
            'business': 79
        }
        return prices.get(plan, 0)
    
    @action(detail=False, methods=['get'])
    def analytics(self, request):
        """
        Get complete analytics dashboard data.
        
        GET /api/admin/dashboard/analytics/
        
        Query Parameters:
        - days: Number of days to look back (default: 30)
        - group_by: 'day' or 'month' (default: 'day')
        
        Returns comprehensive analytics data for charts and visualizations.
        """
        days = int(request.query_params.get('days', 30))
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by not in ['day', 'month']:
            group_by = 'day'
        
        # Get all analytics data
        revenue_trends = get_revenue_trends(days=days, group_by=group_by)
        signup_trends = get_signup_trends(days=days, group_by=group_by)
        active_users_trends = get_active_users_over_time(days=days, group_by=group_by)
        geographic_distribution = get_geographic_distribution()
        booking_trends = get_booking_trends(days=days, group_by=group_by)
        client_growth_trends = get_client_growth_trends(days=days, group_by=group_by)
        revenue_by_plan = get_revenue_by_plan()
        top_performing_trainers = get_top_performing_trainers(limit=10)
        
        data = {
            'revenue_trends': revenue_trends,
            'signup_trends': signup_trends,
            'active_users_trends': active_users_trends,
            'geographic_distribution': geographic_distribution,
            'booking_trends': booking_trends,
            'client_growth_trends': client_growth_trends,
            'revenue_by_plan': revenue_by_plan,
            'top_performing_trainers': top_performing_trainers
        }
        
        serializer = AnalyticsDashboardSerializer(data)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def revenue_trends(self, request):
        """
        Get revenue trends over time.
        
        GET /api/admin/dashboard/revenue-trends/
        
        Query Parameters:
        - days: Number of days to look back (default: 30)
        - group_by: 'day' or 'month' (default: 'day')
        """
        days = int(request.query_params.get('days', 30))
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by not in ['day', 'month']:
            group_by = 'day'
        
        trends = get_revenue_trends(days=days, group_by=group_by)
        serializer = RevenueTrendSerializer(trends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def signup_trends(self, request):
        """
        Get trainer signup trends over time.
        
        GET /api/admin/dashboard/signup-trends/
        
        Query Parameters:
        - days: Number of days to look back (default: 30)
        - group_by: 'day' or 'month' (default: 'day')
        """
        days = int(request.query_params.get('days', 30))
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by not in ['day', 'month']:
            group_by = 'day'
        
        trends = get_signup_trends(days=days, group_by=group_by)
        serializer = SignupTrendSerializer(trends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def active_users_trends(self, request):
        """
        Get active users trends over time.
        
        GET /api/admin/dashboard/active-users-trends/
        
        Query Parameters:
        - days: Number of days to look back (default: 30)
        - group_by: 'day' or 'month' (default: 'day')
        """
        days = int(request.query_params.get('days', 30))
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by not in ['day', 'month']:
            group_by = 'day'
        
        trends = get_active_users_over_time(days=days, group_by=group_by)
        serializer = ActiveUsersTrendSerializer(trends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def geographic_distribution(self, request):
        """
        Get geographic distribution of trainers.
        
        GET /api/admin/dashboard/geographic-distribution/
        """
        distribution = get_geographic_distribution()
        serializer = GeographicDistributionSerializer(distribution, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def booking_trends(self, request):
        """
        Get booking trends over time.
        
        GET /api/admin/dashboard/booking-trends/
        
        Query Parameters:
        - days: Number of days to look back (default: 30)
        - group_by: 'day' or 'month' (default: 'day')
        """
        days = int(request.query_params.get('days', 30))
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by not in ['day', 'month']:
            group_by = 'day'
        
        trends = get_booking_trends(days=days, group_by=group_by)
        serializer = BookingTrendSerializer(trends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def client_growth_trends(self, request):
        """
        Get client growth trends over time.
        
        GET /api/admin/dashboard/client-growth-trends/
        
        Query Parameters:
        - days: Number of days to look back (default: 30)
        - group_by: 'day' or 'month' (default: 'day')
        """
        days = int(request.query_params.get('days', 30))
        group_by = request.query_params.get('group_by', 'day')
        
        if group_by not in ['day', 'month']:
            group_by = 'day'
        
        trends = get_client_growth_trends(days=days, group_by=group_by)
        serializer = ClientGrowthTrendSerializer(trends, many=True)
        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def top_performing_trainers(self, request):
        """
        Get top performing trainers by revenue/bookings.
        
        GET /api/admin/dashboard/top-performing-trainers/
        
        Query Parameters:
        - limit: Number of trainers to return (default: 10)
        """
        limit = int(request.query_params.get('limit', 10))
        trainers = get_top_performing_trainers(limit=limit)
        serializer = TopPerformingTrainerSerializer(trainers, many=True)
        return Response(serializer.data)


class TrainerAdminViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin endpoints for managing trainers.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]
    queryset = Trainer.objects.select_related('user').all()
    serializer_class = TrainerAdminSerializer
    
    def get_serializer_class(self):
        if self.action == 'retrieve':
            return TrainerDetailAdminSerializer
        return TrainerAdminSerializer
    
    def list(self, request, *args, **kwargs):
        """
        List all trainers with filters.
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Filter by search query
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(business_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        # Filter by status
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(user__is_active=is_active.lower() == 'true')
        
        # Filter by subscription plan
        plan = request.query_params.get('plan')
        if plan:
            try:
                from apps.payments.models import Subscription
                trainer_ids = Subscription.objects.filter(
                    plan=plan
                ).values_list('trainer_id', flat=True)
                queryset = queryset.filter(id__in=trainer_ids)
            except:
                pass
        
        page = self.paginate_queryset(queryset)
        if page is not None:
            serializer = self.get_serializer(page, many=True)
            return self.get_paginated_response(serializer.data)
        
        serializer = self.get_serializer(queryset, many=True)
        return Response(serializer.data)
    
    @action(detail=True, methods=['post'])
    def account_action(self, request, pk=None):
        """
        Perform account actions: suspend, activate, delete, verify.
        """
        trainer = self.get_object()
        serializer = TrainerAccountActionSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        action_type = serializer.validated_data['action']
        reason = serializer.validated_data.get('reason', '')
        
        if action_type == 'suspend':
            trainer.user.is_active = False
            trainer.user.save()
            log_action = 'suspend'
            message = f'Trainer {trainer.business_name} has been suspended.'
            
        elif action_type == 'activate':
            trainer.user.is_active = True
            trainer.user.save()
            log_action = 'activate'
            message = f'Trainer {trainer.business_name} has been activated.'
            
        elif action_type == 'verify':
            trainer.is_verified = True
            trainer.save()
            log_action = 'activate'
            message = f'Trainer {trainer.business_name} has been verified.'
            
        elif action_type == 'delete':
            business_name = trainer.business_name
            trainer.user.delete()  # Cascade deletes trainer
            log_action = 'delete_trainer'
            message = f'Trainer {business_name} has been deleted.'
        else:
            return Response(
                {'error': 'Invalid action'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Log the action
        log_admin_action(
            admin_user=request.user,
            action=log_action,
            target_trainer=trainer if action_type != 'delete' else None,
            details={'reason': reason},
            request=request
        )
        
        return Response({'message': message})
    
    @action(detail=True, methods=['post'])
    def impersonate(self, request, pk=None):
        """
        Impersonate a trainer (returns their auth token).
        """
        trainer = self.get_object()
        serializer = ImpersonateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        reason = serializer.validated_data.get('reason', 'Support/Debugging')
        
        # Log the impersonation
        log_admin_action(
            admin_user=request.user,
            action='impersonate',
            target_trainer=trainer,
            details={'reason': reason},
            request=request
        )
        
        # Generate token for the trainer's user
        from rest_framework.authtoken.models import Token
        token, _ = Token.objects.get_or_create(user=trainer.user)
        
        return Response({
            'token': token.key,
            'trainer_id': trainer.id,
            'user_id': trainer.user.id,
            'email': trainer.user.email,
            'business_name': trainer.business_name,
            'message': 'Impersonation active. Use this token to access trainer dashboard.'
        })
    
    @action(detail=False, methods=['post'])
    def bulk_action(self, request):
        """
        Perform bulk actions on multiple trainers.
        
        POST /api/admin/trainers/bulk-action/
        {
            "action": "suspend|activate|verify|delete",
            "trainer_ids": [1, 2, 3],
            "reason": "Optional reason"
        }
        """
        action_type = request.data.get('action')
        trainer_ids = request.data.get('trainer_ids', [])
        reason = request.data.get('reason', '')
        
        if not action_type:
            return Response(
                {'error': 'Action type is required'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        if not trainer_ids or not isinstance(trainer_ids, list):
            return Response(
                {'error': 'trainer_ids must be a non-empty list'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Perform the bulk action
        if action_type == 'suspend':
            result = bulk_suspend_trainers(trainer_ids, request.user, reason, request)
        elif action_type == 'activate':
            result = bulk_activate_trainers(trainer_ids, request.user, reason, request)
        elif action_type == 'verify':
            result = bulk_verify_trainers(trainer_ids, request.user, request)
        elif action_type == 'delete':
            result = bulk_delete_trainers(trainer_ids, request.user, reason, request)
        else:
            return Response(
                {'error': f'Invalid action: {action_type}'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        return Response({
            'action': action_type,
            'success_count': result['success_count'],
            'failed_count': result['failed_count'],
            'failed': result['failed'],
            'message': f'Successfully {action_type}ed {result["success_count"]} trainer(s)'
        })
    
    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export trainers list to CSV.
        
        GET /api/admin/trainers/export/
        """
        queryset = self.filter_queryset(self.get_queryset())
        
        # Apply same filters as list view
        search = request.query_params.get('search', '')
        if search:
            queryset = queryset.filter(
                Q(business_name__icontains=search) |
                Q(user__email__icontains=search) |
                Q(user__first_name__icontains=search) |
                Q(user__last_name__icontains=search)
            )
        
        is_active = request.query_params.get('is_active')
        if is_active is not None:
            queryset = queryset.filter(user__is_active=is_active.lower() == 'true')
        
        plan = request.query_params.get('plan')
        if plan:
            try:
                from apps.payments.models import Subscription
                trainer_ids = Subscription.objects.filter(
                    plan=plan
                ).values_list('trainer_id', flat=True)
                queryset = queryset.filter(id__in=trainer_ids)
            except:
                pass
        
        # Log the export action
        log_admin_action(
            admin_user=request.user,
            action='view_trainer',
            details={'action': 'export', 'count': queryset.count()},
            request=request
        )
        
        return export_trainers_csv(queryset)
    
    @action(detail=True, methods=['get'])
    def export_detail(self, request, pk=None):
        """
        Export detailed trainer information to CSV.
        
        GET /api/admin/trainers/{id}/export-detail/
        """
        trainer = self.get_object()
        
        # Log the export action
        log_admin_action(
            admin_user=request.user,
            action='view_trainer',
            target_trainer=trainer,
            details={'action': 'export_detail'},
            request=request
        )
        
        return export_trainer_detail_csv(trainer)


class AdminActionLogViewSet(viewsets.ReadOnlyModelViewSet):
    """
    View admin action logs.
    """
    permission_classes = [IsAuthenticated, IsSuperUser]
    queryset = AdminActionLog.objects.select_related(
        'admin_user', 'target_trainer'
    ).all()
    serializer_class = AdminActionLogSerializer
    
    def get_queryset(self):
        queryset = super().get_queryset()
        
        # Filter by admin user
        admin_id = self.request.query_params.get('admin_id')
        if admin_id:
            queryset = queryset.filter(admin_user_id=admin_id)
        
        # Filter by trainer
        trainer_id = self.request.query_params.get('trainer_id')
        if trainer_id:
            queryset = queryset.filter(target_trainer_id=trainer_id)
        
        # Filter by action type
        action = self.request.query_params.get('action')
        if action:
            queryset = queryset.filter(action=action)
        
        return queryset
