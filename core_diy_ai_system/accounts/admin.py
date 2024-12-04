from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import User, EmailVerificationToken, UserSession
# Register your models here.


admin.site.register(User, UserAdmin)
admin.site.register(EmailVerificationToken)
admin.site.register(UserSession)