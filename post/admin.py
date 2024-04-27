from django.contrib import admin
from .models import Post, Comment, PostLike, CommentLike


class PostAdmin(admin.ModelAdmin):
    list_display = ['id', 'author', 'caption', 'create_time']
    search_fields = ['author', 'caption']


class CommentAdmin(admin.ModelAdmin):
    list_display = ['author', 'post', 'comment', 'parent', 'create_time']
    search_fields = ['author', 'comment']


admin.site.register(Post, PostAdmin)
admin.site.register(Comment, CommentAdmin)
admin.site.register(PostLike)
admin.site.register(CommentLike)
