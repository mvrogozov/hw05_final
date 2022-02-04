from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

User = get_user_model()

TEMPLATES_URL_NAMES = {
    '/auth/signup/': 'users/signup.html',
    '/auth/login/': 'users/login.html',
    '/auth/password_change/': 'users/password_change_form.html',
    '/auth/password_change/done/': 'users/password_change_done.html',
    '/auth/password_reset/': 'users/password_reset_form.html',
    '/auth/password_reset/done/': 'users/password_reset_done.html',
    '/auth/reset/<uidb64>/<token>/':
    'users/password_reset_confirm.html',
    '/auth/reset/done/': 'users/password_reset_complete.html',
    '/auth/logout/': 'users/logged_out.html',
}


class UserURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_url_are_ok(self):
        """User app urls status test"""
        for address in TEMPLATES_URL_NAMES.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_template(self):
        """Users app urls correct template"""
        for address, template in TEMPLATES_URL_NAMES.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
