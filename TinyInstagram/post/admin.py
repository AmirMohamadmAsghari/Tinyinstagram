from django.contrib import admin
from .models import Post, Images, Tag, Comment, Dislike, Like

admin.site.register(Post)
# admin.site.register(Reply)
admin.site.register(Like)
admin.site.register(Dislike)
admin.site.register(Images)
admin.site.register(Tag)
admin.site.register(Comment)

