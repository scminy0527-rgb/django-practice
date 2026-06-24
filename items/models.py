from django.db import models


class Item(models.Model):
    name = models.CharField(max_length=200)
    detail = models.TextField()
    stock = models.PositiveIntegerField(default=0)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    thumbnail_url = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'item'
        ordering = ['-created_at']
