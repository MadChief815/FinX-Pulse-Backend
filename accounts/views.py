from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.throttling import AnonRateThrottle
from rest_framework_simplejwt.views import TokenObtainPairView
from rest_framework_simplejwt.tokens import RefreshToken

from .serializers import (
	LoginSerializer,
	ProfileSerializer,
	ProfileUpdateSerializer,
	RegisterSerializer,
)

class AuthRateThrottle(AnonRateThrottle):
	rate = "5/minute"

class RegisterView(generics.CreateAPIView):
	permission_classes = [AllowAny]
	throttle_classes = [AuthRateThrottle]
	serializer_class = RegisterSerializer

	def create(self, request, *args, **kwargs):
		serializer = self.get_serializer(data=request.data)
		serializer.is_valid(raise_exception=True)
		user = serializer.save()
		refresh = RefreshToken.for_user(user)
		data = {
			"id": user.pk,
			"email": user.email,
			"username": user.username,
			"access": str(refresh.access_token),
			"refresh": str(refresh),
		}
		headers = self.get_success_headers(data)
		return Response(data, status=status.HTTP_201_CREATED, headers=headers)

class LoginView(TokenObtainPairView):
	permission_classes = [AllowAny]
	throttle_classes = [AuthRateThrottle]
	serializer_class = LoginSerializer

class ProfileView(generics.RetrieveUpdateAPIView):
    permission_classes = [IsAuthenticated]
    serializer_class = ProfileSerializer

    http_method_names = ["get", "patch", "head", "options"]

    def get_object(self):
        return self.request.user

    def get_serializer_class(self):
        if self.request.method == "PATCH":
            return ProfileUpdateSerializer

        return ProfileSerializer

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop("partial", False)
        instance = self.get_object()

        serializer = self.get_serializer(
            instance,
            data=request.data,
            partial=partial,
        )

        serializer.is_valid(raise_exception=True)

        updated_fields = [
            field
            for field in ("username", "password")
            if field in serializer.validated_data
        ]

        self.perform_update(serializer)

        messages = []

        if "username" in updated_fields:
            messages.append("Username updated successfully.")

        if "password" in updated_fields:
            messages.append("Password updated successfully.")

        return Response(
            {
                "success": True,
                "messages": messages,
            },
            status=status.HTTP_200_OK,
        )