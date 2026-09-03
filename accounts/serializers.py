from django.contrib.auth import get_user_model
from django.contrib.auth.password_validation import validate_password
from rest_framework import serializers
from rest_framework.exceptions import AuthenticationFailed
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer


User = get_user_model()


class RegisterSerializer(serializers.ModelSerializer):
	email = serializers.EmailField(required=True)
	password = serializers.CharField(write_only=True, min_length=8)

	class Meta:
		model = User
		fields = ["id", "email", "username", "password"]
		read_only_fields = ["id"]

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
	identifier = serializers.CharField(write_only=True)

	def __init__(self, *args, **kwargs):
		super().__init__(*args, **kwargs)
		self.fields.pop(self.username_field)

	def validate(self, attrs):
		identifier = attrs.pop("identifier")
		user = User.objects.filter(username=identifier).first()
		if user is None:
			user = User.objects.filter(email__iexact=identifier).first()
		if user is None:
			raise AuthenticationFailed("No active account found with the given credentials")

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