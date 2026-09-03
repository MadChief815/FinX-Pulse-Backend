from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework_simplejwt.views import TokenObtainPairView

from .serializers import LoginSerializer, ProfileSerializer, ProfileUpdateSerializer, RegisterSerializer


class RegisterView(generics.CreateAPIView):
	permission_classes = [AllowAny]
	serializer_class = RegisterSerializer


class LoginView(TokenObtainPairView):
	permission_classes = [AllowAny]
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
		serializer = self.get_serializer(instance, data=request.data, partial=partial)
		serializer.is_valid(raise_exception=True)
		self.perform_update(serializer)
		return Response({"username": serializer.instance.username}, status=status.HTTP_200_OK)
