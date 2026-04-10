from django.contrib import admin
from .models import Client, Agency, Admin

admin.site.register(Client)
admin.site.register(Agency)
admin.site.register(Admin)
