from django.test import TestCase

from posts.models import Group, Post, User


class PostsAppModelTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='auth')
        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='Тестовый слаг',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Какой-то текст из поста',
        )

    def test_models_have_correct_object_names(self):
        """Проверяем, что у моделей корректно работает __str__."""
        model_objects = (
            ('Post', (str(self.post), self.post.text[:15])),
            ('Group', (str(self.group), self.group.title))
        )
        for model_name, object in model_objects:
            with self.subTest(model_name=model_name):
                self.assertEqual(object[0], object[1])
