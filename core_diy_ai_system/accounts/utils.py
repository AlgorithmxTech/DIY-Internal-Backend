from django.core.mail import send_mail
from django.core import signing
from django.conf import settings
from django.template.loader import render_to_string
from django.urls import reverse

# def send_password_reset_email(email, reset_link):
#     send_mail(
#         'Password Reset Request',
#         f'Click the following link to reset your password: {reset_link}',
#         'from@yourdomain.com',
#         [email],
#         fail_silently=False,
#     )

def generate_verification_link(user):
    """Generate a signed verification token that expires in 24 hours"""
    data = {
        'user_id': user.id,
        'email': user.email
    }
    # Create a signed token that expires in 24 hours (86400 seconds)
    token = signing.dumps(data, salt='email-verification', compress=True)
    
    # Generate the full verification URL
    verification_url = f"{settings.BACKEND_URL}{reverse('verify-email-confirm')}?token={token}"
    
    return verification_url


# def send_verification_email(user, token):
#     verification_link = f"{settings.FRONTEND_URL}/verify-email/{token}"
    
#     # Email content
#     subject = 'Verify Your Email Address'
#     html_message = render_to_string('accounts/emails/verify_email.html', {
#         'user': user,
#         'verification_link': verification_link
#     })
#     plain_message = f"""
#     Hi {user.username},
    
#     Please verify your email address by clicking the link below:
#     {verification_link}
    
#     This link will expire in 24 hours.
    
#     If you didn't register for an account, please ignore this email.
#     """
    
#     # Send email
#     try:
#         send_mail(
#             subject=subject,
#             message=plain_message,
#             from_email=settings.DEFAULT_FROM_EMAIL,
#             recipient_list=[user.email],
#             html_message=html_message,
#             fail_silently=False,
#         )
#         return True
#     except Exception as e:
#         print(f"Email sending failed: {str(e)}")  # Log this in production
#         return False

def send_verification_email(user):
    verification_link = generate_verification_link(user)
    
    context = {
        'user': user,
        'verification_link': verification_link
    }
    
    html_message = render_to_string('accounts/emails/verify_email.html', context)
    plain_message = render_to_string('accounts/emails/verify_email.txt', context)

    
    try:
        send_mail(
            subject='Verify Your Email Address',
            message=plain_message,
            from_email=settings.DEFAULT_FROM_EMAIL,
            recipient_list=[user.email],
            html_message=html_message,
            fail_silently=False,
        )
        return True, verification_link
    except Exception as e:
        return False, str(e)