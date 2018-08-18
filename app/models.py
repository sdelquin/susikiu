import datetime
import re
import json

from django.db import models
from django.contrib.auth.models import User
from django.conf import settings
from django.core.urlresolvers import reverse
from django.contrib.staticfiles.templatetags.staticfiles import static
from django.utils.timezone import utc
from PIL import Image, ImageOps
import dateparser
import dateutil
import requests

from .tasks import send_new_video_email


class EndUser(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE
    )
    dancing_level = models.ForeignKey(
        "DancingLevel",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    favourite_dancing_style = models.ForeignKey(
        "DancingStyle",
        on_delete=models.SET_NULL,
        blank=True,
        null=True
    )
    teacher = models.BooleanField(default=False)
    avatar = models.ImageField(
        null=True,
        blank=True,
        upload_to="uploads/"
    )
    date_of_birth = models.DateField(blank=True, null=True)
    why_dance = models.CharField(
        blank=True,
        max_length=140
    )
    bio = models.TextField(blank=True)
    twitter_username = models.SlugField(blank=True)
    facebook_username = models.SlugField(blank=True)
    snapchat_username = models.SlugField(blank=True)
    instagram_username = models.SlugField(blank=True)

    def __str__(self):
        return self.get_fullname()

    def save(self):
        super(EndUser, self).save()
        if self.avatar:
            image = Image.open(self.avatar)
            image = ImageOps.fit(image,
                                 settings.AVATAR_SIZE,
                                 Image.ANTIALIAS,
                                 centering=(0.5, 0.5))
            image.save(self.avatar.path)

    def get_avatar_url(self):
        if self.avatar:
            return self.avatar.url
        else:
            return static("app/images/nobody.png")

    def get_dancing_level_code(self):
        if self.dancing_level:
            return self.dancing_level.code
        else:
            return ""

    def get_favourite_dancing_style_code(self):
        if self.favourite_dancing_style:
            return self.favourite_dancing_style.code
        else:
            return ""

    def get_fullname(self):
        return "{} {}".format(self.user.first_name, self.user.last_name)

    def age(self):
        if self.date_of_birth:
            now = datetime.datetime.utcnow()
            now = now.date()
            age = dateutil.relativedelta.relativedelta(now, self.date_of_birth)
            age = age.years
        else:
            age = None
        return age

    def joined_days(self):
        return (datetime.datetime.utcnow().replace(tzinfo=utc) -
                self.user.date_joined).days

    def get_social_network_url(self, network):
        attribute = getattr(self, "{}_username".format(network))
        if attribute:
            return "{}{}".format(
                settings.SOCIAL_NETWORKS_BASE_URL[network.upper()],
                attribute
            )
        else:
            return None

    def complete_profile(self):
        return self.dancing_level and\
            self.favourite_dancing_style and\
            self.avatar and\
            self.date_of_birth and\
            self.why_dance and\
            self.bio and\
            self.facebook_username


class DancingStyle(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(
        max_length=8,
        unique=True
    )
    description = models.CharField(
        blank=True,
        max_length=256
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_choices(cls):
        r = [(d.code, d.name) for d in cls.objects.all()]
        # empty label
        r.insert(0, ("", "Ninguno"))
        return r


class DancingLevel(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(
        max_length=8,
        unique=True
    )
    level = models.PositiveSmallIntegerField()
    description = models.CharField(
        blank=True,
        max_length=256
    )
    timetable = models.CharField(
        blank=True,
        max_length=256
    )

    def __str__(self):
        return self.name

    @classmethod
    def get_choices(cls):
        r = [(d.code, d.name) for d in cls.objects.all()]
        # empty label
        r.insert(0, ("", "Ninguno"))
        return r


class DifficultyLevel(models.Model):
    name = models.CharField(max_length=64)
    code = models.CharField(
        max_length=8,
        unique=True
    )
    level = models.PositiveSmallIntegerField()
    description = models.CharField(
        blank=True,
        max_length=256
    )

    def __str__(self):
        return self.name


class Song(models.Model):
    title = models.CharField(
        unique=True,
        max_length=191
    )
    artist = models.CharField(max_length=256)
    spotify_url = models.URLField(blank=True)
    youtube_url = models.URLField(blank=True)

    def __str__(self):
        return self.title


class Video(models.Model):
    short_url = models.URLField(
        max_length=191,
        unique=True
    )
    title = models.CharField(
        unique=True,
        max_length=191,
        blank=True
    )
    recorded = models.DateField(
        blank=True,
        null=True
    )
    youtube_id = models.CharField(
        max_length=64,
        unique=True,
        blank=True
    )
    api_url = models.URLField(
        max_length=191,
        blank=True,
        unique=True
    )
    embed_url = models.CharField(
        max_length=191,
        unique=True,
        blank=True
    )
    thumbnail_url = models.URLField(
        max_length=191,
        blank=True,
        unique=True
    )
    duration = models.PositiveSmallIntegerField(
        blank=True,
    )
    duration_string = models.CharField(
        blank=True,
        max_length=32
    )
    views_count = models.IntegerField(default=0)
    likes_count = models.IntegerField(default=0)
    dancing_style = models.ForeignKey(
        "DancingStyle",
        on_delete=models.CASCADE,
    )
    dancing_level = models.ForeignKey(
        "DancingLevel",
        on_delete=models.CASCADE
    )
    difficulty_level = models.ForeignKey(
        "DifficultyLevel",
        on_delete=models.CASCADE
    )
    dancer1 = models.CharField(
        default="Adán",
        max_length=128
    )
    dancer2 = models.CharField(
        default="Nelisa",
        max_length=128,
        blank=True
    )
    song = models.ForeignKey(
        "Song",
        blank=True,
        null=True,
        on_delete=models.SET_NULL
    )
    likes = models.ManyToManyField(
        "EndUser",
        blank=True
    )

    def __str__(self):
        return self.title

    def __set_random_title__(self):
        while (True):
            title = requests.get(settings.NAMES_URL).text
            if not Video.objects.filter(title=title):
                return title

    def save(self, *args, **kwargs):
        if self.pk is None:
            new_video = True
        else:
            new_video = False

        self.youtube_id = \
            re.match(r"^https?://youtu.be/(.*)$", self.short_url).group(1)
        self.api_url = \
            "https://www.googleapis.com/youtube/v3/videos?id={}&key={}&"\
            "part=snippet,contentDetails,statistics,status".format(
                self.youtube_id,
                settings.GOOGLE_API
            )
        self.embed_url = \
            "//www.youtube.com/embed/{}?rel=0&autoplay=1&showinfo=0".format(
                self.youtube_id
            )
        data = json.loads(requests.get(self.api_url).text)
        self.thumbnail_url = \
            data["items"][0]["snippet"]["thumbnails"]["medium"]["url"]
        self.duration_string = \
            data["items"][0]["contentDetails"]["duration"][2:].lower()
        r = re.match(
            r"^((?P<minutes>\d+)m)?((?P<seconds>\d+)s)?",
            self.duration_string
        )
        self.duration = int(r.group("minutes") or 0) * 60 +\
            int(r.group("seconds") or 0)
        if not self.recorded:
            published_at = data["items"][0]["snippet"]["publishedAt"]
            published_at = re.sub(r"\..*", "", published_at).replace("T", " ")
            self.recorded = dateparser.parse(published_at)
        if not self.title:
            self.title = self.__set_random_title__()

        super(Video, self).save(*args, **kwargs)

        if new_video:
            url = "http://susikiu.es{}".format(
                reverse("video", args=[self.id])
            )
            emails = list(EndUser.objects.all().values_list(
                "user__email",
                flat=True)
            )
            settings.RQ.enqueue(
                send_new_video_email,
                self.title,
                url,
                emails
            )

    @property
    def music(self):
        return "{} - {}".format(self.song.title, self.song.artist)

    @property
    def debug_embed_url(self):
        return re.sub(r"autoplay=1", "autoplay=0", self.embed_url)

    def get_siblings_video_ids(self, videos):
        try:
            videos = list(videos)
            # next
            i = videos.index(self)
            if i == (len(videos) - 1):
                next_video = videos[0]
            else:
                next_video = videos[i + 1]
            # previous
            prev_video = videos[videos.index(self) - 1]
        except IndexError:
            return self.get_siblings_video_ids(
                Video.objects.all().order_by("-recorded", "title")
            )
        return (prev_video.id, next_video.id)
