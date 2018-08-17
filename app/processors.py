from .models import DifficultyLevel
from .models import DancingStyle
from .models import DancingLevel
from django.conf import settings
from .models import EndUser


def globals(request):
    try:
        enduser = EndUser.objects.get(user=request.user)
    except EndUser.DoesNotExist:
        enduser = None
    return {
        "dancing_styles": DancingStyle.objects.all().order_by("name"),
        "dancing_levels": DancingLevel.objects.all().order_by("level"),
        "difficulty_levels": DifficultyLevel.objects.all().order_by("level"),
        "bachata_spotify_list": settings.BACHATA_SPOTIFY_LIST,
        "salsa_spotify_list": settings.SALSA_SPOTIFY_LIST,
        "my_enduser": enduser
    }
