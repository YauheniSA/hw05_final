from django.test import Client, TestCase


class StaticPagesURLTests(TestCase):
    def setUp(self):
        self.guest_client = Client()

    def test_about_url_exist_at_desired_location(self):
        """Проверка доступности статических адресов"""
        field_static_urls = {
            '/about/author/': 200,
            '/about/tech/': 200,
        }
        for field, expected_value in field_static_urls.items():
            with self.subTest(field=field):
                self.assertEqual(
                    self.guest_client.get(field).status_code,
                    expected_value,
                )

    def test_about_uses_correct_templates(self):
        """Проверка использования статических шаблонов"""
        field_static_templates = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }
        for field, expected_value in field_static_templates.items():
            with self.subTest(field=field):
                self.assertTemplateUsed(
                    self.guest_client.get(field),
                    expected_value,
                )
