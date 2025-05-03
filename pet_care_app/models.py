from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager

SEX_CHOICES = (
    ('MALE', 'Чоловіча'),
    ('FEMALE', 'Жіноча'),
)


class SitePartner(models.Model):
    site_url = models.URLField(max_length=255)
    site_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    photo_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.site_name


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, full_name=None, **extra_fields):
        if not email:
            raise ValueError("Електронна пошта обов'язкова")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, full_name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        return self.create_user(
            email,
            password,
            full_name=None,
            **extra_fields
        )


class User(AbstractBaseUser, PermissionsMixin):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    photo_url = models.URLField(max_length=255, blank=True, null=True)
    # password = models.TextField()

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['full_name']

    objects = CustomUserManager()

    def __str__(self):
        return self.full_name or self.email

    class Meta:
        db_table = 'user'


class Pet(models.Model):
    user = models.ForeignKey(User, related_name='pets', on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=255)
    breed = models.CharField(max_length=255)
    sex = models.CharField(max_length=8, choices=SEX_CHOICES, default='FEMALE')
    birthday = models.DateField()
    photo_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.pet_name} ({self.breed})'


class CalendarEvent(models.Model):
    pet = models.ForeignKey(Pet, related_name='calendar_events', on_delete=models.CASCADE)
    event_title = models.CharField(max_length=255)
    start_date = models.DateField(blank=True, null=True)
    start_time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return f'{self.event_title} on {self.start_date}'


class JournalEntry(models.Model):
    pet = models.ForeignKey(Pet, related_name='journal_entries', on_delete=models.CASCADE)
    entry_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.entry_title


class ForumPost(models.Model):
    user = models.ForeignKey(User, related_name='forum_posts', on_delete=models.CASCADE)
    post_text = models.TextField()
    photo_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Post #{self.id} by {self.user.full_name}'


class ForumComment(models.Model):
    forum_post = models.ForeignKey(ForumPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='forum_comments', on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment #{self.id} by {self.user.full_name}'


class ForumLike(models.Model):
    user = models.ForeignKey(User, related_name='forum_likes', on_delete=models.CASCADE)
    forum_post = models.ForeignKey(ForumPost, related_name='likes', on_delete=models.CASCADE)

    def __str__(self):
        return f'Like #{self.id} by {self.user.full_name}'
