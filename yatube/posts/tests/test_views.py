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

    def check_correct_post_fields(self, post):
        """Проверка полей поста."""
        self.assertEqual(post.text, 'Тестовый текст')
        self.assertEqual(post.author.username, 'HasNoName')
        self.assertEqual(post.group.title, 'Название тестовой группы')

    def check_correct_group_fields(self, group):
        """Проверка полей группы."""
        self.assertEqual(group.title, 'Название тестовой группы')
        self.assertEqual(group.slug, 'test-slug')
        self.assertEqual(group.description, 'Описание тестовой группы')

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
        post = response.context.get('page_obj')[0]
        self.check_correct_post_fields(post)

    def test_group_posts_get_correct_context(self):
        """Контекст страницы группы."""
        response = self.authorized_client.get(
            reverse('posts:group_list', args=[self.group.slug])
        )
        post = response.context.get('page_obj')[0]
        group = response.context.get('group')
        self.check_correct_post_fields(post)
        self.check_correct_group_fields(group)

    def test_profile_get_correct_context(self):
        """Контекст страницы профайла."""
        response = self.authorized_client.get(
            reverse('posts:profile', args=[self.user.username])
        )
        post = response.context.get('page_obj')[0]
        author = response.context.get('author')
        self.check_correct_post_fields(post)
        self.assertEqual(author.username, self.user.username)

    def test_post_detail_get_correct_context(self):
        """Контекст страницы поста."""
        response = self.authorized_client.get(
            reverse('posts:post_detail', args=[self.post.id])
        )
        post = response.context.get('post')
        self.check_correct_post_fields(post)

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

    def test_views_uses_correct_template(self):
        """View использует соответствующий шаблон."""
        view_names_templates = {
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
        for view, template in view_names_templates.items():
            with self.subTest(view=view):
                response = self.authorized_client.get(view)
                self.assertTemplateUsed(response, template)

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
        # капец, ну ты видал до чего смог допереть???
        post = response.context.get('page_obj').paginator.object_list.filter(
            id=self.post.id
        )
        # posts = list(filter(
        #     lambda post: post.id == self.post.id,
        #     response.context.get('page_obj')
        # ))
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

    def setUp(self):
        self.guest_client = Client()

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
