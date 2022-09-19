from django import forms
from django.test import TestCase, Client
from django.urls import reverse

from posts.models import Post, Group, User


class PostsAppViewTest(TestCase):
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

    def check_correct_post_fields(self, post_from_response):
        """Проверка значений полей поста."""
        self.assertEqual(post_from_response.text, self.post.text)
        self.assertEqual(
            post_from_response.author.username,
            self.post.author.username
        )
        self.assertEqual(
            post_from_response.group.id,
            self.post.group.id
        )

    def check_correct_group_fields(self, group_from_response):
        """Проверка значений полей группы."""
        self.assertEqual(group_from_response.title, self.group.title)
        self.assertEqual(group_from_response.slug, self.group.slug)
        self.assertEqual(
            group_from_response.description,
            self.group.description
        )

    def check_correct_post_form_fields(self, form):
        """Проверка типов полей формы поста."""
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = form.fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_index_get_correct_context(self):
        """Контекст главной страницы."""
        response = self.authorized_client.get(reverse('posts:index'))
        post_from_response = response.context.get('page_obj')[0]
        self.check_correct_post_fields(post_from_response)

    def test_group_posts_get_correct_context(self):
        """Контекст страницы группы."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        post_from_response = response.context.get('page_obj')[0]
        group_from_response = response.context.get('group')
        self.check_correct_post_fields(post_from_response)
        self.check_correct_group_fields(group_from_response)

    def test_profile_get_correct_context(self):
        """Контекст страницы профайла."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user.username])
        )
        post_from_response = response.context.get('page_obj')[0]
        author = response.context.get('author')
        self.check_correct_post_fields(post_from_response)
        self.assertEqual(author.username, self.user.username)

    def test_post_detail_get_correct_context(self):
        """Контекст страницы поста."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        post_from_response = response.context.get('post')
        self.check_correct_post_fields(post_from_response)

    def test_create_get_correct_context(self):
        """Контекст формы создания поста."""
        response = self.authorized_client.get(reverse('posts:post_create'))
        form = response.context.get('form')
        self.check_correct_post_form_fields(form)

    def test_post_edit_get_correct_context(self):
        """Контекст формы редактирования поста."""
        response = self.authorized_client.get(
            reverse('posts:post_edit', args=[self.post.id])
        )
        form = response.context.get('form')
        self.check_correct_post_form_fields(form)

    def test_new_post_will_appear_on_pages(self):
        """Новый пост с группой есть на страницах."""
        view_names = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
        ]
        for view in view_names:
            with self.subTest(view=view):
                response = self.authorized_client.get(view)
                post = response.context.get('page_obj')[0]
                self.assertEqual(post.id, self.post.id)

    def test_new_post_will_not_appear_on_other_group_page(self):
        """Нового поста нет на странице другой группы."""
        new_group = Group.objects.create(
            title='Название новой тестовой группы',
            slug='new-test-slug',
            description='Описание новой тестовой группы'
        )
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[new_group.slug])
        )
        post = response.context.get('page_obj').paginator.object_list.filter(
            id=self.post.id
        )
        self.assertFalse(post.exists())


class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='HasNoName')
        cls.group = Group.objects.create(
            title='Название тестовой группы',
            slug='test-slug',
            description='Описание тестовой группы'
        )
        new_posts = [
            Post(text=f'Тестовый текст {i}',
                 author=cls.user,
                 group=cls.group) for i in range(13)
        ]
        Post.objects.bulk_create(new_posts)

    def test_first_page_contains_ten_records(self):
        """На первой странице 10 постов."""
        view_names = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
        ]
        for view in view_names:
            with self.subTest(view=view):
                response = self.client.get(view)
                self.assertEqual(len(response.context['page_obj']), 10)

    def test_second_page_contains_three_records(self):
        """На второй странице оставшиейся 3 поста."""
        view_names = [
            reverse('posts:index'),
            reverse('posts:group_list', args=[self.group.slug]),
            reverse('posts:profile', args=[self.user.username]),
        ]
        for view in view_names:
            with self.subTest(view=view):
                response = self.client.get(view + '?page=2')
                self.assertEqual(len(response.context['page_obj']), 3)
