from django import template

register = template.Library()

@register.filter
def get_item(dictionary, key):
    """Retorna um item de um dicionário usando a chave"""
    if dictionary is None:
        return None
    return dictionary.get(key)

