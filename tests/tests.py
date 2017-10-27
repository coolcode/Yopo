from django.test import TestCase,Client
from django.contrib.auth.models import User
from django.core.urlresolvers import reverse
import json
from yopool.repos import repos
repo = repos()

class TestLoginModel(TestCase):

    def setup(self):
        # user = User.objects.create_user("testing", "testing@yopo.com", "123456")
        # user.save()
        self.client = Client(enforce_csrf_checks=True)


    def test_login_valid(self):
        response = self.client.get(reverse('login'))
        self.assertEquals(response.status_code, 200)

        loginRight = {"username": "testing", "password": "111"}
        response = self.client.post(reverse('login'), data=loginRight, follow=True)
        self.assertEqual(response.status_code, 200)

        loginWrong = {"username": "wrong", "password": "222"}
        response = self.client.post(reverse('login'), data=loginWrong, follow=True)
        self.assertTemplateUsed(response, 'accounts/login.html')



class TestRegistrationModel(TestCase):

    def test_register_valid(self):
        response = self.client.get('/register')
        self.assertEquals(response.status_code, 200)


        user_data = {"username": "testing", "password": "333"}
        response = self.client.post('/register', data=user_data, follow=True)
        self.assertEqual(response.status_code, 200)



class TestIndexModel(TestCase):

    def test_like_valid(self):
        data = {"liked_user": "bruce"}
        response = self.client.post('/like', json.dumps(data), content_type="application/json", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_dislike_valid(self):
        data = {"disliked_user": "bruce"}
        response = self.client.post('/dislike', json.dumps(data), content_type="application/json", follow=True)
        self.assertEqual(response.status_code, 200)

    def test_send_msg_valid(self):
        data = {"chat_user": "bruce", "msg": "Test message"}
        response = self.client.post('/send_msg', json.dumps(data), content_type="application/json", follow=True)
        self.assertEqual(response.status_code, 200)


class TestInfoModel(TestCase):

    def test_info_valid(self):
        user_info = {"display_name": "testing", "sex": "male", "memo": "hello",}
        response = self.client.post('/info', data=user_info, follow=True)
        self.assertEqual(response.status_code, 200)

