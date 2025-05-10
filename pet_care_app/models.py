from django.db import models
from django.utils import timezone
from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin, BaseUserManager
from django.core.exceptions import ValidationError
from datetime import date
from django.db.models import Q

SEX_CHOICES = (
    ('MALE', 'Чоловіча'),
    ('FEMALE', 'Жіноча'),
)

TYPE_CHOICES = (
    ('CHECKUP', 'Огляд у ветеринара'),
    ('VACCINATION', 'Вакцинація'),
    ('FLEA_CTRL', 'Обробка від бліх/кліщів'),
    ('GROOMING', 'Грумінг'),
    ('BATH', 'Купання'),
    ('TRAINING', 'Тренування'),
    ('OTHER', 'Інше'),
)

PARTNER_TYPES = [
    ('CLINIC', 'Ветеринарна клініка'),
    ('GROOMING_SALON', 'Грумінг-салон'),
    ('PET_STORE', 'Зоомагазин'),
]


def validate_birthday(value):
    if value > date.today():
        raise ValidationError(
            'Дата народження не може бути в майбутньому.'
        )
    if value.year < 1950:
        raise ValidationError(
            'Рік народження не може бути раніше 1950-го.'
        )


class SitePartner(models.Model):
    site_url = models.URLField(max_length=255)
    site_name = models.CharField(max_length=255)
    partner_type = models.CharField(max_length=20, choices=PARTNER_TYPES, default='PET_STORE')
    rating = models.DecimalField(max_digits=3, decimal_places=1, default=0.0)
    photo_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return self.site_name

    class Meta:
        db_table = 'SitePartner'


class CustomUserManager(BaseUserManager):
    def create_user(self, email, password=None, full_name=None, **extra_fields):
        if not email:
            raise ValueError("Електронна пошта обов'язкова")
        if not full_name:
            raise ValueError("Повне ім’я обов'язкове")
        email = self.normalize_email(email)
        user = self.model(email=email, full_name=full_name, **extra_fields)
        user.set_password(password)
        user.save(using=self._db)
        return user

    def create_superuser(self, email, password, full_name=None, **extra_fields):
        extra_fields.setdefault('is_staff', True)
        extra_fields.setdefault('is_superuser', True)

        if not full_name:
            raise ValueError("Суперкористувач повинен мати full_name")

        return self.create_user(
            email=email,
            password=password,
            full_name=full_name,
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
        db_table = 'User'


class PartnerWatchlist(models.Model):
    user = models.ForeignKey(
        User,
        related_name='partner_watchlist',
        on_delete=models.CASCADE
    )
    partner = models.ForeignKey(
        SitePartner,
        related_name='in_watchlists',
        on_delete=models.CASCADE
    )

    class Meta:
        unique_together = ('user', 'partner')
        db_table = 'SitePartnerWatchlist'


class Pet(models.Model):
    user = models.ForeignKey(User, related_name='pets', on_delete=models.CASCADE)
    pet_name = models.CharField(max_length=255)
    breed = models.CharField(max_length=255)
    sex = models.CharField(max_length=8, choices=SEX_CHOICES, default='FEMALE')
    birthday = models.DateField(validators=[validate_birthday])
    photo_url = models.URLField(max_length=255, blank=True, null=True)

    def __str__(self):
        return f'{self.pet_name} ({self.breed})'

    class Meta:
        db_table = 'Pet'


class CalendarEvent(models.Model):
    pet = models.ForeignKey(Pet, related_name='calendar_events', on_delete=models.CASCADE)
    event_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='OTHER')
    event_title = models.CharField(max_length=255)
    start_date = models.DateField(default=timezone.now)
    start_time = models.TimeField(blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    completed = models.BooleanField(default=False)

    def __str__(self):
        return f'{self.event_title} on {self.start_date}'

    class Meta:
        db_table = 'CalendarEvent'


class JournalEntry(models.Model):
    pet = models.ForeignKey(Pet, related_name='journal_entries', on_delete=models.CASCADE)
    entry_type = models.CharField(max_length=20, choices=TYPE_CHOICES, default='OTHER')
    entry_title = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    description = models.TextField(blank=True, null=True)

    def __str__(self):
        return self.entry_title

    class Meta:
        db_table = 'JournalEntry'


class ForumPost(models.Model):
    user = models.ForeignKey(User, related_name='forum_posts', on_delete=models.CASCADE)
    post_text = models.TextField(blank=True, null=True)
    photo_url = models.URLField(max_length=255, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Post #{self.id} by {self.user.full_name}'

    class Meta:
        db_table = 'ForumPost'


class ForumComment(models.Model):
    forum_post = models.ForeignKey(ForumPost, related_name='comments', on_delete=models.CASCADE)
    user = models.ForeignKey(User, related_name='forum_comments', on_delete=models.CASCADE)
    comment_text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f'Comment #{self.id} by {self.user.full_name}'

    class Meta:
        db_table = 'ForumComment'


class ForumLike(models.Model):
    user = models.ForeignKey(User, related_name='forum_likes', on_delete=models.CASCADE)
    forum_post = models.ForeignKey(ForumPost, related_name='likes', on_delete=models.CASCADE)

    def __str__(self):
        return f'Like #{self.id} by {self.user.full_name}'

    class Meta:
        db_table = 'ForumLike'
