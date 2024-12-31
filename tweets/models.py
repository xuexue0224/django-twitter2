from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from datetime import datetime
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

    @property
    def hours_to_now(self):
        return (utc_now()-self.created_at).seconds // 3600

    def __str__(self):
        return f'{self.created_at} {self.user}: {self.content}'