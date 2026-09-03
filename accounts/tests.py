from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APITestCase


User = get_user_model()


class ProfileUpdateTests(APITestCase):
	def setUp(self):
		self.user = User.objects.create_user(
			username="jane",
			email="jane@example.com",
			password="OldPassword123!",
		)
		self.profile_url = reverse("profile")

	def test_requires_authentication(self):
		response = self.client.patch(self.profile_url, {"username": "new-jane"}, format="json")

		self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

	def test_updates_username(self):
		self.client.force_authenticate(self.user)

		response = self.client.patch(self.profile_url, {"username": "new-jane"}, format="json")

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, {"username": "new-jane"})
		self.assertEqual(User.objects.get(pk=self.user.pk).username, "new-jane")

	def test_updates_password_with_current_password(self):
		self.client.force_authenticate(self.user)

		response = self.client.patch(
			self.profile_url,
			{"current_password": "OldPassword123!", "password": "NewPassword123!"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_200_OK)
		self.assertEqual(response.data, {"username": "jane"})
		self.assertTrue(User.objects.get(pk=self.user.pk).check_password("NewPassword123!"))

	def test_rejects_incorrect_current_password(self):
		self.client.force_authenticate(self.user)

		response = self.client.patch(
			self.profile_url,
			{"current_password": "wrong-password", "password": "NewPassword123!"},
			format="json",
		)

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

	def test_rejects_duplicate_username(self):
		User.objects.create_user(username="other", email="other@example.com", password="Password123!")
		self.client.force_authenticate(self.user)

		response = self.client.patch(self.profile_url, {"username": "other"}, format="json")

		self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
