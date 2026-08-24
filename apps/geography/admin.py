from django.contrib import admin
from .models import Country, Province, City
admin.site.register([Country, Province, City])
