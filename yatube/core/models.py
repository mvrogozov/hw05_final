from django.db import models


class CreatedModel(models.Model):
    """Abstract model. Add creation date."""
    created = models.DateTimeField(
        'Дата создания',
        auto_now_add=True,
        help_text='Дата создания'
    )

    class Meta:
        abstract = True
