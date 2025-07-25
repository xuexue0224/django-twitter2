from testing.testcases import TestCase
from accounts.models import UserProfile

# Create your tests here.

class UserProfileTests(TestCase):

    def setUp(self):
        self.clear_cache()

    def test_profile_property(self):
        linghu = self.create_user('linghu')
        self.assertEqual(UserProfile.objects.count(), 0)
        p = linghu.profile
        self.assertEqual(isinstance(p, UserProfile), True)
        self.assertEqual(UserProfile.objects.count(), 1)
