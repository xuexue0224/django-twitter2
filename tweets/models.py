from utils.memcached_helper import MemcachedHelper
from django.db import models
from django.contrib.auth.models import User
from utils.time_helpers import utc_now
from datetime import datetime
from likes.models import Like
from django.contrib.contenttypes.models import ContentType
from tweets.constants import TweetPhotoStatus, TWEET_PHOTO_STATUS_CHOICES
from django.db.models.signals import post_save, pre_delete
from utils.listeners import invalidate_object_cache
from tweets.listeners import push_tweet_to_cache


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

    @property
    def cached_user(self):
        return MemcachedHelper.get_object_through_cache(User, self.user_id)


class TweetPhoto(models.Model):
    # 图片在哪个 tweet 下面
    tweet = models.ForeignKey(Tweet, on_delete=models.SET_NULL, null=True)

    # 谁上传了这张照片，这个信息虽然可以从 tweet 中获取到，但是重复的记录在 image 里可以在
    # 使用上带来很多便利，比如某个人经常上传一些不合法的照片，那么这个人新上传的照片可以被标记
    # 为重点审查对象，或者我们需要封禁某个用户上传的所有照片的时候，就可以通过这个 model 快速
    # 进行筛选
    user = models.ForeignKey(User, null=True, on_delete=models.SET_NULL)

    # 图片文件
    file = models.FileField()
    order = models.IntegerField(default=0)

    # 图片状态，用于审核等情况
    status = models.IntegerField(
        default=TweetPhotoStatus.PENDING,
        choices=TWEET_PHOTO_STATUS_CHOICES,
    )

    # 软删除（soft delete）标记，当一个照片被删除的时候，首先会被标记为已经被删除，在一定时间之后
    # 才会被真正的删除。这样做的目的是，如果在 tweet 被删除的时候马上执行真删除的通常会花费一定的
    # 时间，影响效率。可以用异步任务在后台慢慢做真删除。
    has_deleted = models.BooleanField(default=False)
    deleted_at = models.DateTimeField(null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        index_together = (
            ('user', 'created_at'),
            ('has_deleted', 'created_at'),
            ('status', 'created_at'),
            ('tweet', 'order'),
        )

    def __str__(self):
        return f'{self.tweet_id}: {self.file}'


post_save.connect(invalidate_object_cache, sender=Tweet)
pre_delete.connect(invalidate_object_cache, sender=Tweet)
post_save.connect(push_tweet_to_cache, sender=Tweet)