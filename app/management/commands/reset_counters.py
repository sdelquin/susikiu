from django.core.management.base import BaseCommand
from app.models import Video
from django.db import transaction


class Command(BaseCommand):
    help = "Reset the specified counter to zero"

    def add_arguments(self, parser):
        parser.add_argument("--likes", action="store_true")
        parser.add_argument("--views", action="store_true")

    @transaction.atomic
    def handle(self, *args, **options):
        if options["views"]:
            Video.objects.all().update(views_count=0)
        if options["likes"]:
            Video.likes.through.objects.all().delete()
            Video.objects.all().update(likes_count=0)
