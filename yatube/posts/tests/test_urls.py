from django.test import TestCase, Client
from django.urls import reverse
from http import HTTPStatus

from posts.models import Post, Group, User


class PostsAppURLTests(TestCase):
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
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_404_page_does_not_exist(self):
        """Запрос к несуществующей странице вернет 404."""
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_pages_available_to_guest_client(self):
        """Страницы доступные для неавторизованного пользователя."""
        urls = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
            reverse('posts:post_detail', args=[self.post.id])
        ]
        for url in urls:
            with self.subTest(url=url):
                response = self.guest_client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_pages_available_to_authorized_client(self):
        """Страницы доступные только авторизованным пользователям."""
        urls_redirect_urls = {
            reverse('posts:post_create'): '/auth/login/?next=/create/',
            reverse('posts:post_edit', args=[self.post.id]): (
                '/auth/login/?next=/posts/1/edit/'
            )
        }
        for url, redirect_url in urls_redirect_urls.items():
            with self.subTest(url=url):
                response = self.guest_client.get(url, follow=True)
                # Проверка редиректа на страницу авторизации
                self.assertRedirects(response, redirect_url)

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        urls_templates = {
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', args=[self.group.slug]): (
                'posts/group_list.html'
            ),
            reverse('posts:profile', args=[self.user.username]): (
                'posts/profile.html'
            ),
            reverse('posts:post_detail', args=[self.post.id]): (
                'posts/post_detail.html'
            ),
            reverse('posts:post_edit', args=[self.post.id]): (
                'posts/create_post.html'
            ),
            reverse('posts:post_create'): 'posts/create_post.html'
        }
        for address, template in urls_templates.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
