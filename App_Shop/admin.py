from django.contrib import admin
from . import models

# Register your models here.

class ProductAdmin(admin.ModelAdmin):
    list_display = ['name' , 'price' , ]
    list_editable = ['price', ]
    search_fields = ['name__istartswith']
    list_filter = [ 'price']



admin.site.register(models.Product , ProductAdmin)
