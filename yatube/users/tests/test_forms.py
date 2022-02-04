from django.test import TestCase
from django.urls import reverse

from posts.models import User


class UsersFormsTest(TestCase):
    def test_user_creating_form(self):
        users_count = User.objects.count()
        form_data = {
            'first_name': 'Petya',
            'last_name': 'Pupkin',
            'username': 'auth',
            'email': 'pupkin@goverment.ru',
            'password1': '4%fghjksL',
            'password2': '4%fghjksL'
        }
        self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(User.objects.count(), users_count + 1)
