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
        post = self.post
        group = self.group
        model_objects = {
            'Post': {'obj_name': str(post), 'expected_value': post.text[:15]},
            'Group': {'obj_name': str(group), 'expected_value': group.title}
        }
        for model_name, object in model_objects.items():
            with self.subTest(model_name=model_name):
                self.assertEqual(object['obj_name'],
                                 object['expected_value'])
