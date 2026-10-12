from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

User = get_user_model()


class AccountsTests(TestCase):
    def test_teacher_registration(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "prof_smith",
                "email": "smith@school.edu",
                "first_name": "John",
                "last_name": "Smith",
                "password": "SecurePassword123!",
                "password_confirm": "SecurePassword123!",
            },
        )
        self.assertEqual(response.status_code, 302)
        teacher = User.objects.get(username="prof_smith")
        self.assertEqual(teacher.role, User.Role.TEACHER)
        self.assertTrue(teacher.is_teacher_role())
        self.assertFalse(teacher.is_student_role())

    def test_teacher_registration_password_mismatch(self):
        response = self.client.post(
            reverse("register"),
            {
                "username": "prof_smith",
                "email": "smith@school.edu",
                "password": "Password123",
                "password_confirm": "WrongPassword",
            },
        )
        self.assertEqual(response.status_code, 200)
        self.assertFormError(response.context["form"], "password_confirm", "Passwords do not match.")
        self.assertFalse(User.objects.filter(username="prof_smith").exists())

    def test_login_and_logout(self):
        user = User.objects.create_user(
            username="teacher1",
            password="Password123!",
            role=User.Role.TEACHER,
        )
        response = self.client.post(
            reverse("login"),
            {"username": "teacher1", "password": "Password123!"},
        )
        self.assertEqual(response.status_code, 302)

        # Logout
        response = self.client.post(reverse("logout"))
        self.assertEqual(response.status_code, 302)
