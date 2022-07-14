from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post, Comment, Follow


User = get_user_model()


class PostModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )

    def test_model_post_have_correct_object_name(self):
        """__str__ post - это строчка с содержимым post.text[:15]"""
        post = PostModelTest.post
        expected_object_text = post.text[:15]
        self.assertEqual(expected_object_text, str(post))

    def test_model_post_verbose_name(self):
        """verbose_name в модели Post совпадает с ожидаемым"""
        post = PostModelTest.post
        field_verboses = {
            'text': 'Текст поста',
            'pub_date': 'Дата публикации',
            'author': 'Автор',
            'group': 'Группа'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).verbose_name, expected_value
                )

    def test_model_post_verbose_name(self):
        """help_text в модели Post совпадает с ожидаемым"""
        post = PostModelTest.post
        field_help_text = {
            'text': 'Введите текст поста',
            'pub_date': 'Добавляется автоматически',
            'author': 'Укажите автора',
            'group': 'Выберете группу'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    post._meta.get_field(field).help_text, expected_value
                )


class GroupModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )

    def test_model_group_have_correct_object_name(self):
        """__str__ group - это строчка с содержимым group.title"""
        group = GroupModelTest.group
        expected_object_title = group.title
        self.assertEqual(expected_object_title, str(group))

    def test_model_group_verbose_name(self):
        """verbose_name в модели Group совпадает с ожидаемым"""
        group = GroupModelTest.group
        field_verboses = {
            'title': 'Название',
            'slug': 'Конвертер пути SLUG',
            'description': 'Описание',
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).verbose_name, expected_value
                )

    def test_model_post_verbose_name(self):
        """help_text в модели Group совпадает с ожидаемым"""
        group = GroupModelTest.group
        field_help_text = {
            'title': 'Не более 200 символов.',
            'slug': 'Строка из букв и цифр',
            'description': ('Текстовое поле без ограничений '
                            'по количеству символов'),
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    group._meta.get_field(field).help_text, expected_value
                )


class CommentModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
        )
        cls.comment = Comment.objects.create(
            post=cls.post,
            author=cls.user,
            text='I want to read your posts'
        )

    def test_model_comment_have_correct_object_name(self):
        """__str__ comment - это строчка с содержимым comment.text[:15]"""
        comment = CommentModelTest.comment
        expected_object_text = comment.text[:15]
        self.assertEqual(expected_object_text, str(comment))

    def test_model_comment_verbose_name(self):
        """verbose_name в модели Comment совпадает с ожидаемым"""
        comment = CommentModelTest.comment
        field_verboses = {
            'post': 'Комментарий',
            'author': 'Автор комментария',
            'text': 'Текст комменатрия',
            'created': 'Дата публикации комментария'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).verbose_name, expected_value
                )

    def test_model_comment_verbose_name(self):
        """help_text в модели Comment совпадает с ожидаемым"""
        comment = CommentModelTest.comment
        field_help_text = {
            'post': 'Оставьте Ваш комментарий',
            'author': 'Имя автора комментария',
            'text': 'Введите текст комменатрия',
            'created': ('Автоматическое добавление времени'
                        ' публикации комментария')
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    comment._meta.get_field(field).help_text, expected_value
                )


class FollowModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='follower')
        cls.author = User.objects.create_user(username='author')
        cls.follow = Follow.objects.create(
            user=cls.user,
            author=cls.author
        )

    def test_model_follow_have_correct_object_name(self):
        """__str__ foolow - это строчка с содержимым
        {self.user} подписан на {self.author}.
        """
        follow = FollowModelTest.follow
        expected_object_text = f'{self.user} подписан на {self.author}.'
        self.assertEqual(expected_object_text, str(follow))

    def test_model_follow_verbose_name(self):
        """verbose_name в модели Follow совпадает с ожидаемым"""
        follow = FollowModelTest.follow
        field_verboses = {
            'user': 'Подписчик',
            'author': 'Имена подписчиков'
        }
        for field, expected_value in field_verboses.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).verbose_name, expected_value
                )

    def test_model_follow_verbose_name(self):
        """help_text в модели Follow совпадает с ожидаемым"""
        follow = FollowModelTest.follow
        field_help_text = {
            'user': 'Имена подписчиков',
            'author': 'Имена авторов, на которых подписан'
        }
        for field, expected_value in field_help_text.items():
            with self.subTest(field=field):
                self.assertEqual(
                    follow._meta.get_field(field).help_text, expected_value
                )
