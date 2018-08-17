from django.contrib import admin

from .models import EndUser
from .models import DancingStyle
from .models import DancingLevel
from .models import DifficultyLevel
from .models import Song
from .models import Video
from import_export.admin import ImportExportActionModelAdmin


class VideoAdmin(admin.ModelAdmin):
    exclude = (
        "youtube_id",
        "api_url",
        "embed_url",
        "thumbnail_url",
        "duration",
        "duration_string",
        "views_count",
        "likes_count",
        "likes"
    )
    raw_id_fields = ("song",)
    list_display = (
        "title",
        "recorded",
        "duration_string",
        "dancing_style"
    )


class SongAdmin(ImportExportActionModelAdmin):
    list_display = (
        "title",
        "artist"
    )
    search_fields = [
        "title",
        "artist"
    ]


admin.site.register(EndUser)
admin.site.register(DancingStyle)
admin.site.register(DancingLevel)
admin.site.register(DifficultyLevel)
admin.site.register(Song, SongAdmin)
admin.site.register(Video, VideoAdmin)
