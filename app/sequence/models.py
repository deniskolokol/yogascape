from django.db import models
from django.contrib.postgres.fields import ArrayField, HStoreField
from django.utils.translation import gettext_lazy as _

from core.models import NamedUserModel, TaggedUserItem, MARKS


MARKS_TOTAL = MARKS # Warning: update this list when adding
                    #          a new content-type.


class Sequence(NamedUserModel):
    """
    Ordered sequence of elements from a particular TaggedModel,
    created by a certain user.

    Sequence also can be categorized in some way with use of Score.
    For example if a user wants to "star" a sequence, he/she can use
    ScoredItem for this purpose (where Score would be 'stars').
    """
    pass


class SequenceItem(models.Model):
    """Sequence item (ordered)."""
    sequence = models.ForeignKey(
        Sequence,
        related_name='items',
        on_delete=models.CASCADE
        )
    order = models.PositiveSmallIntegerField()
    item = models.ForeignKey(TaggedUserItem, on_delete=models.CASCADE)
    transitional = models.BooleanField(
        default=False,
        help_text=_('Transitional items are marked with dashed arrow.')
        )
    mark = ArrayField(
       models.CharField(
           choices=MARKS_TOTAL,
           max_length=10,
           help_text=_('Anything to appear below the image.')
           ),
       default=list
       )


class SubSequence(models.Model):
    """
    Marked subsequece is for short sequences within the main Sequence,
    which should be denoted somehow different from the main flow,
    for example:

    ITEM1 ITEM2 ITEM3 ITEM4 ITEM5
          |               |
          -------L,R-------

    This can also be represented as a structure:
    [
        {
            'lr': [2, 4]
            },
        ],
    where 'lr' is a `mark`, 2 and 4 - `id`s of the first
    (ITEM2) and the last (ITEM4) SequenceItem's respectively.

    The following configurations are also supported:

    ITEM1 ITEM2 ITEM3 ITEM4 ITEM5
          |     |         ||
          |     -----X2----|
          -------L,R--------

    [
        {
            'lr': [2, 4]
            },
        {
            'x2': [3, 4]
            },
        ]

    ITEM1 ITEM2 ITEM3 ITEM4 ITEM5
    |     |   |            |
    --L,R-|----            |
          -------L,R--------

    [
        {
            'lr': [1, 2]
            },
        {
            'lr': [2, 4]
            },
        ]
    """
    sequence = models.ForeignKey(
        Sequence,
        related_name='subsequences',
        on_delete=models.CASCADE
        )
    span = ArrayField(
        models.PositiveSmallIntegerField(),
        size=2,
        help_text=_('Indises of he first and last items in the sub-sequence.')
        )
    mark = models.CharField(
       choices=MARKS_TOTAL,
       max_length=10,
       help_text=_('Sub-sequence mark.')
       )
