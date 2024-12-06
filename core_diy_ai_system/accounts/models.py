from django.contrib.auth.models import AbstractUser
from django.db import models
from django.utils import timezone

# Create your models here.
class User(AbstractUser):
    email = models.EmailField(unique=True)
    is_email_verified = models.BooleanField(default=False)
    phone_number = models.CharField(max_length=15, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']

    def __str__(self):
        return self.email

class EmailVerificationToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'expires_at'])
        ]

    def is_valid(self):
        return timezone.now() <= self.expires_at

class UserSession(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    last_activity = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        indexes = [
            models.Index(fields=['user', 'is_active'])
        ]

class FailedLoginAttempt(models.Model):
    email = models.EmailField()
    ip_address = models.GenericIPAddressField()
    timestamp = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['email', 'ip_address', 'timestamp'])
        ]

class PasswordResetToken(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    token = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()

    class Meta:
        indexes = [
            models.Index(fields=['token']),
            models.Index(fields=['user', 'expires_at'])
        ]

    def is_valid(self):
        return timezone.now() <= self.expires_at


class UserRegistrationInfo(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    ip_address = models.GenericIPAddressField()
    user_agent = models.CharField(max_length=255)
    registration_source = models.CharField(max_length=50, default='web')  # web, mobile, etc.
    registration_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending Verification'),
            ('verified', 'Email Verified'),
            ('expired', 'Verification Expired'),
        ],
        default='pending'
    )
    verification_attempts = models.IntegerField(default=0)
    last_verification_attempt = models.DateTimeField(null=True, blank=True)
    registered_at = models.DateTimeField(auto_now_add=True)
    verified_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'user_registration_info'
        indexes = [
            models.Index(fields=['registration_status']),
            models.Index(fields=['registered_at']),
        ]

    def __str__(self):
        return f"{self.user.email} - {self.registration_status}"


class UserDeviceInfo(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    device_type = models.CharField(max_length=50)  # mobile, desktop, tablet
    os_type = models.CharField(max_length=50)
    browser = models.CharField(max_length=50)
    ip_address = models.GenericIPAddressField()
    last_used = models.DateTimeField(auto_now=True)
    first_used = models.DateTimeField(auto_now_add=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'user_device_info'
        indexes = [
            models.Index(fields=['user', 'is_active']),
            models.Index(fields=['ip_address']),
        ]