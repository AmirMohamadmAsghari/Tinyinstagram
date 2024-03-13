from django.db import models


class User(models.Model):
    pass


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True)
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True,null=True)


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class OTP(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    otp_code = models.IntegerField()
    expiration_time = models.DateTimeField()
