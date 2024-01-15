"""
test for user api
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL=reverse('user:create')

def create_user(**params):
    """create and return a new user"""
    return get_user_model().objects.create_user(**params)


class PublicUserApiTests(TestCase):
    """test public features of user api"""

    def setUp(self):
        self.client=APIClient()

    def test_create_user_successfull(self):
        "test creating a user is successfull"
        payload={
            'email':'test@test.com',
            'password':'testpass123',
            'name':'test name'
        }
        
        res=self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_201_CREATED)
        user=get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password',res.data)

    def test_user_with_email_exists(self):
        """check for user with email alrdy exists"""
        payload={
            'email':'test@test.com',
            'password':'testpass123',
            'name':'test name'
        }
        create_user(**payload)
        res=self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """check if password is too short"""
        payload={
            'email':'test@test.com',
            'password':'tes',
            'name':'test name'
        }
        res=self.client.post(CREATE_USER_URL,payload)

        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)
        user_exists=get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)