from django.test import TestCase
from django.contrib.auth import get_user_model

from posts.models import Group, Post


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
