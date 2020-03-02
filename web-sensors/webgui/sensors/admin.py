from django.contrib import admin

from .models import Node,NodeReading

# Register your models here.
admin.site.register(Node)
admin.site.register(NodeReading)