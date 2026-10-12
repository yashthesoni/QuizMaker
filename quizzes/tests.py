from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from .models import ClassTag, Quiz, QuizResult

User = get_user_model()


class DistributionSystemTests(TestCase):
    def setUp(self):
        # Create a teacher
        self.teacher = User.objects.create_user(
            username="teacher_alan",
            password="TeacherPass123!",
            role=User.Role.TEACHER,
        )
        # Create a class tag
        self.class_physics = ClassTag.objects.create(
            name="Physics 101",
            created_by=self.teacher,
        )

    def test_teacher_create_class(self):
        self.client.login(username="teacher_alan", password="TeacherPass123!")
        response = self.client.post(
            reverse("create_class"),
            {"name": "Chemistry 201"},
        )
        self.assertEqual(response.status_code, 302)
        self.assertTrue(ClassTag.objects.filter(name="Chemistry 201", created_by=self.teacher).exists())

    def test_teacher_creates_student_account_and_assigns_classes(self):
        """Test the Teacher's Form where teachers create student accounts."""
        self.client.login(username="teacher_alan", password="TeacherPass123!")
        response = self.client.post(
            reverse("create_student"),
            {
                "username": "student_bob",
                "password": "StudentPass123!",
                "first_name": "Bob",
                "last_name": "Builder",
                "assigned_classes": [self.class_physics.id],
            },
        )
        self.assertEqual(response.status_code, 302)
        student = User.objects.get(username="student_bob")
        self.assertEqual(student.role, User.Role.STUDENT)
        self.assertTrue(student.is_student_role())
        self.assertIn(self.class_physics, student.enrolled_classes.all())

    def test_quiz_distribution_and_access_code_unlock(self):
        """Test quiz creation with access code and student unlock."""
        self.client.login(username="teacher_alan", password="TeacherPass123!")

        # Create quiz
        response = self.client.post(
            reverse("create_quiz"),
            {
                "title": "Quantum Mechanics Intro",
                "access_code": "SECRET-99",
                "is_formal": True,
                "time_limit_minutes": 45,
                "description": "Midterm test for Physics 101",
                "target_classes": [self.class_physics.id],
            },
        )
        self.assertEqual(response.status_code, 302)
        quiz = Quiz.objects.get(title="Quantum Mechanics Intro")
        self.assertEqual(quiz.access_code, "SECRET-99")
        self.assertTrue(quiz.is_formal)

        # Create student and enroll in physics
        student = User.objects.create_user(
            username="student_alice",
            password="AlicePass123!",
            role=User.Role.STUDENT,
        )
        self.class_physics.students.add(student)

        # Student logs in
        self.client.login(username="student_alice", password="AlicePass123!")

        # Check student dashboard displays quiz
        dash_resp = self.client.get(reverse("student_dashboard"))
        self.assertEqual(dash_resp.status_code, 200)
        self.assertContains(dash_resp, "Quantum Mechanics Intro")

        # Wrong access code
        wrong_resp = self.client.post(
            reverse("unlock_quiz", kwargs={"quiz_id": quiz.id}),
            {"access_code": "WRONG-CODE"},
        )
        self.assertEqual(wrong_resp.status_code, 200)
        self.assertContains(wrong_resp, "Invalid access code")

        # Correct access code
        correct_resp = self.client.post(
            reverse("unlock_quiz", kwargs={"quiz_id": quiz.id}),
            {"access_code": "SECRET-99"},
        )
        self.assertEqual(correct_resp.status_code, 200)
        self.assertContains(correct_resp, "Access Code Verified")

    def test_quiz_results_model_and_answers_string(self):
        """Test quiz results storage including answers string and marks."""
        quiz = Quiz.objects.create(
            title="General Knowledge",
            creator=self.teacher,
            access_code="GK-101",
            is_formal=False,
        )
        student = User.objects.create_user(
            username="student_carol",
            password="CarolPass123!",
            role=User.Role.STUDENT,
        )
        # Store attempt with answers string e.g. '01230...' (0=blank, 1-9 options)
        result = QuizResult.objects.create(
            quiz=quiz,
            student=student,
            answers="10231",
            marks=18.5,
            total_marks=20.0,
            access_code_used="GK-101",
        )
        self.assertEqual(result.answers, "10231")
        self.assertEqual(float(result.marks), 18.5)
        self.assertFalse(result.is_formal)
