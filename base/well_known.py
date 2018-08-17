import os
from django.conf import settings
from django.http import HttpResponse


def acme_challenge(request, filename):
    path = os.path.join(
        settings.BASE_DIR,
        ".well-known",
        "acme-challenge",
        filename
    )
    with open(path) as f:
        return HttpResponse(f.read())
