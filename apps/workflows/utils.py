"""
Utility functions for workflow automation
"""
import re
from datetime import datetime


def replace_variables(text: str, data: dict) -> str:
    """
    Replace variables in text with values from data.
    
    Variables are in the format {{variable_name}}.
    
    Args:
        text: Text containing variables
        data: Dictionary of variable values
    
    Returns:
        Text with variables replaced
    
    Example:
        >>> replace_variables("Hello {{client_name}}!", {"client_name": "John"})
        'Hello John!'
    """
    if not text:
        return ""
    
    # Find all variables in the format {{variable_name}}
    pattern = r'\{\{(\w+)\}\}'
    
    def replacer(match):
        var_name = match.group(1)
        value = data.get(var_name, match.group(0))  # Keep {{var}} if not found
        
        # Format datetime objects
        if isinstance(value, datetime):
            return value.strftime('%Y-%m-%d %H:%M')
        
        return str(value)
    
    return re.sub(pattern, replacer, text)


def get_available_variables(trigger_type: str) -> list:
    """
    Get list of available variables for a trigger type.
    
    Args:
        trigger_type: Type of trigger
    
    Returns:
        List of variable dictionaries
    """
    variables = {
        'booking_created': [
            {'name': 'client_name', 'description': "Client's full name"},
            {'name': 'client_email', 'description': "Client's email address"},
            {'name': 'client_phone', 'description': "Client's phone number"},
            {'name': 'trainer_name', 'description': "Trainer's business name"},
            {'name': 'booking_date', 'description': 'Date of the booking'},
            {'name': 'booking_time', 'description': 'Time of the booking'},
            {'name': 'booking_location', 'description': 'Location of the booking'},
        ],
        'booking_confirmed': [
            {'name': 'client_name', 'description': "Client's full name"},
            {'name': 'client_email', 'description': "Client's email address"},
            {'name': 'trainer_name', 'description': "Trainer's business name"},
            {'name': 'booking_date', 'description': 'Date of the booking'},
            {'name': 'booking_time', 'description': 'Time of the booking'},
        ],
        'booking_cancelled': [
            {'name': 'client_name', 'description': "Client's full name"},
            {'name': 'client_email', 'description': "Client's email address"},
            {'name': 'trainer_name', 'description': "Trainer's business name"},
            {'name': 'booking_date', 'description': 'Date of the booking'},
            {'name': 'cancellation_reason', 'description': 'Reason for cancellation'},
        ],
        'payment_received': [
            {'name': 'client_name', 'description': "Client's full name"},
            {'name': 'client_email', 'description': "Client's email address"},
            {'name': 'trainer_name', 'description': "Trainer's business name"},
            {'name': 'payment_amount', 'description': 'Amount paid'},
            {'name': 'payment_method', 'description': 'Payment method used'},
            {'name': 'payment_date', 'description': 'Date of payment'},
        ],
        'client_created': [
            {'name': 'client_name', 'description': "Client's full name"},
            {'name': 'client_email', 'description': "Client's email address"},
            {'name': 'trainer_name', 'description': "Trainer's business name"},
        ],
        'package_purchased': [
            {'name': 'client_name', 'description': "Client's full name"},
            {'name': 'client_email', 'description': "Client's email address"},
            {'name': 'trainer_name', 'description': "Trainer's business name"},
            {'name': 'package_name', 'description': 'Name of the package'},
            {'name': 'package_price', 'description': 'Price of the package'},
            {'name': 'sessions_included', 'description': 'Number of sessions'},
        ],
    }
    
    return variables.get(trigger_type, [])

