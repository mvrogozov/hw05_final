from django.contrib.auth.forms import UsernameField
from django.contrib.auth.tokens import default_token_generator
from django.forms.fields import CharField, EmailField
from django.test import Client, TestCase
from django.urls import reverse
from django.utils.encoding import force_bytes
from django.utils.http import urlsafe_base64_encode

from posts.models import User


class UserPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.TEMPLATES_NAMES = {
            reverse('users:signup'): 'users/signup.html',
            reverse('users:login'): 'users/login.html',
            reverse('users:password_change'):
            'users/password_change_form.html',
            reverse('users:password_change_done'):
            'users/password_change_done.html',
            reverse('users:password_reset'):
            'users/password_reset_form.html',
            reverse('users:password_reset_done'):
            'users/password_reset_done.html',
            reverse(
                'users:password_reset_confirm',
                kwargs={
                    'uidb64': urlsafe_base64_encode(force_bytes(cls.user)),
                    'token': default_token_generator.make_token(cls.user)}
            ): 'users/password_reset_confirm.html',
            reverse('users:password_reset_complete'):
            'users/password_reset_complete.html',
            reverse('users:logout'): 'users/logged_out.html',
        }

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        """User pages uses correct template"""
        for address, template in self.TEMPLATES_NAMES.items():
            with self.subTest(page=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_signup_form_context(self):
        """Test user signup context contains form"""
        response = self.authorized_client.get(reverse('users:signup'))
        form_fields = {
            'first_name': CharField,
            'last_name': CharField,
            'username': UsernameField,
            'email': EmailField
        }
        for value, expected in form_fields.items():
            with self.subTest(field=value):
                self.assertTrue(value in response.context.get('form').fields)
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)
