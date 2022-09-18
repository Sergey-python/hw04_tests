from typing import Dict, Union

from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.db.models.query import QuerySet
from django.http import HttpResponse
from django.shortcuts import render, get_object_or_404, redirect

from .forms import PostForm
from .models import Post, Group, User


POSTS_ON_PAGE: int = 10


def get_page_obj(request, queryset: QuerySet) -> Paginator:
    """Get page_obj from QuerySet"""
    paginator: Paginator = Paginator(queryset, POSTS_ON_PAGE)
    page_num: int = request.GET.get('page')
    return paginator.get_page(page_num)


def index(request) -> HttpResponse:
    """Rendering posts page."""
    posts: QuerySet = Post.objects.select_related('author', 'group')
    page_obj: Paginator = get_page_obj(request, posts)

    context: Dict[str, Paginator] = {'page_obj': page_obj}
    return render(request, 'posts/index.html', context)


def group_posts(request, slug: str) -> HttpResponse:
    """Rendering group posts page."""
    group: Union[Group, HttpResponse] = get_object_or_404(Group, slug=slug)
    posts: QuerySet = group.posts.select_related('author')
    page_obj: Paginator = get_page_obj(request, posts)

    context: Dict[str, Union[Group, Paginator]] = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request, 'posts/group_list.html', context)


def profile(request, username: str) -> HttpResponse:
    """Rendering profile page."""
    author: Union[User, HttpResponse] = get_object_or_404(User,
                                                          username=username)
    posts: QuerySet = author.posts.select_related('group')
    page_obj: Paginator = get_page_obj(request, posts)

    context: Dict[str, Union[User, Paginator]] = {
        'author': author,
        'page_obj': page_obj,
    }
    return render(request, 'posts/profile.html', context)


def post_detail(request, post_id: int) -> HttpResponse:
    """Rendering post detail page."""
    post: Union[Post, HttpResponse] = get_object_or_404(
        Post.objects.select_related('group', 'author'),
        id=post_id
    )
    context: Dict[str, Post] = {'post': post}
    return render(request, 'posts/post_detail.html', context)


@login_required
def post_create(request):
    """Creating post form."""
    form: PostForm = PostForm(request.POST or None)
    if form.is_valid():
        new_post: PostForm = form.save(commit=False)
        new_post.author = request.user
        new_post.save()
        return redirect('posts:profile', request.user.username)
    context: Dict[str, PostForm] = {'form': form}
    return render(request, 'posts/create_post.html', context)


@login_required
def post_edit(request, post_id: int):
    """Editing post form."""
    post: Union[Group, HttpResponse] = get_object_or_404(Post, id=post_id)
    if post.author != request.user:
        return redirect(post)
    is_edit: bool = True
    form: PostForm = PostForm(request.POST or None, instance=post)
    if form.is_valid():
        form.save()
        return redirect(post)
    context: Dict[str, Union[PostForm, bool]] = {
        'is_edit': is_edit,
        'form': form
    }
    return render(request, 'posts/create_post.html', context)
