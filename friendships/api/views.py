from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework.response import Response
from friendships.models import Friendship
from friendships.api.serializers import (
    #FollowingSerializer,
    FollowerSerializer,
    #FriendshipSerializerForCreate,
)
from django.contrib.auth.models import User


class FriendshipViewSet(viewsets.GenericViewSet):
    # 我们希望 POST /api/friendship/1/follow 是去 follow user_id=1 的用户
    # 因此这里 queryset 需要是 User.objects.all()
    # 如果是 Friendship.objects.all 的话就会出现 404 not found
    # 因为 detail = true 的actions 会默认先去调用 get_object() 也就是
    # queryset.filter(pk = 1) 查询一下这个object 在不在
    queryset = User.objects.all()

    @action(methods = ['GET'], detail = True, permission_classes = [AllowAny])
    def followers(self, request, pk):
        # GET /api/friendships/1/followers/
        friendships = Friendship.objects.filter(to_user_id = pk).order_by('-created_at')
        serializer = FollowerSerializer(friendships, many = True)
        return Response(
            {'followers': serializer.data},
            status = status.HTTP_200_OK,
        )

    def list(self, request):
        return Response({'message': 'this is friendships home page'})