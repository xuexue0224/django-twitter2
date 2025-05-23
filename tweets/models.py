from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from datetime import datetime
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
# Create your models here.


class Tweet(models.Model):
    user = models.ForeignKey\
        (User,
        on_delete=models.SET_NULL,
        #null: If True, Django will store blank values as NULL in the database
        # for fields where this is appropriate
        # (a CharField will instead store an empty string). The default is False.
        null=True,
        help_text = 'who posts this tweet',
        verbose_name = u'谁发了这个题',
        )
    content = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (('user', 'created_at'),)
        ordering = ('user', '-created_at')

    @property
    def hours_to_now(self):
        return (utc_now()-self.created_at).seconds // 3600

    @property
    def like_set(self):
        return Like.objects.filter(
            content_type=ContentType.objects.get_for_model(Tweet),
            object_id=self.id,
        ).order_by('-created_at')

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'