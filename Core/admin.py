from django.contrib import admin
from .models import Stock, Profile, FollowChart

admin.site.register(Stock)
admin.site.register(Profile)
admin.site.register(FollowChart)
