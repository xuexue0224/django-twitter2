from accounts.api.serializers import UserSerializerForLike
from comments.models import Comment
from django.contrib.contenttypes.models import ContentType
from likes.models import Like
from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from tweets.models import Tweet


class LikeSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike()

    class Meta:
        model = Like
        fields = ('user', 'created_at',)


class BaseLikeSerializerForCreateAndCancel(serializers.ModelSerializer):
    # verify if data received from frontend is comment or tweet
    content_type = serializers.ChoiceField(choices=['comment', 'tweet'])
    object_id = serializers.IntegerField()

    class Meta:
        model = Like
        fields = ('content_type', 'object_id',)

    def _get_model_class(self, data):
        if data['content_type'] == 'comment':
            return Comment
        if data['content_type'] == 'tweet':
            return Tweet
        return None

    def validate(self, data):
        model_class = self._get_model_class(data)
        if model_class is None:
            raise ValidationError({'content_type': 'Content type does not exist'})

        # similar to if xxxx.exists()
        # .get will report error, will return 500 error
        like_object = model_class.objects.filter(id=data['object_id']).first()
        if like_object is None:
            raise ValidationError({'object_id': 'Object does not exist'})
        return data


class LikeSerializerForCreate(BaseLikeSerializerForCreateAndCancel):
    def get_or_create(self):
        validated_data = self.validated_data
        model_class = self._get_model_class(validated_data)
        return Like.objects.get_or_create(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=validated_data['object_id'],
            user=self.context['request'].user,
        )
        #return instance


class LikeSerializerForCancel(BaseLikeSerializerForCreateAndCancel):

    def cancel(self):
        """
        cancel 仿佛是一个自定义的方法，cancel 不会被 serializer.save 调用
        所以需要直接调用 serializer.cancel()
        """
        model_class = self._get_model_class(self.validated_data)
        deleted, rows_counted = Like.objects.filter(
            content_type=ContentType.objects.get_for_model(model_class),
            object_id=self.validated_data['object_id'],
            user=self.context['request'].user,
        ).delete()
        return deleted