from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, Skill, Opportunity, Attendance, Badge, UserBadge

# Register the custom User model with the standard User configuration layout
admin.site.register(User, UserAdmin)

# Register the rest of your custom VMS models
admin.site.register(Skill)
admin.site.register(Opportunity)
admin.site.register(Attendance)
admin.site.register(Badge)
admin.site.register(UserBadge)
# Register your models here.
