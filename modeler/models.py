from django.db import models
from django.contrib.contenttypes.fields import GenericForeignKey
from django.contrib.contenttypes.models import ContentType
from django.utils import timezone

# Create your models here.

class Hub(models.Model):
    name = models.CharField(max_length=255, unique=True)
    description = models.TextField(blank=True, null=True)
    business_keys = models.CharField(max_length=500, help_text="Campos que formam a chave de negócio, separados por vírgula.")
    load_date = models.DateTimeField(auto_now_add=True)
    record_source = models.CharField(max_length=255, default='DefaultSource')

    def __str__(self):
        return self.name

class Link(models.Model):
    name = models.CharField(max_length=255, unique=True)
    hubs = models.ManyToManyField(Hub)
    description = models.TextField(blank=True, null=True)
    load_date = models.DateTimeField(auto_now_add=True)
    record_source = models.CharField(max_length=255, default='DefaultSource')

    def __str__(self):
        return self.name

class Satellite(models.Model):
    name = models.CharField(max_length=255)
    attributes = models.TextField(help_text="Campos descritivos, separados por vírgula.")
    load_date = models.DateTimeField(auto_now_add=True)
    record_source = models.CharField(max_length=255, default='DefaultSource')
    
    # Generic relation to parent (Hub or Link)
    content_type = models.ForeignKey(ContentType, on_delete=models.CASCADE)
    object_id = models.PositiveIntegerField()
    parent = GenericForeignKey('content_type', 'object_id')

    class Meta:
        # Garante que o nome de um satélite seja único para seu pai
        unique_together = ('name', 'content_type', 'object_id')

    def __str__(self):
        return f"{self.name} (for {self.parent})"
