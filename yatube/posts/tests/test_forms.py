import tempfile
import shutil

from django.test import TestCase, Client, override_settings
from django.contrib.auth import get_user_model
from django.urls import reverse
from django.core.files.uploadedfile import SimpleUploadedFile
from django.conf import settings

from posts.models import Post, Group, Comment

User = get_user_model()
POSTS_PER_SECOND_PAGE = 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUserAuthor')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_slug',
            description='TestDescription'
        )
        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        cls.uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)

    def check_post(self, post, form_data):
        self.assertEqual(post.text, form_data['text'])
        self.assertEqual(post.author, self.author)
        self.assertEqual(post.group.pk, form_data['group'])

    def test_create_post_form(self):
        """"Валидная форма создает запись в модели Post."""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'TestText2',
            'group': self.group.pk,
            'image': self.uploaded
        }
        response = self.author_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:profile', kwargs={'username': self.author.username}
            )
        )
        post = Post.objects.latest('pub_date')
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.check_post(post, form_data)

    def test_edit_post_form(self):
        """Валидная форма редактирует запись в модели Post."""
        self.post = Post.objects.create(
            author=self.author,
            text='TestText_1',
            group=self.group,
            image=self.uploaded
        )
        posts_count = Post.objects.count()
        form_data = {
            'text': 'EditedText',
            'group': self.group.pk
        }
        response = self.author_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(Post.objects.count(), posts_count)
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        get_object = response.context['post']
        self.check_post(get_object, form_data)


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.commentator = User.objects.create_user(username='TestUserAuthor3')
        cls.post = Post.objects.create(
            text='TestPostText',
            author=cls.commentator
        )

    def setUp(self):
        self.commentator_client = Client()
        self.commentator_client.force_login(self.commentator)

    def test_add_comment_form(self):
        """Валидная форма создает забись в модели Comment"""
        form_data = {'text': 'TestCommentTest'}
        comment_count = Comment.objects.filter(post=self.post).count()
        response = self.commentator_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post).count(),
            comment_count + 1
        )
        self.assertEqual(
            Comment.objects.get(post=self.post).text,
            form_data['text']
        )
        self.assertEqual(
            Comment.objects.get(post=self.post).author,
            self.commentator
        )
        self.assertEqual(
            Comment.objects.get(post=self.post).post,
            self.post
        )
