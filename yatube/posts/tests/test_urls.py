from http import HTTPStatus
from django.test import TestCase, Client
from django.contrib.auth import get_user_model
from django.core.cache import cache

from posts.models import Post, Group

User = get_user_model()


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.author = User.objects.create_user(username='TestAuthor')
        cls.user = User.objects.create_user(username='TestUserName')
        cls.group = Group.objects.create(
            title='TestGroup',
            slug='test_slug',
            description='TestDescription'
        )
        cls.post = Post.objects.create(
            author=cls.author,
            text='TestText',
            group=cls.group
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.author_client = Client()
        self.authorized_client.force_login(self.user)
        self.author_client.force_login(self.author)
        cache.clear()

    def test_url_exist_at_desired_location(self):
        """Доступность страниц незарегистрированным пользователем."""
        field_url_desired = {
            '/': HTTPStatus.OK,
            '/group/test_slug/': HTTPStatus.OK,
            '/profile/TestUserName/': HTTPStatus.OK,
            f'/posts/{self.post.id}/': HTTPStatus.OK,
            '/unexisting_page/': HTTPStatus.NOT_FOUND
        }
        for field, expected_value in field_url_desired.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.guest_client.get(field).status_code,
                    expected_value
                )

    def test_url_exist_at_desired_location_authorized_and_author(self):
        """Создание и редактирование поста его автором."""
        field_url_desired = {
            '/create/': HTTPStatus.OK,
            f'/posts/{self.post.id}/edit/': HTTPStatus.OK
        }
        for field, expected_value in field_url_desired.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.author_client.get(field).status_code,
                    expected_value
                )

    def test_url_redirect_guest_client(self):
        """Страницы create/ и post/edit/ перенаправят анонимного пользователя
        на страницу логина.
        """
        field_url_desired = {
            '/create/': '/auth/login/?next=/create/',
            f'/posts/{self.post.id}/edit/':
            f'/auth/login/?next=/posts/{self.post.id}/edit/'
        }
        for field, expected_value in field_url_desired.items():
            with self.subTest(field=field):
                self.assertRedirects(
                    self.guest_client.get(field, follow=True),
                    expected_value
                )

    def test_url_redirect_authorized_client(self):
        """Страница edit/ перенаправит авторизированного пользователя,
        но не автора поста на posts/<int:post_id>/.
        """
        response = self.authorized_client.get(f'/posts/{self.post.id}/edit/')
        expected_url = f'/posts/{self.post.id}/'
        self.assertRedirects(response, expected_url)

    def test_urls_uses_correct_templates(self):
        """Страницы используют правильные шаблоны."""
        templates_url_names = {
            '/': 'posts/index.html',
            '/group/test_slug/': 'posts/group_list.html',
            '/profile/TestAuthor/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
        }
        for field, template in templates_url_names.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.author_client.get(field),
                    template
                )

    def test_url_post_comment_at_guest_user(self):
        """Навторизированный при попытке оставить комментарий
        перенаправляется на страницу входа.
        """
        self.assertRedirects(
            self.guest_client.get(f'/posts/{self.post.id}/comment/'),
            f'/auth/login/?next=/posts/{self.post.id}/comment/'
        )
