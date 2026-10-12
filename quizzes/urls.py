from django.urls import path
from . import views

urlpatterns = [
    path("teacher/", views.teacher_dashboard, name="teacher_dashboard"),
    path("teacher/create-class/", views.create_class_view, name="create_class"),
    path("teacher/create-student/", views.create_student_view, name="create_student"),
    path("teacher/create-quiz/", views.create_quiz_view, name="create_quiz"),
    path("student/", views.student_dashboard, name="student_dashboard"),
    path("quiz/<int:quiz_id>/unlock/", views.unlock_quiz_view, name="unlock_quiz"),
]
