from accounts.api.serializers import UserSerializerForFriendship
from friendships.models import Friendship
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.contrib.auth.models import User


# 可以通过 source=xxx 制定去访问每个 model instance 的 xxx 方法
# 即 model_instance.xxx 来获得数据
# https://www.django-rest-framework.org/api-guide/serializers/#specifying-fields-explicitly
# 关注我的人
class FollowerSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source = 'from_user')
    #created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        # when the above from_user(1) started to follow another user.
        # they are another user's follower
        # the user in the fields below is (1)
        fields = ('user', 'created_at')


# 我关注的人
class FollowingSerializer(serializers.ModelSerializer):
    user = UserSerializerForFriendship(source='to_user')

    # created_at = serializers.DateTimeField()

    class Meta:
        model = Friendship
        # the above to_user(1)
        # the user in the fields below is (1)
        fields = ('user', 'created_at')


class FriendshipSerializerForCreate(serializers.ModelSerializer):
    from_user_id = serializers.IntegerField()
    to_user_id = serializers.IntegerField()

    class Meta:
        model = Friendship
        fields = ('from_user_id', 'to_user_id')

    def validate(self, attrs):
        if attrs['from_user_id'] == attrs['to_user_id']:
            raise ValidationError({
                'message': 'You can not follow yourself.',
            })
        """
        if Friendship.objects.filter(
            from_user_id=attrs['from_user_id'],
            to_user_id=attrs['to_user_id']
        ).exists():
            raise ValidationError({
                'message': 'You have already followed this user.',
            })
        """
        if not User.objects.filter(id=attrs['to_user_id']).exists():
            raise ValidationError({
                'message': 'You cano not follow a non-exist user.',
            })
        return attrs
    def create(self, validated_data):
        return Friendship.objects.create(
            from_user_id = validated_data['from_user_id'],
            to_user_id = validated_data['to_user_id'],
        )