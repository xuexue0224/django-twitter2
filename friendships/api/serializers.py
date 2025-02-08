from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError


# 可以通过 source=xxx 制定去访问每个 model instance 的 xxx 方法
# 即 model_instance.xxx 来获得数据
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source = 'from_user')
    created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        # when the above from_user(1) started to follow another user.
        # the user in the fields below is (1)
        fields = ('user', 'created_at')