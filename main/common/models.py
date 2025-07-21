from django.db import models

# Create your models here.


# تگ ها
class Tag(models.Model):
    title = models.CharField(max_length=100, unique=True)
    slug = models.SlugField(unique=True)
    available = models.BooleanField(default=True)