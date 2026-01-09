from django import template
register = template.Library()

@register.filter
def get(dict, key): #used in contact_form.html
    return dict.get(key, '')