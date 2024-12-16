# accounts/serializers.py
from rest_framework import serializers
from django.contrib.auth import get_user_model
from django.core.exceptions import ValidationError
from django.utils import timezone
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from .models import PasswordResetToken 


# Accessing Accounts/Models.py
User = get_user_model()

class UserRegistrationSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True, min_length=8)
    password_confirm = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['email', 'username', 'password', 'password_confirm']

    def validate(self, data):
        if data['password'] != data['password_confirm']:
            raise ValidationError("Passwords don't match")
        return data

    def create(self, validated_data):
        validated_data.pop('password_confirm')
        user = User.objects.create_user(**validated_data)
        return user

class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_email_verified', 'created_at']
        read_only_fields = ['is_email_verified']

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):
    def validate(self, attrs):
        data = super().validate(attrs)
        data['user'] = UserSerializer(self.user).data
        return data
    
class ForgotPasswordSerializer(serializers.Serializer):
    email = serializers.EmailField()

    def validate_email(self, value):
        try:
            User.objects.get(email=value)
            return value
        except User.DoesNotExist:
            raise serializers.ValidationError("No user found with this email address.")

class ResetPasswordSerializer(serializers.Serializer):
    token = serializers.CharField()
    new_password = serializers.CharField(min_length=8, write_only=True)
    confirm_password = serializers.CharField(write_only=True)

    def validate(self, data):
        if data['new_password'] != data['confirm_password']:
            raise serializers.ValidationError("Passwords don't match")
        
        try:
            token = PasswordResetToken.objects.get(
                token=data['token'],
                expires_at__gt=timezone.now()
            )
            data['user'] = token.user
        except PasswordResetToken.DoesNotExist:
            raise serializers.ValidationError("Invalid or expired reset token")
        
        return data

    def save(self):
        user = self.validated_data['user']
        user.set_password(self.validated_data['new_password'])
        user.save()
        # Delete the used token
        PasswordResetToken.objects.filter(user=user).delete()
        return user

class ChangePasswordView(APIView):
    permission_classes = (IsAuthenticated,)
    serializer_class = ChangePasswordSerializer

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        
        if serializer.is_valid():
            user = request.user
            
            # Verify current password
            if not user.check_password(serializer.validated_data['current_password']):
                return Response({
                    'current_password': ['Current password is incorrect.']
                }, status=status.HTTP_400_BAD_REQUEST)
            
            try:
                # Set new password
                user.set_password(serializer.validated_data['new_password'])
                user.save()
                
                # Optional: Log the password change
                UserRegistrationInfo.objects.filter(user=user).update(
                    last_password_change=timezone.now()
                )
                
                return Response({
                    'message': 'Password changed successfully.',
                    'status': 'success'
                })
                
            except Exception as e:
                return Response({
                    'message': 'An error occurred while changing password.',
                    'error': str(e)
                }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)