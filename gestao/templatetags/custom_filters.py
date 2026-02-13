from django import template

register = template.Library()


@register.filter
def status_color(status):
    """Return Bootstrap color class based on status"""
    colors = {
        'aberta': 'danger',
        'em_andamento': 'warning',
        'resolvida': 'info',
        'fechada': 'success',
    }
    return colors.get(status, 'secondary')


@register.filter
def role_icon(role):
    """Return icon for user role"""
    icons = {
        'encarregado': '👤',
        'gerente': '👨‍💼',
        'gestor': '👨‍✈️',
    }
    return icons.get(role, '❓')
