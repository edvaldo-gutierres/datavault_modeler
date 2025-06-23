from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# Create your models here.

class Project(models.Model):
    name = models.CharField(max_length=100)
    description = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.name

class Hub(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='hubs')
    name = models.CharField(max_length=100)
    business_key = models.CharField(max_length=100)
    load_date = models.CharField(max_length=100, default='load_date')
    record_source = models.CharField(max_length=100, default='record_source')

    def __str__(self):
        return self.name

class Link(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='links')
    name = models.CharField(max_length=100)
    hubs = models.ManyToManyField(Hub, related_name='links')
    load_date = models.CharField(max_length=100, default='load_date')
    record_source = models.CharField(max_length=100, default='record_source')

    def __str__(self):
        return self.name

class Satellite(models.Model):
    project = models.ForeignKey(Project, on_delete=models.CASCADE, related_name='satellites')
    name = models.CharField(max_length=100)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    parent_object = GenericForeignKey('content_type', 'object_id')
    attributes = models.JSONField(default=dict)
    load_date = models.CharField(max_length=100, default='load_date')
    record_source = models.CharField(max_length=100, default='record_source')

    def __str__(self):
        return self.name

    def save(self, *args, **kwargs):
        if not self.content_type or not self.object_id:
            raise ValueError("Satellite precisa ter um Hub ou Link pai definido.")
        super().save(*args, **kwargs)
