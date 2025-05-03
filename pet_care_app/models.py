import bcrypt
from django.db import models
from django.utils import timezone
from django.contrib.auth.models import PermissionsMixin

SEX_CHOICES = (
    ('MALE', 'Чоловіча'),
    ('FEMALE', 'Жіноча'),
)


class SitePartner(models.Model):
    site_url = models.URLField(max_length=255)
    # site_url  = models.CharField(max_length=255)
    site_name = models.CharField(max_length=255)
    location = models.CharField(max_length=255)
    photo_url = models.URLField(max_length=255, blank=True, null=True)

    # photo_url = models.CharField(max_length=255, blank=True, null=True)
    def __str__(self):
        return self.site_name


class User(models.Model):
    full_name = models.CharField(max_length=255)
    email = models.EmailField(max_length=255, unique=True)
    photo_url = models.URLField(max_length=255, blank=True, null=True)
    hash_password = models.TextField()

    def set_password(self, raw_password):
        salt = bcrypt.gensalt()
        self.hash_password = bcrypt.hashpw(raw_password.encode(), salt).decode()

    def check_password(self, raw_password):
        return bcrypt.checkpw(raw_password.encode(), self.hash_password.encode())

    def __str__(self):
        return self.full_name


class Pet(models.Model):
    user = models.ForeignKey(User, related_name='pets', on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=255)
    breed = models.CharField(max_length=255)
    sex = models.CharField(max_length=8, choices=SEX_CHOICES, default='FEMALE')
    birthday = models.DateField()
    photo_url = models.URLField(max_length=255, blank=True, null=True)

    # photo_url = models.CharField(max_length=255, blank=True, null=True)
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
    # photo_url = models.CharField(max_length=255, blank=True, null=True)
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
