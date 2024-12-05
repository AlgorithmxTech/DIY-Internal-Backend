from django.core.mail import send_mail

def send_password_reset_email(email, reset_link):
    send_mail(
        'Password Reset Request',
        f'Click the following link to reset your password: {reset_link}',
        'from@yourdomain.com',
        [email],
        fail_silently=False,
    )