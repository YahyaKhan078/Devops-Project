from django import template
from App_Order.models import Cart

register = template.Library()


@register.filter
def cart_total(user):
    """Return the number of items in the user's cart."""
    if user.is_authenticated:
        return Cart.objects.filter(user=user, purchased=False).count()
    return 0