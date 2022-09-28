from django.contrib import admin

from .models import TaggedUserItem, ScoredItem, Score


def admin_method_attrs(**outer_kwargs):
    """
    Wrap an admin method with passed arguments as attributes and values
    (for common admin manipulation such as setting short_description, etc.)
    """
    def method_decorator(func):
        for kw, arg in outer_kwargs.items():
            setattr(func, kw, arg)
        return func
    return method_decorator


def pict_or_name(obj):
    try:
        return obj.content_object.pict_100x100
    except AttributeError:
        return obj


class ScoreAdmin(admin.ModelAdmin):
    list_display = ("name", "minval", "maxval", "user", "privacy", )
    list_filter = ("user", "privacy", )


# XXX display scores of authenticated user (unless SU, then display all)
class ScoredItemAdmin(admin.ModelAdmin):
    list_display = ("_content_object", "score", "val", )
    ordering = ("score", "val", "object_id", )
    list_filter = ("score__name", "content_type", )

    @admin_method_attrs(short_description='object')
    def _content_object(self, obj):
        return pict_or_name(obj)


class TaggedUserItemAdmin(admin.ModelAdmin):
    list_display = ("_content_object", "name", "user", )
    ordering = ("user", "name", "object_id", )
    list_filter = ("name", "user", "content_type", )

    @admin_method_attrs(short_description='object')
    def _content_object(self, obj):
        return pict_or_name(obj)


admin.site.register(TaggedUserItem, TaggedUserItemAdmin)
admin.site.register(ScoredItem, ScoredItemAdmin)
admin.site.register(Score, ScoreAdmin)
