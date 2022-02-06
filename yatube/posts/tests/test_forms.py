import shutil
import tempfile

from django.conf import settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from posts.forms import PostForm
from posts.models import Comment, Group, Post, User

TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostCreateFormTest(TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.user_not_author = User.objects.create_user(username='not_author')
        cls.form = PostForm()
        cls.group = Group.objects.create(
            title='Test group',
            slug='test_slug'
        )
        cls.group2 = Group.objects.create(
            title='2nd group',
            slug='second'
        )
        cls.post = Post.objects.create(
            text='Test text',
            author=cls.user,
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls) -> None:
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self) -> None:
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_authorized_create_post(self):
        """Test authorized create post"""
        post_count = Post.objects.count()
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        form_data = {
            'text': 'Test text2',
            'group': self.group.id,
            'image': uploaded
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        post = Post.objects.all().order_by('-id')[0]
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.group.id, form_data['group'])
        self.assertEqual(str(post.image), 'posts/' + str(form_data['image']))
        self.assertRedirects(response, reverse(
            'posts:profile',
            kwargs={'username': self.user.username}
        )
        )

    def test_guest_create_post(self):
        """Test guest create post """
        post_count = Post.objects.count()
        form_data = {
            'text': 'anonymous text',
        }
        self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertEqual(Post.objects.count(), post_count)

    def test_authorized_edit_post(self):
        """Test authorized_edit post"""
        post = Post.objects.first()
        text_before = post.text
        form_data = {
            'text': text_before + ' new text',
            'group': self.group2.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=post.id)
        text_after = post.text
        group_after = post.group
        self.assertEqual(text_after, form_data['text'])
        self.assertEqual(group_after.id, form_data['group'])

    def test_authorized_but_not_author_edit(self):
        """Test not author edit"""
        post = Post.objects.first()
        self.authorized_client.force_login(self.user_not_author)
        text_before = post.text
        group_before = post.group
        form_data = {
            'text': text_before + ' new text',
            'group': self.group2.id
        }
        self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=post.id)
        text_after = post.text
        group_after = post.group
        self.assertEqual(text_after, text_before)
        self.assertEqual(group_after, group_before)

    def test_guest_edit_post(self):
        """Test guest edit post"""
        post = Post.objects.first()
        text_before = post.text
        group_before = post.group
        form_data = {
            'text': text_before + ' new text'
        }
        self.client.post(
            reverse('posts:post_edit', kwargs={'post_id': post.id}),
            data=form_data,
            follow=True
        )
        post = Post.objects.get(id=post.id)
        text_after = post.text
        group_after = post.group
        self.assertEqual(text_after, text_before)
        self.assertEqual(group_after, group_before)

    def test_new_user_create(self):
        """Test user creating"""
        User.objects.create_user(username='new_user')
        self.assertTrue(
            User.objects.filter(username='new_user').exists()
        )

    def test_authorized_user_comment(self):
        """Test authorized user create comment"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Test comment',
        }
        self.authorized_client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count + 1)
        last_comment = Comment.objects.all().order_by('-id')[0]
        self.assertEqual(
            last_comment.text,
            form_data['text']
        )
        self.assertEqual(last_comment.post.id, self.post.id)

    def test_guest_comment(self):
        """Test guest create comment"""
        comments_count = Comment.objects.count()
        form_data = {
            'text': 'Test comment',
        }
        self.client.post(
            reverse(
                'posts:add_comment',
                kwargs={'post_id': self.post.id}
            ),
            data=form_data,
            follow=True
        )
        self.assertEqual(Comment.objects.count(), comments_count)
