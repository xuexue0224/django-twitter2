from friendships.models import Friendship
from rest_framework.test import APIClient
from testing.testcases import TestCase
from friendships.api.paginations import FriendshipPagination


FOLLOW_URL = '/api/friendships/{}/follow/'
UNFOLLOW_URL = '/api/friendships/{}/unfollow/'
FOLLOWERS_URL = '/api/friendships/{}/followers/'
FOLLOWINGS_URL = '/api/friendships/{}/followings/'


class FriendshipApiTests(TestCase):

    def setUp(self):
        self.clear_cache()
        #self.anonymous_client = APIClient()

        self.linghu = self.create_user('linghu')
        self.linghu_client = APIClient()
        self.linghu_client.force_authenticate(self.linghu)

        self.dongxie = self.create_user('dongxie')
        self.dongxie_client = APIClient()
        self.dongxie_client.force_authenticate(self.dongxie)

        # create followings and followers for dongxie
        for i in range(2):
            # 这些人关注了 dongxie
            follower = self.create_user('dongxie_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.dongxie)

            # dongxie 关注了这些人
        for i in range(3):
            following = self.create_user('dongxie_following{}'.format(i))
            Friendship.objects.create(from_user=self.dongxie, to_user=following)

    def test_follow(self):
        url = FOLLOW_URL.format(self.linghu.id)

        # 需要登录才能 follow 别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)
        # 要用 get 来 follow
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)
        # 不可以 follow 自己
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)
        # follow 成功
        response = self.dongxie_client.post(url)
        print(response.data)
        self.assertEqual(response.status_code, 201)
        self.assertEqual('created_at' in response.data, True)
        self.assertEqual('user' in response.data, True)
        self.assertEqual(response.data['user']['id'], self.linghu.id)
        self.assertEqual(response.data['user']['username'], self.linghu.username)

        # 重复 follow 会 400
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 400)
        # self.assertEqual(response.data['duplicate'], True)
        # 反向关注会创建新的数据
        count = Friendship.objects.count()
        response = self.linghu_client.post(FOLLOW_URL.format(self.dongxie.id))
        self.assertEqual(response.status_code, 201)
        self.assertEqual(Friendship.objects.count(), count + 1)

    def test_unfollow(self):
        url = UNFOLLOW_URL.format(self.linghu.id)

        # 需要登录才能 unfollow 别人
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 403)

        # 不能用 get 来 unfollow 别人
        response = self.dongxie_client.get(url)
        self.assertEqual(response.status_code, 405)

        # 不能 unfollow 自己
        response = self.linghu_client.post(url)
        self.assertEqual(response.status_code, 400)

        # unfollow 成功
        Friendship.objects.create(from_user=self.dongxie, to_user=self.linghu)
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 1)
        self.assertEqual(Friendship.objects.count(), count - 1)

        # 来 follow 的情况下 unfollow 静默处理
        count = Friendship.objects.count()
        response = self.dongxie_client.post(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.data['deleted'], 0)
        self.assertEqual(Friendship.objects.count(), count)

    def test_followings(self):
        url = FOLLOWINGS_URL.format(self.dongxie.id)

        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 3)

        # 确保按照时间倒序
        ts0 = response.data['results'][0]['created_at']
        print("\n")
        print("print ts0")

        print(ts0)
        ts1 = response.data['results'][1]['created_at']
        print("print ts1 \n")
        print(ts1)
        ts2 = response.data['results'][2]['created_at']
        print("print ts2 \n")
        print(ts2)
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(ts1 > ts2, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'dongxie_following2',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'dongxie_following1',
        )
        self.assertEqual(
            response.data['results'][2]['user']['username'],
            'dongxie_following0',
        )

    def test_followers(self):
        url = FOLLOWERS_URL.format(self.dongxie.id)

        # post is not allowed
        response = self.anonymous_client.post(url)
        self.assertEqual(response.status_code, 405)

        # get is ok
        response = self.anonymous_client.get(url)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), 2)

        # 确保按照时间倒序
        ts0 = response.data['results'][0]['created_at']
        ts1 = response.data['results'][1]['created_at']
        self.assertEqual(ts0 > ts1, True)
        self.assertEqual(
            response.data['results'][0]['user']['username'],
            'dongxie_follower1',
        )
        self.assertEqual(
            response.data['results'][1]['user']['username'],
            'dongxie_follower0',
        )

    def test_followers_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            follower = self.create_user('linghu_follower{}'.format(i))
            Friendship.objects.create(from_user=follower, to_user=self.linghu)
            if follower.id % 2 == 0:
                Friendship.objects.create(from_user=self.dongxie, to_user=follower)

        url = FOLLOWERS_URL.format(self.linghu.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous has not followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # dongxie has followed user with even id
        response = self.dongxie_client.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

    def test_followings_pagination(self):
        max_page_size = FriendshipPagination.max_page_size
        page_size = FriendshipPagination.page_size
        for i in range(page_size * 2):
            following = self.create_user('linghu_following{}'.format(i))
            Friendship.objects.create(from_user=self.linghu, to_user=following)
            if following.id % 2 == 0:
                Friendship.objects.create(from_user=self.dongxie, to_user=following)

        url = FOLLOWINGS_URL.format(self.linghu.id)
        self._test_friendship_pagination(url, page_size, max_page_size)

        # anonymous has not followed any users
        response = self.anonymous_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], False)

        # dongxie has followed users with even id
        response = self.dongxie_client.get(url, {'page': 1})
        for result in response.data['results']:
            has_followed = (result['user']['id'] % 2 == 0)
            self.assertEqual(result['has_followed'], has_followed)

        # linghu has followed all his following users
        response = self.linghu_client.get(url, {'page': 1})
        for result in response.data['results']:
            self.assertEqual(result['has_followed'], True)

    def _test_friendship_pagination(self, url, page_size, max_page_size):
        response = self.anonymous_client.get(url, {'page': 1})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        response = self.anonymous_client.get(url, {'page': 2})
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data['results']), page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 2)
        self.assertEqual(response.data['has_next_page'], False)

        response = self.anonymous_client.get(url, {'page': 3})
        self.assertEqual(response.status_code, 404)

        # test user cannot customize page_size exceeds max_page_size
        response = self.anonymous_client.get(url, {'page': 1, 'size': max_page_size + 1})
        self.assertEqual(len(response.data['results']), max_page_size)
        self.assertEqual(response.data['total_pages'], 2)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)

        # test user can customize page size by param size
        response = self.anonymous_client.get(url, {'page': 1, 'size': 2})
        self.assertEqual(len(response.data['results']), 2)
        self.assertEqual(response.data['total_pages'], page_size)
        self.assertEqual(response.data['total_results'], page_size * 2)
        self.assertEqual(response.data['page_number'], 1)
        self.assertEqual(response.data['has_next_page'], True)
