from django.db import models
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, Group, BaseUserManager
from django.utils import timezone


class CustomUserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError('The Phone field must be set')
        user = self.model(phone=phone, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)
        if extra_fields.get('is_staff') is not True:
            raise ValueError('Superuser must have is_staff=True.')
        if extra_fields.get('is_superuser') is not True:
            raise ValueError('Superuser must have is_superuser=True.')
        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    name = models.CharField(max_length=150)
    email = models.EmailField(blank=True,unique=True)
    phone = models.CharField(unique=True, max_length=11)
    otp_code = models.IntegerField(null=True)
    expiration_time = models.DateTimeField(blank=True, null=True)
    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    date_joined = models.DateTimeField(default=timezone.now)
    USERNAME_FIELD = 'phone'
    REQUIRED_FIELDS = ['name']

    objects = CustomUserManager()

    def __str__(self):
        return self.name


groups = models.ManyToManyField(Group, verbose_name='groups', blank=True,
                                help_text='The groups this user belongs to. A user will get all permissions granted '
                                          'to each of their groups.',
                                related_name="user_set", related_query_name="user")


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE, primary_key=True, related_name='profile')
    followers = models.IntegerField(default=0)
    following = models.IntegerField(default=0)
    avatar = models.ImageField(upload_to='avatars/', blank=True)
    bio = models.TextField(blank=True, null=True)


class Follow(models.Model):
    follower = models.ForeignKey(User, related_name='followers', on_delete=models.CASCADE)
    following = models.ForeignKey(User, related_name='following', on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
