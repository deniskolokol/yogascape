from django.db import models
from django.contrib.contenttypes.models import ContentType

from core.models import NamedUserModel, TaggedUserItem


class Sequence(NamedUserModel):
    """
    Ordered sequence of elements from a particular TaggedModel,
    created by a certain user.
    """
    order = models.PositiveSmallIntegerField()
    element = models.ForeignKey(TaggedUserItem, on_delete=models.CASCADE)
