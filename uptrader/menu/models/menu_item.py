from django.db import models
from menu.services.menu_funcs import update_parent


class MenuItem(models.Model):
    name = models.CharField(max_length=30, null=False, blank=False)
    url = models.CharField(max_length=2048, null=False, blank=False)
    parent = models.ForeignKey(
        "self",
        on_delete=models.CASCADE,
        related_name="children",
        null=True,
        blank=True,
    )

    def __str__(self) -> str:
        return f"{self.name} ({self.url})"

    def save(self, *args, **kwargs):
        is_new = not self.pk

        # Сохраняем оригинальный parent_id до сохранения
        if not is_new:
            original = MenuItem.objects.get(pk=self.pk)
            self._original_parent_id = original.parent_id
        else:
            self._original_parent_id = None

        # Если это новый объект — строим URL
        if is_new:
            if self.parent_id is not None:
                try:
                    parent = MenuItem.objects.get(pk=self.parent_id)
                    self.url = f"{parent.url}{self.name}/"
                except MenuItem.DoesNotExist:
                    raise ValueError("Parent does not exist")
            else:
                self.url = f"{self.name}/"

        # Сохраняем объект, чтобы получить pk
        super().save(*args, **kwargs)

        # Если это обновление и parent изменился — запускаем update_parent
        if not is_new and self.parent_id != self._original_parent_id:
            update_parent(menu_item_id=self.id, new_parent_id=self.parent_id)
            self.refresh_from_db()
