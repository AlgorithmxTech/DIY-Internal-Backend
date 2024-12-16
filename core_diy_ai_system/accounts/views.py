from django.shortcuts import render
from django.template.loader import render_to_string
from django.core.mail import send_mail 
from rest_framework import status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework.views import APIView
from django.contrib.auth import get_user_model
from django.utils import timezone
from datetime import timedelta
from django.conf import settings
from user_agents import parse
from django.core import signing
from django.shortcuts import redirect

from .utils import send_verification_email
from .serializers import (
    UserRegistrationSerializer,
    UserSerializer,
    CustomTokenObtainPairSerializer,
    ForgotPasswordSerializer,
    ResetPasswordSerializer
)

from .models import EmailVerificationToken, PasswordResetToken, UserRegistrationInfo, UserDeviceInfo, FailedLoginAttempt

import uuid

# Create your views here.

User = get_user_model()

class RegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    permission_classes = (AllowAny,)
    serializer_class = UserRegistrationSerializer

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0]
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip
    
    def get_device_info(self, request):
        user_agent_string = request.META.get('HTTP_USER_AGENT', '')
        user_agent = parse(user_agent_string)
        
        return {
            'device_type': 'mobile' if user_agent.is_mobile else 'tablet' if user_agent.is_tablet else 'desktop',
            'os_type': f"{user_agent.os.family} {user_agent.os.version_string}",
            'browser': f"{user_agent.browser.family} {user_agent.browser.version_string}"
        }

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # create user
        user = serializer.save()

        # Get client information
        ip_address = self.get_client_ip(request)
        user_agent = request.META.get('HTTP_USER_AGENT', '')
        device_info = self.get_device_info(request)
        
        # Create registration info
        UserRegistrationInfo.objects.create(
            user=user,
            ip_address=ip_address,
            user_agent=user_agent,
            registration_source='api'  # or determine based on request
        )

        # Create device info
        UserDeviceInfo.objects.create(
            user=user,
            ip_address=ip_address,
            **device_info
        )

        # Create verification token
        token = str(uuid.uuid4())
        verification = EmailVerificationToken.objects.create(
            user=user,
            token=token,
            expires_at=timezone.now() + timedelta(hours=24)
        )
        
        # Send verification email
        email_sent, verification_info = send_verification_email(user)

        response_data = {
            'message': 'Registration successful. Please check your email to verify your account.',
            'email_status': 'sent' if email_sent else 'failed'
        }

        # In debug mode, include the verification link
        if settings.DEBUG:
            response_data['debug_info'] = {
                'verification_link': verification_info
            }
        if not email_sent:
            response_data['error'] = verification_info
        
        return Response(response_data, status=status.HTTP_201_CREATED)


class CustomTokenObtainPairView(TokenObtainPairView):
    serializer_class = CustomTokenObtainPairSerializer

    def get_client_ip(self, request):
        x_forwarded_for = request.META.get('HTTP_X_FORWARDED_FOR')
        if x_forwarded_for:
            ip = x_forwarded_for.split(',')[0].strip()
        else:
            ip = request.META.get('REMOTE_ADDR')
        return ip

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        
        try:
            serializer.is_valid(raise_exception=True)
            # If valid, return the tokens
            return Response(serializer.validated_data)
            
        except Exception as e:
            # Track failed login attempt
            email = request.data.get('email', '')
            ip_address = self.get_client_ip(request)
            
            FailedLoginAttempt.objects.create(
                email=email,
                ip_address=ip_address
            )
            
            # You can add logic here to check for multiple failed attempts
            recent_failures = FailedLoginAttempt.objects.filter(
                email=email,
                ip_address=ip_address,
                timestamp__gte=timezone.now() - timezone.timedelta(hours=24)
            ).count()
            
            # Return error response
            error_message = 'Invalid email or password'
            if recent_failures >= 5:  # You can adjust this threshold
                error_message = 'Too many failed attempts. Please try again later.'
                
            return Response(
                {'detail': error_message},
                status=status.HTTP_401_UNAUTHORIZED
            )

# class VerifyEmailView(APIView):
#     permission_classes = (AllowAny,)

#     def post(self, request):
#         token = request.data.get('token')
#         try:
#             verification = EmailVerificationToken.objects.get(
#                 token=token,
#                 expires_at__gt=timezone.now()
#             )
#             user = verification.user
#             user.is_email_verified = True
#             user.save()

#             # Update registration info
#             registration_info = UserRegistrationInfo.objects.get(user=user)
#             registration_info.registration_status = 'verified'
#             registration_info.verified_at = timezone.now()
#             registration_info.save()

#             verification.delete()

#             return Response({'message': 'Email verified successfully'})

#         except EmailVerificationToken.DoesNotExist:
#             # Track failed verification attempt
#             try:
#                 verification = EmailVerificationToken.objects.get(token=token)
#                 registration_info = UserRegistrationInfo.objects.get(user=verification.user)
#                 registration_info.verification_attempts += 1
#                 registration_info.last_verification_attempt = timezone.now()
#                 registration_info.save()
#             except (EmailVerificationToken.DoesNotExist, UserRegistrationInfo.DoesNotExist):
#                 pass
                
#             return Response(
#                 {'error': 'Invalid or expired token'},
#                 status=status.HTTP_400_BAD_REQUEST
#             )

class UserProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = UserSerializer
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user

class ForgotPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ForgotPasswordSerializer

    def send_password_reset_email(self, user, reset_link):
        """Send password reset email to user"""
        context = {
            'user': user,
            'reset_link': reset_link
        }

        # Render email templates
        html_message = render_to_string(
            'accounts/emails/password_reset.html', 
            context
        )
        plain_message = render_to_string(
            'accounts/emails/password_reset.txt', 
            context
        )

        try:
            # Send email
            send_mail(
                subject='Reset Your Password',
                message=plain_message,
                from_email=settings.DEFAULT_FROM_EMAIL,
                recipient_list=[user.email],
                html_message=html_message,
                fail_silently=False,
            )
            return True, None
        except Exception as e:
            return False, str(e)

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        email = serializer.validated_data['email']
        
        try:
            user = User.objects.get(email=email)
            
            # Generate unique token
            token = str(uuid.uuid4())
            
            # Save reset token
            PasswordResetToken.objects.filter(user=user).delete()
            reset_token = PasswordResetToken.objects.create(
                user=user,
                token=token,
                expires_at=timezone.now() + timedelta(hours=24)
            )
            
            # Generate reset link
            reset_link = f"{settings.FRONTEND_URL}/reset-password/{token}"
            
            # Send email
            email_sent, error = self.send_password_reset_email(user, reset_link)
            
            response_data = {
                'message': 'Password reset instructions have been sent to your email.'
            }
            
            # Include debug info in development
            if settings.DEBUG:
                response_data['debug_info'] = {
                    'reset_link': reset_link,
                    'email_status': 'sent' if email_sent else 'failed',
                }
                if not email_sent:
                    response_data['debug_info']['error'] = error
            
            return Response(response_data)
            
        except User.DoesNotExist:
            # For security, use the same message even if email doesn't exist
            return Response({
                'message': 'Password reset instructions have been sent to your email if an account exists with this email address.'
            })


class ResetPasswordView(APIView):
    permission_classes = (AllowAny,)
    serializer_class = ResetPasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)
        
        serializer.save()
        
        return Response({
            'message': 'Password has been reset successfully.'
        })


class VerifyEmailConfirmView(APIView):
    """Handle the email verification link click"""
    permission_classes = (AllowAny,)

    def get(self, request):
        token = request.GET.get('token')
        try:
            # Verify the signed token
            data = signing.loads(
                token, 
                salt='email-verification', 
                max_age=86400  # 24 hours in seconds
            )
            
            # Get and verify user
            user = User.objects.get(id=data['user_id'], email=data['email'])
            
            if user.is_email_verified:
                return redirect(f"{settings.FRONTEND_URL}/verification/already-verified")
            
            user.is_email_verified = True
            user.save()
            
            # Update registration info if exists
            UserRegistrationInfo.objects.filter(user=user).update(
                registration_status='verified',
                verified_at=timezone.now()
            )
            
            # Redirect to frontend success page
            return redirect(f"{settings.FRONTEND_URL}/verification/success")
            
        except (signing.BadSignature, signing.SignatureExpired):
            # Redirect to frontend error page
            return redirect(f"{settings.FRONTEND_URL}/verification/error")
        except User.DoesNotExist:
            return redirect(f"{settings.FRONTEND_URL}/verification/error")


# New endpoint for changing password while logged in
class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)  # Only logged-in users
    
    def post(self, request):
        serializer = ChangePasswordSerializer(data=request.data)
        if serializer.is_valid():
            # Access authenticated user directly
            user = request.user
            # Check old password
            if user.check_password(serializer.data.get('current_password')):
                user.set_password(serializer.data.get('new_password'))
                user.save()
                return Response({
                    'message': 'Password successfully changed'
                })
            return Response({
                'error': 'Incorrect current password'
            }, status=status.HTTP_400_BAD_REQUEST)