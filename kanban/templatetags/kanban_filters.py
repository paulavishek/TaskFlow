from django import template

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

@register.simple_tag
def assign_value(value):
    """
    Assign a value to a variable in the template
    
    Usage: {% assign_value "some_value" as my_var %}
    """
    return value