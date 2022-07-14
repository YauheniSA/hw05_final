import tempfile
import shutil

from django.test import TestCase, Client, override_settings
from django.core.files.uploadedfile import SimpleUploadedFile
from django.contrib.auth import get_user_model
from django.urls import reverse
from django import forms
from django.conf import settings
from django.core.cache import cache

from posts.models import Post, Group, Comment, Follow
from yatube.settings import POSTS_PER_PAGE


User = get_user_model()
POSTS_PER_SECOND_PAGE = 3
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostsPagesTestsContext(TestCase):
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
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='TestText',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        cache.clear()

    def check_post(self, post):
        checking_values = {
            post.author: self.post.author,
            post.text: self.post.text,
            post.group: self.post.group,
            post.image: self.post.image,
            post.comments: self.post.comments
        }
        for get_value, expected_value in checking_values.items():
            self.assertEqual(get_value, expected_value)

    def response_to_index_page(self):
        return self.author_client.get(reverse('posts:index'))

    def test_pages_uses_correct_templates(self):
        """URL-адреса приложения posts используют правильные шаблоны."""
        templates_pages_names = {
            reverse(
                'posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.post.group.slug}):
                    'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}):
                    'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.id}): 'posts/post_detail.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.id}): 'posts/create_post.html',
            reverse(
                'posts:post_create'): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.author_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_pages_with_posts_lists_show_correct_context(self):
        """Шаблоны index, group_list, profile сформированы
        с правильным контекстом.
        """
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        ]
        for url in reverse_list:
            response = self.author_client.get(url)
            first_object = response.context['page_obj'][0]
            self.check_post(first_object)

    def test_page_post_detail_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом."""
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        get_object = response.context['post']
        self.check_post(get_object)

    def test_create_and_edit_post_pages_show_correct_context(self):
        """Шаблоны create_post и edit_post сформированы
        с правильным контекстом.
        """
        reverse_list = [
            reverse('posts:post_create'),
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
        ]
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
        }
        for url in reverse_list:
            response = self.author_client.get(url)
            for value, expected in form_fields.items():
                with self.subTest(value=value):
                    form_field = response.context.get('form').fields.get(value)
                    self.assertIsInstance(form_field, expected)

    def test_post_cache(self):
        """Посты на странице index хранятся в кэше"""
        Post.objects.create(
            text='We need to check a cache',
            author=self.author
        )
        first_object = self.response_to_index_page().content
        Post.objects.filter(text='We need to check a cache').delete()
        second_object = self.response_to_index_page().content
        self.assertEqual(first_object, second_object)
        cache.clear()
        third_object = self.response_to_index_page().content
        self.assertNotEqual(first_object, third_object)


class PostsPagesTestsPaginator(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUserAuthor')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_slug',
            description='TestDescription'
        )
        for post_number in range(0, POSTS_PER_PAGE + POSTS_PER_SECOND_PAGE):
            Post.objects.create(
                author=cls.author,
                text=f'TestText number {post_number}',
                group=cls.group
            )

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.post = Post.objects.latest('pub_date')
        cache.clear()

    def test_paginator_page_contains_post_per_page_records(self):
        """Шаблоны index, group_list, profile содержат POSTS_PER_PAGE
        постов на первой странице и POSTS_PER_SECOND_PAGE
        постов на второй странице.
        """
        reverse_list = [
            reverse('posts:index'),
            reverse('posts:group_list', kwargs={'slug': self.post.group.slug}),
            reverse(
                'posts:profile',
                kwargs={'username': self.post.author.username}
            )
        ]
        for url in reverse_list:
            response_first_page = self.author_client.get(url)
            self.assertEqual(
                len(response_first_page.context['page_obj']),
                POSTS_PER_PAGE
            )
            response_second_page = self.author_client.get(url + '?page=2')
            self.assertEqual(
                len(response_second_page.context['page_obj']),
                POSTS_PER_SECOND_PAGE
            )


class FollowPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.follower = User.objects.create_user(username='TestFollower')
        cls.not_follwer = User.objects.create_user(username='Not_Follower')

    def setUp(self):
        self.author_client = Client()
        self.follower_client = Client()
        self.not_follower_client = Client()
        self.author_client.force_login(self.author)
        self.follower_client.force_login(self.follower)
        self.not_follower_client.force_login(self.not_follwer)

    def test_authorized_client_can_follow(self):
        """Авторизированный пользователь может стать подписчиком."""
        followers_count_zero = Follow.objects.count()
        self.follower_client.get(
            reverse('posts:profile_follow',
                    kwargs={'username': self.author.username}
                    )
        )
        folowwers_count_one = Follow.objects.count()
        self.assertEqual(folowwers_count_one, followers_count_zero + 1)
        new_follow = Follow.objects.latest('id')
        self.assertEqual(self.author, new_follow.author)
        self.assertEqual(self.follower, new_follow.user)

    def test_follower_can_unfollow(self):
        """Подписчик может описаться."""
        Follow.objects.create(
            user=self.follower,
            author=self.author
        )
        folowwers_count_one = Follow.objects.count()
        self.follower_client.get(
            reverse('posts:profile_unfollow',
                    kwargs={'username': self.author.username}
                    )
        )
        followers_count_unfollow = Follow.objects.count()
        self.assertEqual(followers_count_unfollow, folowwers_count_one - 1)
        self.assertFalse(Follow.objects.filter(user=self.follower).exists())

    def test_check_a_new_post_for_followers(self):
        """Новая запись пользователя появляется в ленте тех,
        кто на него подписан и не появляется в ленте тех, кто не подписан.
        """
        Follow.objects.create(
            user=self.follower,
            author=self.author
        )
        Post.objects.create(
            text='we need to test followers',
            author=self.author
        )
        follower_context = self.follower_client.get(
            reverse('posts:follow_index')
        ).context['page_obj']
        not_follower_context = self.not_follower_client.get(
            reverse('posts:follow_index')
        ).context['page_obj']
        self.assertNotEqual(
            len(follower_context),
            len(not_follower_context)
        )


class CommentTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestUserAuthor')
        cls.post = Post.objects.create(
            author=cls.author,
            text='I want to read your comments',
        )
        """cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.author,
            text='I want to read your posts'
        )"""

    def setUp(self):
        self.author_client = Client()
        self.author_client.force_login(self.author)
        self.response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )

    def add_comment(self):
        form_data = {'text': 'TestCommentTest'}
        return self.author_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )

    def test_view_add_comment_uses_correct_form(self):
        """Поля формы Comment имеют правильные значения на странице
        post_detail.
        """
        get_field = self.response.context.get('form').fields.get('text')
        expected_field = forms.fields.CharField
        self.assertIsInstance(get_field, expected_field)

    def test_view_add_comment_add_new_object_in_model(self):
        """Функция добавляет объект модели Comment в базу."""
        comment_count = Comment.objects.filter(post=self.post).count()
        response = self.add_comment()
        self.assertRedirects(
            response, reverse(
                'posts:post_detail', kwargs={'post_id': self.post.id}
            )
        )
        self.assertEqual(
            Comment.objects.filter(post=self.post).count(),
            comment_count + 1
        )

    def test_comments_are_in_context_page_post_detail(self):
        """Комментарии передаются в контексте при генерации шаблона
        post_detail.
        """
        self.add_comment()
        response = self.author_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        get_field = response.context.get('comments')[0]
        expected_field = Comment.objects.latest('id').text
        self.assertEqual(get_field.text, expected_field)
