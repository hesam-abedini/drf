"""
test for user api
"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL=reverse('user:create')
TOKEN_URL=reverse('user:token')
ME_URL=reverse('user:me')

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

    def create_token_for_user(self):

        user_details={
            'name':'hesam',
            'email':'test@example.com',
            'password':'testpass213'
        }
        create_user(**user_details)

        payload={
            'email':user_details['email'],
            'paasword':user_details['password']
        }

        res=self.client.post(TOKEN_URL,payload)

        self.assertIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_200_OK)

    def create_token_for_user_bad_cred(self):

        user_details={
            'name':'hesam',
            'email':'test@example.com',
            'password':'testpass213'
        }
        create_user(**user_details)

        payload={
            'email':'ali@gmail.com',
            'paasword':user_details['password']
        }

        res=self.client.post(TOKEN_URL,payload)

        self.assertNotIn('token',res.data)
        self.assertEqual(res.status_code,status.HTTP_400_BAD_REQUEST)

    def test_retrive_user_unathorized(self):

        res=self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_401_UNAUTHORIZED)

class PrivateUserAppiTest(TestCase):

    def setUp(self):
        
        self.user=create_user(
            email='test@test.com',
            password='testpass123',
            name='ali test'
        )
        self.client=APIClient()
        self.client.force_authenticate(user=self.user)

    def test_rerive_profile_success(self):
        
        res=self.client.get(ME_URL)

        self.assertEqual(res.status_code,status.HTTP_200_OK)
        self.assertEqual(res.data,{
            'name':self.user.name,
            'email':self.user.email
        })

    def test_post_me_not_allowed(self):

        res=self.client.post(ME_URL,{})

        self.assertEqual(res.status_code,status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        
        payload={
            'name':'updated name',
            'password':'newpassword123'
        }

        res=self.client.patch(ME_URL,payload)

        self.user.refresh_from_db()

        self.assertEqual(self.user.name,payload['name'])
        self.assertTrue(self.user.check_password(payload['password']))
        self.assertEqual(res.status_code,status.HTTP_200_OK)

