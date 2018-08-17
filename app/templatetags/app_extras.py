from django import template
import unicodedata

register = template.Library()


def normalize2ascii(value):
    return unicodedata.normalize("NFKD", value).encode("ascii", "ignore")


register.filter("normalize2ascii", normalize2ascii)
