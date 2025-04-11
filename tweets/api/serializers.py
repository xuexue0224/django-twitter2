from rest_framework import serializers
from tweets.models import Tweet
from accounts.api.serializers import UserSerializerForLike
from comments.api.serializers import CommentSerializer
from likes.services import LikeService
from likes.api.serializers import LikeSerializer


class TweetSerializer(serializers.ModelSerializer):
    user = UserSerializerForLike()
    comments_count = serializers.SerializerMethodField()
    likes_count = serializers.SerializerMethodField()
    has_liked = serializers.SerializerMethodField()

    class Meta:
        model = Tweet
        # id of a tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments_count',
            'likes_count',
            'has_liked',
        )

    def get_likes_count(self, obj):
        return obj.like_set.count()

    def get_comments_count(self, obj):
        return obj.comment_set.count()

    def get_has_liked(self, obj):
        return LikeService.has_liked(self.context['request'].user, obj)


class TweetSerializerForDetail(TweetSerializer):
    # <HOMEWORK> 使用 serializer.SerializerMethodField 的方式实现 comments
    comments = CommentSerializer(source='comment_set', many=True)
    likes = LikeSerializer(source='like_set', many=True)

    class Meta:
        model = Tweet
        fields = (
            'id',
            'user',
            'created_at',
            'content',
            'comments',
            'likes',
            'likes_count',
            'comments_count',
            'has_liked',
        )


class TweetSerializerForCreate(serializers.ModelSerializer):
    content = serializers.CharField(min_length = 6, max_length = 140)

    class Meta:
        model = Tweet
        fields = ('content',)

    def create(self, validated_data):
        user = self.context['request'].user
        content = validated_data['content']
        tweet = Tweet.objects.create(user=user, content=content)
        return tweet