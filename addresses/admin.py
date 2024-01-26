from django.contrib import admin

from addresses.models import Place


# Register your models here.
@admin.register(Place)
class PlaceAdmin(admin.ModelAdmin):
    pass
