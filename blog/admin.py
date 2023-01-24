from django.contrib import admin

# Register your models here.
from .models import User, Ticket, Review

admin.site.register(User)
admin.site.register(Ticket)
admin.site.register(Review)
