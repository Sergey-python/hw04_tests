from django.contrib.auth import get_user_model
from django.db import models
from django.urls import reverse


User = get_user_model()


class Group(models.Model):
    """Model of groups."""

    title = models.CharField(max_length=200)
    slug = models.SlugField(max_length=255, unique=True)
    description = models.TextField()

    def __str__(self) -> str:
        return self.title


class Post(models.Model):
    """Model of posts."""

    text = models.TextField()
    pub_date = models.DateTimeField(auto_now_add=True)
    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='posts'
    )
    group = models.ForeignKey(
        Group,
        on_delete=models.SET_NULL,
        blank=True,
        null=True,
        related_name='posts'
    )

    class Meta:
        ordering = ('-pub_date',)

    def __str__(self) -> str:
        return self.text[:15]

    def get_absolute_url(self):
        return reverse('posts:post_detail', kwargs={'post_id': self.id})
