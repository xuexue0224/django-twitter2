# instance 代表 即将被 delete 或 create 的 instance
def invalidate_following_cache(sender, instance, **kwargs):
    from friendships.services import FriendshipService
    FriendshipService.invalidate_following_cache(instance.from_user_id)