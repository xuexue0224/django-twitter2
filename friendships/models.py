from django.db import models
from django.contrib.auth.models import User

# Create your models here.

# from user 关注了 to user
class Friendship(models.Model):
    from_user = models.ForeignKey(
        User,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'following_friendship_set',
    )
    to_user = models.ForeignKey(
        User,
        on_delete = models.SET_NULL,
        null = True,
        related_name = 'follower_friendship_set',
    )
    created_at = models.DateTimeField(auto_now_add = True)

    class Meta:
        index_together = (
            # 获取我关注的所有人，按照关注时间排序
            ('from_user_id', 'created_at'),
            # 获取关注我的所有人，按照关注时间排序，我是这里的 to_user_id
            ('to_user_id', 'created_at'),
        )
        unique_together =(('from_user_id', 'to_user_id'),)

    def __str__(self):
        return '{} followed {}'.format(self.from_user_id, self.to_user_id)