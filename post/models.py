from django.contrib.auth import get_user_model
from django.core.validators import FileExtensionValidator, MaxLengthValidator
from django.db import models
from django.db.models import UniqueConstraint

from shared.models import BaseModel

User = get_user_model()


class Post(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    image = models.ImageField(upload_to='posts/', validators=[
        FileExtensionValidator(allowed_extensions=['png', 'jpg', 'jpeg', 'heic', 'heif', 'webp'])
    ])
    caption = models.TextField(validators=[MaxLengthValidator(limit_value=1000)])

    class Meta:
        db_table = 'posts'
        ordering = ['-create_time']

    def __str__(self):
        return f"{self.author.fullname} for post {self.caption}"


class Comment(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE)
    comment = models.TextField(validators=[MaxLengthValidator(limit_value=500)])
    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='childs',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'comments'
        ordering = ['-create_time']

    def __str__(self):
        return f"{self.author.fullname} - {self.comment}"


class PostLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'post_likes'
        ordering = ['-create_time']
        constraints = [
            UniqueConstraint(
                fields=['author', 'post'],
                name='PostLikeUnique'
            )
        ]


class CommentLike(BaseModel):
    author = models.ForeignKey(User, on_delete=models.CASCADE)
    comment = models.ForeignKey(Comment, on_delete=models.CASCADE, related_name='likes')

    class Meta:
        db_table = 'comment_likes'
        constraints = [
            UniqueConstraint(
                fields=['author', 'comment'],
                name='CommentLikeUnique'
            )
        ]








