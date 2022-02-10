from django.conf import settings
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Follow, Group, Post, User


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_to_follow = User.objects.create_user(username='followme')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug'
        )
        cls.empty_group = Group.objects.create(
            title='empty test group',
            slug='test_empty'
        )
        cls.post = Post.objects.create(
            text='text1',
            author=cls.user,
            group=cls.group
        )
        cls.page_objects = Post.objects.all()
        cls.PAGES_CONTEXT = {
            reverse('posts:index'): {
                'title': 'Последние обновления на сайте',
                'page_obj': cls.post,
            },
            reverse(
                'posts:profile',
                kwargs={'username': cls.post.author.username}
            ): {
                'title': 'Профайл пользователя ' + cls.post.author.username,
                'page_obj': cls.post,
                'author': cls.post.author
            },
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.post.group.slug}
            ): {
                'title': f'Записи сообщества {cls.post.group.title}',
                'page_obj': cls.post,
                'group': cls.post.group
            },
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): {
                'post': Post.objects.get(id=cls.post.id),
                'posts_total': Post.objects.filter(
                    author=cls.post.author
                ).count(),
                'title': cls.post.text[:30]
            },
            reverse(
                'posts:post_create'
            ): {
                'form': PostForm(None),
                'is_edit': False
            },
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ): {
                'form': PostForm(instance=cls.post),
                'is_edit': True
            },
        }
        cls.TEMPLATES_NAMES = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:profile',
                kwargs={'username': cls.post.author.username}
            ): 'posts/profile.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.post.group.slug}
            ): 'posts/group_list.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): 'posts/post_detail.html',
            reverse(
                'posts:post_create'
            ): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ): 'posts/create_post.html',
        }

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        cache.clear()

    def test_pages_uses_correct_template(self):
        """Post pages uses correct template"""
        for address, template in self.TEMPLATES_NAMES.items():
            with self.subTest(page=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_has_right_context(self):
        """Pages has right context"""
        for address in self.PAGES_CONTEXT.keys():
            for value, expected in self.PAGES_CONTEXT[address].items():
                with self.subTest(value=self.PAGES_CONTEXT[address]):
                    cache.clear()
                    response = self.authorized_client.get(address)
                    if value == 'page_obj':
                        elem = response.context.get(value)[0]
                        self.assertEqual(elem, expected)
                    elif value == 'form':
                        fields = response.context[value].fields
                        self.assertTrue('text' in fields)
                        self.assertTrue('group' in fields)
                    else:
                        elem = response.context.get(value)
                        self.assertEqual(elem, expected)

    def test_post_context_has_image(self):
        """Posts has image in context"""
        post_pages = (
            reverse('posts:index'),
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug}
            ),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}
            )
        )
        for page in post_pages:
            response = self.authorized_client.get(page)
            keys = response.context.keys()
            expected = self.post.image
            if 'post' in keys:
                image = response.context['post'].image
            elif 'object_list' in keys:
                image = response.context['object_list'][0].image
            self.assertEqual(image, expected)

    def test_page_form_edit_context(self):
        """Form edit has right post context"""
        response = self.authorized_client.get(reverse(
            'posts:post_edit',
            kwargs={'post_id': self.post.id}
        )
        )
        value = response.context['form']['text'].value()
        self.assertEqual(value, self.post.text)
        value = response.context['form']['group'].value()
        self.assertEqual(value, self.post.group.id)
        value = response.context['form']['image'].value()
        self.assertEqual(value, self.post.image)

    def test_post_has_only_1_group(self):
        """Post has only 1 group"""
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.empty_group.slug}
        )
        )
        self.assertEqual(len(response.context['page_obj']), 0)

    def test_authorized_user_can_follow(self):
        """Authorized user allow to follow"""
        follow_before = Follow.objects.filter(
            user=self.user, author=self.user_to_follow
        )
        self.assertFalse(follow_before.exists())
        # follow
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_to_follow.username}
        )
        )
        follow_after = Follow.objects.filter(
            user=self.user, author=self.user_to_follow
        )
        self.assertTrue(follow_after.exists)

    def test_authorized_user_can_unfollow(self):
        """Authorized user allow to unfollow"""
        Follow.objects.create(
            user=self.user,
            author=self.user_to_follow
        )
        follow_before = Follow.objects.filter(
            user=self.user,
            author=self.user_to_follow
        )
        self.assertTrue(follow_before.exists())
        self.authorized_client.get(reverse(
            'posts:profile_unfollow',
            kwargs={'username': self.user_to_follow.username}
        )
        )
        unfollow_after = Follow.objects.filter(
            user=self.user, author=self.user_to_follow
        )
        self.assertFalse(unfollow_after.exists())

    def test_new_post_in_follower_list_only(self):
        """New post presents in follower list only"""
        alone_user = User.objects.create_user(username='alone')
        follow_post = Post.objects.create(
            text='follow text',
            author=self.user_to_follow,
        )
        self.authorized_client.get(reverse(
            'posts:profile_follow',
            kwargs={'username': self.user_to_follow.username}
        )
        )
        response = self.authorized_client.get(reverse(
            'posts:follow_index',
        )
        )
        post = response.context.get('object_list')
        self.assertTrue(follow_post in post)

        # not follower list
        alone_client = Client()
        alone_client.force_login(user=alone_user)
        response = alone_client.get(reverse(
            'posts:follow_index',
        )
        )
        post = response.context.get('object_list')
        self.assertFalse(follow_post in post)


class PaginatorViewsTest(TestCase):
    """Paginator tests"""
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='test group',
            slug='test_slug'
        )
        cls.post = Post.objects.create(
            text='text1',
            author=cls.user,
            group=cls.group
        )
        cls.page_objects = Post.objects.all()
        cls.PAGES_CONTEXT = {
            reverse('posts:index'): (
                'title',
                'page_obj'
            ),
            reverse(
                'posts:profile',
                kwargs={'username': cls.post.author.username}
            ): (
                'title',
                'page_obj',
                'author'
            ),
            reverse(
                'posts:group_list',
                kwargs={'slug': cls.post.group.slug}
            ): (
                'title',
                'page_obj',
                'group'
            ),
            reverse(
                'posts:post_detail',
                kwargs={'post_id': cls.post.id}
            ): (
                'post',
                'posts_total',
                'title'
            ),
            reverse(
                'posts:post_create'
            ): (
                'form',
                'is_edit'
            ),
            reverse(
                'posts:post_edit',
                kwargs={'post_id': cls.post.id}
            ): (
                'form',
                'is_edit'
            )
        }

    def setUp(self) -> None:
        self.authorized_client = self.client
        self.authorized_client.force_login(self.user)
        for i in range(1, 15):
            Post.objects.create(
                text=f'text {i}',
                author=self.user,
                group=self.group
            )
        cache.clear()        

    def test_first_page_contains_ten_records(self):
        """Test 10 records on 1st page"""
        for address, value in self.PAGES_CONTEXT.items():
            if 'page_obj' in value:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address)
                    self.assertEqual(
                        len(response.context['page_obj']),
                        settings.POSTS_AMOUNT
                    )

    def test_second_page_contains_four_records(self):
        """Test 4 records on 2nd page"""
        for address, value in self.PAGES_CONTEXT.items():
            if 'page_obj' in value:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address + '?page=2')
                    self.assertEqual(
                        len(response.context['page_obj']),
                        Post.objects.count() % settings.POSTS_AMOUNT
                    )

    def test_post_text_on_2nd_page(self):
        """Test right text on 2nd page"""
        required_post = Post.objects.all()[settings.POSTS_AMOUNT]
        for address, value in self.PAGES_CONTEXT.items():
            if 'page_obj' in value:
                with self.subTest(address=address):
                    response = self.authorized_client.get(address + '?page=2')
                    text = response.context.get('page_obj').object_list[0].text
                    self.assertEqual(text, required_post.text)
