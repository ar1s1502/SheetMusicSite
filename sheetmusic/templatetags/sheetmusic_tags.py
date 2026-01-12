from django import template
register = template.Library()


@register.filter
def convert_price(num: int):
    if (num == 0):
        return "Free!"
    return f"${(num/100):.2f}"