from django.db import models
from django.utils import timezone
from django.contrib.auth.models import User # Or 'auth.User'
from django.utils.text import slugify

class NewsItem(models.Model): # Make sure this class definition exists
    title = models.CharField(max_length=200)
    content = models.TextField()
    published_date = models.DateTimeField(default=timezone.now)
    author = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )
    slug = models.SlugField(max_length=200, unique=True, blank=True, help_text="A short label for the news item, used in URLs. Will be auto-generated if left blank.")

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-published_date']
        verbose_name = "News Item"
        verbose_name_plural = "News Items"

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            queryset = NewsItem.objects.filter(slug=self.slug)
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            while queryset.exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                queryset = NewsItem.objects.filter(slug=self.slug)
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
        super().save(*args, **kwargs)

# Your Event model should be below this
class Event(models.Model):
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True, null=True)
    start_datetime = models.DateTimeField(default=timezone.now)
    end_datetime = models.DateTimeField(blank=True, null=True, help_text="Leave blank if it's a single-day event or duration is not specific.")
    location = models.CharField(max_length=255, blank=True, null=True)
    slug = models.SlugField(max_length=250, unique_for_date='start_datetime', blank=True, help_text="A short label for the event, used in URLs. Auto-generated if blank.")
    created_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='created_events'
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['start_datetime']
        verbose_name = "Event"
        verbose_name_plural = "Events"

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
            original_slug = self.slug
            counter = 1
            queryset = Event.objects.filter(slug=self.slug, start_datetime__date=self.start_datetime.date())
            if self.pk:
                queryset = queryset.exclude(pk=self.pk)

            while queryset.exists():
                self.slug = f'{original_slug}-{counter}'
                counter += 1
                queryset = Event.objects.filter(slug=self.slug, start_datetime__date=self.start_datetime.date())
                if self.pk:
                    queryset = queryset.exclude(pk=self.pk)
        super().save(*args, **kwargs)

    @property
    def is_upcoming(self):
        return self.start_datetime > timezone.now()

    @property
    def is_past(self):
        if self.end_datetime:
            return self.end_datetime < timezone.now()
        return self.start_datetime < timezone.now()