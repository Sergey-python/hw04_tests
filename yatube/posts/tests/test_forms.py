from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


class PostsAppFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Описание тестовой группы'
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_create_post(self):
        """Пост корректно добавляется в базу."""
        posts_count = Post.objects.count()
        form_data = {'text': 'Тестовый текст2'}
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )
        # Проверка редиректа после создания
        self.assertRedirects(
            response,
            reverse('posts:profile', args=[self.user.username])
        )
        # Проверка что пост добавился в базу
        self.assertEqual(Post.objects.count(), posts_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text='Тестовый текст2',
                author=self.user
            ).exists()
        )

    def test_edit_post(self):
        """Пост корректно редактируется."""
        form_data = {'text': 'Измененный текст'}
        response = self.authorized_client.post(
            reverse('posts:post_edit', args=[self.post.id]),
            data=form_data,
            follow=True
        )
        # Проверка что пост изменился
        change_post = Post.objects.get(id=self.post.id)
        self.assertEqual(change_post.text, form_data['text'])
        # Проверка редиректа после изменения
        self.assertRedirects(
            response,
            reverse('posts:post_detail', args=[change_post.id])
        )
