"""
Bulk action utilities for admin panel.
Handle bulk operations on multiple trainers.
"""
from django.db import transaction
from .models import AdminActionLog
from .utils import log_admin_action


def bulk_suspend_trainers(trainer_ids, admin_user, reason='', request=None):
    """
    Suspend multiple trainers at once.
    
    Args:
        trainer_ids: List of trainer IDs
        admin_user: Admin user performing the action
        reason: Reason for suspension
        request: HTTP request object (optional)
        
    Returns:
        dict: Results of the operation
    """
    from apps.trainers.models import Trainer
    
    success_count = 0
    failed = []
    
    with transaction.atomic():
        trainers = Trainer.objects.filter(id__in=trainer_ids).select_related('user')
        
        for trainer in trainers:
            try:
                if trainer.user.is_active:
                    trainer.user.is_active = False
                    trainer.user.save()
                    
                    # Log the action
                    log_admin_action(
                        admin_user=admin_user,
                        action='suspend',
                        target_trainer=trainer,
                        details={'reason': reason, 'bulk_action': True},
                        request=request
                    )
                    
                    success_count += 1
                else:
                    failed.append({
                        'id': trainer.id,
                        'business_name': trainer.business_name,
                        'reason': 'Already suspended'
                    })
            except Exception as e:
                failed.append({
                    'id': trainer.id,
                    'business_name': trainer.business_name,
                    'reason': str(e)
                })
    
    return {
        'success_count': success_count,
        'failed_count': len(failed),
        'failed': failed
    }


def bulk_activate_trainers(trainer_ids, admin_user, reason='', request=None):
    """
    Activate multiple trainers at once.
    
    Args:
        trainer_ids: List of trainer IDs
        admin_user: Admin user performing the action
        reason: Reason for activation
        request: HTTP request object (optional)
        
    Returns:
        dict: Results of the operation
    """
    from apps.trainers.models import Trainer
    
    success_count = 0
    failed = []
    
    with transaction.atomic():
        trainers = Trainer.objects.filter(id__in=trainer_ids).select_related('user')
        
        for trainer in trainers:
            try:
                if not trainer.user.is_active:
                    trainer.user.is_active = True
                    trainer.user.save()
                    
                    # Log the action
                    log_admin_action(
                        admin_user=admin_user,
                        action='activate',
                        target_trainer=trainer,
                        details={'reason': reason, 'bulk_action': True},
                        request=request
                    )
                    
                    success_count += 1
                else:
                    failed.append({
                        'id': trainer.id,
                        'business_name': trainer.business_name,
                        'reason': 'Already active'
                    })
            except Exception as e:
                failed.append({
                    'id': trainer.id,
                    'business_name': trainer.business_name,
                    'reason': str(e)
                })
    
    return {
        'success_count': success_count,
        'failed_count': len(failed),
        'failed': failed
    }


def bulk_verify_trainers(trainer_ids, admin_user, request=None):
    """
    Verify multiple trainers at once.
    
    Args:
        trainer_ids: List of trainer IDs
        admin_user: Admin user performing the action
        request: HTTP request object (optional)
        
    Returns:
        dict: Results of the operation
    """
    from apps.trainers.models import Trainer
    
    success_count = 0
    failed = []
    
    with transaction.atomic():
        trainers = Trainer.objects.filter(id__in=trainer_ids)
        
        for trainer in trainers:
            try:
                if not trainer.is_verified:
                    trainer.is_verified = True
                    trainer.save()
                    
                    # Log the action
                    log_admin_action(
                        admin_user=admin_user,
                        action='activate',  # Using activate as closest match
                        target_trainer=trainer,
                        details={'action': 'verify', 'bulk_action': True},
                        request=request
                    )
                    
                    success_count += 1
                else:
                    failed.append({
                        'id': trainer.id,
                        'business_name': trainer.business_name,
                        'reason': 'Already verified'
                    })
            except Exception as e:
                failed.append({
                    'id': trainer.id,
                    'business_name': trainer.business_name,
                    'reason': str(e)
                })
    
    return {
        'success_count': success_count,
        'failed_count': len(failed),
        'failed': failed
    }


def bulk_delete_trainers(trainer_ids, admin_user, reason='', request=None):
    """
    Delete multiple trainers at once.
    WARNING: This is a destructive operation!
    
    Args:
        trainer_ids: List of trainer IDs
        admin_user: Admin user performing the action
        reason: Reason for deletion
        request: HTTP request object (optional)
        
    Returns:
        dict: Results of the operation
    """
    from apps.trainers.models import Trainer
    
    success_count = 0
    failed = []
    deleted_names = []
    
    with transaction.atomic():
        trainers = Trainer.objects.filter(id__in=trainer_ids).select_related('user')
        
        for trainer in trainers:
            try:
                business_name = trainer.business_name
                trainer_id = trainer.id
                
                # Log before deletion
                log_admin_action(
                    admin_user=admin_user,
                    action='delete_trainer',
                    target_trainer=None,  # Can't reference after delete
                    details={
                        'reason': reason,
                        'bulk_action': True,
                        'trainer_id': trainer_id,
                        'business_name': business_name
                    },
                    request=request
                )
                
                # Delete (cascade deletes related objects)
                trainer.user.delete()
                
                success_count += 1
                deleted_names.append(business_name)
                
            except Exception as e:
                failed.append({
                    'id': trainer.id,
                    'business_name': trainer.business_name,
                    'reason': str(e)
                })
    
    return {
        'success_count': success_count,
        'failed_count': len(failed),
        'failed': failed,
        'deleted': deleted_names
    }

