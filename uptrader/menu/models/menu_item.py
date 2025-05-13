from django.db import models


class MenuItem(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    url = models.CharField(max_length=2048, null=False, blank=False)
    parent = models.ForeignKey("self", on_delete=models.CASCADE, related_name="children")
