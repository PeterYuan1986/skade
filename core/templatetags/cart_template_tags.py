from django import template
from core.models import Order, Category, Item
from django.template.loader import get_template

register = template.Library()


@register.filter
def cart_item_count(user):
    if user.is_authenticated:
        qs = Order.objects.filter(user=user, ordered=False)
        if qs.exists():
            sm = 0
            for item in qs[0].items.all():
                sm += item.quantity
            return sm
    return 0

@register.filter(name='full')
def full(number):
    if number*10%10>=5:
        return range(int(number)+1)
    else:
        return range(int(number))


@register.filter(name='empty')
def empty(number):
    if number * 10 % 10 < 5:
        return range(5-int(number))
    else:
        return range(4-int(number))