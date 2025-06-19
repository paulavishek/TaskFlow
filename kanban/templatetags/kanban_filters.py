from django import template
from django.utils import timezone
from datetime import datetime

register = template.Library()

@register.filter
def percentage(value, arg):
    """
    Calculate percentage of value/arg
    
    Usage: {{ value|percentage:total }}
    """
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0
        return int((value / arg) * 100)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def divide(value, arg):
    """
    Divide the value by the argument
    
    Usage: {{ value|divide:divisor }}
    """
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0
        return value / arg
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def mul(value, arg):
    """
    Multiply the value by the argument
    
    Usage: {{ value|mul:multiplier }}
    """
    try:
        value = float(value)
        arg = float(arg)
        return value * arg
    except (ValueError, TypeError):
        return 0

@register.filter
def div(value, arg):
    """
    Divide the value by the argument and return integer
    
    Usage: {{ value|div:divisor }}
    """
    try:
        value = float(value)
        arg = float(arg)
        if arg == 0:
            return 0
        return int(value / arg)
    except (ValueError, ZeroDivisionError):
        return 0

@register.filter
def timesince_days(value):
    """
    Calculate the number of days since a given date
    
    Usage: {{ task.due_date|timesince_days }}
    """
    try:
        if value is None:
            return 0
        
        if isinstance(value, datetime):
            due_date = value.date()
        else:
            due_date = value
            
        today = timezone.now().date()
        delta = today - due_date
        return delta.days
    except (AttributeError, TypeError):
        return 0

@register.simple_tag
def assign_value(value):
    """
    Assign a value to a variable in the template
    
    Usage: {% assign_value "some_value" as my_var %}
    """
    return value