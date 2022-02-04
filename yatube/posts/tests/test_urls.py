from http import HTTPStatus
import time
from django.core.cache import cache
from django.test import Client, TestCase

from posts.models import Group, Post, User


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='authname')
        cls.user_not_author = User.objects.create_user(username='notauth')
        cls.group = Group.objects.create(
            title='test group title',
            slug='testslug',
        )
        cls.post = Post.objects.create(
            text='test text',
            author=cls.user,
            group=cls.group,
        )
        cls.post_another_auth = Post.objects.create(
            text='test2 text2',
            author=cls.user_not_author,
            group=cls.group,
        )
        cls.TEMPLATES_URL_NAME = {
            '/': 'posts/index.html',
            f'/group/{cls.group.slug}/': 'posts/group_list.html',
            f'/profile/{cls.post.author}/': 'posts/profile.html',
            f'/posts/{cls.post.id}/': 'posts/post_detail.html',
            f'/posts/{cls.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html',
            
        }

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_urls_ok(self):
        """Test urls is OK"""
        for address in self.TEMPLATES_URL_NAME.keys():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_urls_correct_template(self):
        """Posts app urls correct template"""
        for address, template in self.TEMPLATES_URL_NAME.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_post_urls_redirect_anonymous_on_login(self):
        """Redirecting anonymous user """
        redirect_url_names = {
            f'/posts/{self.post.id}/edit/':
            f'/auth/login/?next=/posts/{self.post.id}/edit/',
            '/create/': f'/auth/login/?next=/create/'
        }
        for address, redir_address in redirect_url_names.items():
            with self.subTest(address=address):
                response = self.client.get(address, follow=True)
                self.assertRedirects(
                    response, redir_address
                )

    def test_post_edit_redirect_not_author(self):
        """Redirecting authorized but not author"""
        response = self.authorized_client.get(
            f'/posts/{self.post_another_auth.id}/edit/',
            follow=True
        )
        self.assertRedirects(
            response, f'/posts/{self.post_another_auth.id}/'
        )

    def test_404(self):
        """Unexisting page"""
        response = self.client.get('/unexisting/')
        self.assertTemplateUsed(response, 'core/404.html')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_cache_page(self):
        """Page has been cached"""
        response = self.client.get('/')
        cached_post = response.context['object_list'][0].id
        cached_content = response.content
        Post.objects.get(pk=cached_post).delete()
        response = self.client.get('/')
        reload_content = response.content
        self.assertEqual(cached_content, reload_content)
        cache.clear()
        response = self.client.get('/')
        reload_content = response.content
        self.assertNotEqual(cached_content, reload_content)
