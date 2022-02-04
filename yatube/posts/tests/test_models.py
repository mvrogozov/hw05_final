from django.test import TestCase

from posts.models import Group, Post, User


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='test text' * 10
        )

        cls.group = Group.objects.create(
            title='test group title',
            slug='test slug',
            description='test descrption'
        )

    def test_str_post(self):
        """__str__ post equal to expected"""

        post = PostModelTest.post
        self.assertEqual(str(post), post.text[:15])

    def test_str_group(self):
        """__str__ group equal to expected"""
        group = PostModelTest.group
        self.assertEqual(str(group), group.title)

    def test_field_verbose_post(self):
        """verbose name equal to expected"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'author': 'Автор',
            'created': 'Дата создания',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_field_help_text_post(self):
        """help text equal to expected"""
        post = PostModelTest.post
        field_help = {
            'text': 'Текст поста',
            'author': 'Автор',
            'created': 'Дата создания',
            'group': 'Группа'
        }
        for field, expected_value in field_help.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )
