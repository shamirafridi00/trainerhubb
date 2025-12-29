from datetime import datetime, timedelta, time
from .models import AvailabilitySlot, TrainerBreak


def get_available_slots(trainer_id, start_date, end_date, duration_minutes=60):
    """
    Calculate available time slots for a trainer.
    
    Args:
        trainer_id: ID of the trainer
        start_date: Start date (date object)
        end_date: End date (date object)
        duration_minutes: Duration of each slot in minutes (default 60)
    
    Returns:
        Dictionary with available slots by date
    """
    from apps.trainers.models import Trainer
    
    try:
        trainer = Trainer.objects.get(id=trainer_id)
    except Trainer.DoesNotExist:
        return {}
    
    # Get all trainer breaks in this period
    breaks = TrainerBreak.objects.filter(
        trainer=trainer,
        start_date__lte=end_date,
        end_date__gte=start_date
    )
    
    available_slots = {}
    current_date = start_date
    
    while current_date <= end_date:
        # Check if this date is within a break
        is_on_break = any(
            break_period.start_date.date() <= current_date <= break_period.end_date.date()
            for break_period in breaks
        )
        
        if is_on_break:
            current_date += timedelta(days=1)
            continue
        
        # Get availability slots for this day of week
        day_of_week = current_date.weekday()
        slots = AvailabilitySlot.objects.filter(
            trainer=trainer,
            day_of_week=day_of_week,
            is_active=True
        )
        
        day_slots = []
        for slot in slots:
            # Generate 60-minute slots within the availability window
            current_time = datetime.combine(current_date, slot.start_time)
            end_time = datetime.combine(current_date, slot.end_time)
            
            while current_time + timedelta(minutes=duration_minutes) <= end_time:
                day_slots.append(current_time.time())
                current_time += timedelta(minutes=duration_minutes)
        
        if day_slots:
            available_slots[current_date.isoformat()] = day_slots
        
        current_date += timedelta(days=1)
    
    return available_slots


def has_conflict(trainer_id, start_datetime, end_datetime):
    """
    Check if booking time conflicts with existing bookings.
    
    Args:
        trainer_id: ID of the trainer
        start_datetime: Start datetime of proposed booking
        end_datetime: End datetime of proposed booking
    
    Returns:
        Boolean indicating if there's a conflict
    """
    from apps.bookings.models import Booking
    
    conflicts = Booking.objects.filter(
        trainer_id=trainer_id,
        status__in=['pending', 'confirmed'],
        start_time__lt=end_datetime,
        end_time__gt=start_datetime
    )
    
    return conflicts.exists()

