from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import (    
    User, 
    EmailVerificationToken, 
    UserSession, 
    FailedLoginAttempt, 
    PasswordResetToken,
    UserRegistrationInfo,
    UserDeviceInfo
)

# Register your models here.
admin.site.register(User, UserAdmin)
admin.site.register(EmailVerificationToken)
admin.site.register(UserSession)
admin.site.register(FailedLoginAttempt)
admin.site.register(PasswordResetToken)
admin.site.register(UserRegistrationInfo)
admin.site.register(UserDeviceInfo)