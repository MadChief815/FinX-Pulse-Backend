from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.tokens import RefreshToken


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(required=True)
	password = serializers.CharField(write_only=True, min_length=8)
	access = serializers.SerializerMethodField()
	refresh = serializers.SerializerMethodField()

	class Meta:
		model = User
		fields = ["id", "email", "username", "password", "access", "refresh"]
		read_only_fields = ["id"]

	def _get_refresh_token(self, user):
		if not hasattr(self, "_registration_refresh"):
			self._registration_refresh = RefreshToken.for_user(user)
		return self._registration_refresh

	def get_refresh(self, user):
		return str(self._get_refresh_token(user))

	def get_access(self, user):
		return str(self._get_refresh_token(user).access_token)

	def validate_email(self, value):
		if User.objects.filter(email__iexact=value).exists():
			raise serializers.ValidationError("A user with this email already exists.")
		return value

	def validate_password(self, value):
		validate_password(value)
		return value

	def create(self, validated_data):
		return User.objects.create_user(**validated_data)


class LoginSerializer(TokenObtainPairSerializer):
    identifier = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "Username or email is required.",
            "blank": "Username or email is required.",
        },
    )

    password = serializers.CharField(
        write_only=True,
        required=True,
        error_messages={
            "required": "Password is required.",
            "blank": "Password is required.",
        },
    )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields.pop(self.username_field)

    def validate(self, attrs):
        identifier = attrs.pop("identifier")
        password = attrs.get("password")

        # Find user by username or email
        user = User.objects.filter(username=identifier).first()

        if user is None:
            user = User.objects.filter(email__iexact=identifier).first()

        if user is None:
            raise AuthenticationFailed(
                "No account found with this username or email."
            )

        # Check if account is active
        if not user.is_active:
            raise AuthenticationFailed(
                "This account is inactive."
            )

        # Check password
        if not user.check_password(password):
            raise AuthenticationFailed(
                "Incorrect password."
            )

        # Pass username to SimpleJWT's normal validation
        attrs[self.username_field] = user.get_username()

        return super().validate(attrs)


class ProfileSerializer(serializers.ModelSerializer):
	class Meta:
		model = User
		fields = ["username", "email"]


class ProfileUpdateSerializer(serializers.ModelSerializer):
	current_password = serializers.CharField(write_only=True, required=False)
	password = serializers.CharField(write_only=True, required=False, min_length=8)

	class Meta:
		model = User
		fields = ["username", "password", "current_password"]

	def validate_username(self, value):
		if User.objects.filter(username=value).exclude(pk=self.instance.pk).exists():
			raise serializers.ValidationError("A user with this username already exists.")
		return value

	def validate(self, attrs):
		if "password" in attrs:
			current_password = attrs.get("current_password")
			if not current_password:
				raise serializers.ValidationError({"current_password": "This field is required when changing password."})
			if not self.instance.check_password(current_password):
				raise serializers.ValidationError({"current_password": "Current password is incorrect."})
			validate_password(attrs["password"], self.instance)
		else:
			attrs.pop("current_password", None)
		return attrs

	def update(self, instance, validated_data):
		validated_data.pop("current_password", None)
		password = validated_data.pop("password", None)
		for field, value in validated_data.items():
			setattr(instance, field, value)
		if password is not None:
			instance.set_password(password)
		instance.save()
		return instance