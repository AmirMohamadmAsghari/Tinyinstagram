from django.db import models
from user.models import User


# Create your models here.


class Post(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE,related_name='posts')
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Like(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='likes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Dislike(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='dislikes')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Tag(models.Model):
    content = models.CharField(max_length=20)
    post_id = models.ManyToManyField(Post, related_name='tag')


class Comment(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE,related_name='comments')
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    parent_comment = models.ForeignKey("self", on_delete=models.CASCADE, null=True, blank=True)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


# class Reply(models.Model):
#     parent_comment = models.ForeignKey(Comment, on_delete=models.CASCADE)
#     user = models.ForeignKey(User, on_delete=models.CASCADE)
#     content = models.TextField()
#     post = models.ForeignKey(Post, on_delete=models.CASCADE)
#

class Images(models.Model):
    post = models.ForeignKey(Post, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='media/')
