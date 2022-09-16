from django.contrib import admin

from genery.utils import smart_truncate

from .models import Asana, AsanaForm
from core.admin import admin_method_attrs


class AsanaAdmin(admin.ModelAdmin):
    list_display = ("name", "_note", "created", "updated", )
    ordering = ("name", "updated", )
    list_filter = ("updated", )
    search_fields = ("name", "note", )

    @admin_method_attrs(admin_order_field='body')
    def _note(self, obj):
        note = obj.note or ''
        return smart_truncate(note, 80)


class AsanaFormAdmin(admin.ModelAdmin):
    list_display = ("_pict", "_name", )
    ordering = ("asana__name", )
    search_fields = ("asana__name", )

    @admin_method_attrs(short_description='name',
                        admin_order_field='asana__name')
    def _name(self, obj):
        return obj.name

    @admin_method_attrs(short_description='pict')
    def _pict(self, obj):
        return obj.pict_100x100


admin.site.register(Asana, AsanaAdmin)
admin.site.register(AsanaForm, AsanaFormAdmin)
