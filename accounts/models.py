from django.contrib.auth.models import AbstractUser
from django.db import models


class User(AbstractUser):
    class Role(models.TextChoices):
        ADMIN = "ADMIN", "Admin"
        TEACHER = "TEACHER", "Teacher"
        STUDENT = "STUDENT", "Student"

    role = models.CharField(
        max_length=10,
        choices=Role.choices,
        default=Role.STUDENT,
    )

    def is_admin_role(self):
        return self.role == self.Role.ADMIN or self.is_superuser

    def is_teacher_role(self):
        return self.role == self.Role.TEACHER

    def is_student_role(self):
        return self.role == self.Role.STUDENT

    def __str__(self):
        return f"{self.username} ({self.get_role_display()})"
