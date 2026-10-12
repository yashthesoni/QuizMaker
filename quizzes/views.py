from django.contrib import messages
from django.contrib.auth.decorators import login_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, redirect, render

from accounts.forms import StudentCreationByTeacherForm
from .forms import ClassTagForm, QuizDistributionForm, UnlockQuizForm
from .models import ClassTag, Quiz, QuizResult


def require_teacher_or_admin(user):
    if not (user.is_teacher_role() or user.is_admin_role()):
        raise PermissionDenied("Only teachers or administrators can access this page.")


@login_required
def teacher_dashboard(request):
    require_teacher_or_admin(request.user)

    teacher = request.user
    classes = ClassTag.objects.filter(created_by=teacher).prefetch_related("students")
    quizzes = Quiz.objects.filter(creator=teacher).prefetch_related("target_classes")
    recent_results = QuizResult.objects.filter(quiz__creator=teacher).select_related("quiz", "student").order_by("-submitted_at")[:10]

    # All unique students across teacher's classes
    student_ids = classes.values_list("students", flat=True).distinct()
    from accounts.models import User
    students = User.objects.filter(id__in=student_ids)

    context = {
        "classes": classes,
        "quizzes": quizzes,
        "students": students,
        "recent_results": recent_results,
    }
    return render(request, "distribution/teacher_dashboard.html", context)


@login_required
def create_class_view(request):
    require_teacher_or_admin(request.user)

    if request.method == "POST":
        form = ClassTagForm(request.POST)
        if form.is_valid():
            class_tag = form.save(commit=False)
            class_tag.created_by = request.user
            class_tag.save()
            messages.success(request, f"Class / Tag '{class_tag.name}' created successfully!")
            return redirect("teacher_dashboard")
    else:
        form = ClassTagForm()

    return render(request, "distribution/create_class.html", {"form": form})


@login_required
def create_student_view(request):
    """
    The Teacher's Form:
    Teachers create student accounts and assign them to classes/tags.
    Students cannot create their own accounts.
    """
    require_teacher_or_admin(request.user)

    if request.method == "POST":
        form = StudentCreationByTeacherForm(request.POST, teacher=request.user)
        if form.is_valid():
            student = form.save()
            messages.success(
                request,
                f"Student account '{student.username}' created successfully and enrolled into assigned classes!"
            )
            return redirect("teacher_dashboard")
    else:
        form = StudentCreationByTeacherForm(teacher=request.user)

    return render(request, "distribution/create_student.html", {"form": form})


@login_required
def create_quiz_view(request):
    """
    Distribute a new quiz to specific classes with an access code.
    """
    require_teacher_or_admin(request.user)

    if request.method == "POST":
        form = QuizDistributionForm(request.POST, teacher=request.user)
        if form.is_valid():
            quiz = form.save(creator=request.user)
            messages.success(
                request,
                f"Quiz '{quiz.title}' distributed with access code '{quiz.access_code}'!"
            )
            return redirect("teacher_dashboard")
    else:
        form = QuizDistributionForm(teacher=request.user)

    return render(request, "distribution/create_quiz.html", {"form": form})


@login_required
def student_dashboard(request):
    user = request.user
    if user.is_teacher_role():
        return redirect("teacher_dashboard")

    enrolled_classes = user.enrolled_classes.all()
    # Quizzes assigned to any of student's classes
    available_quizzes = Quiz.objects.filter(target_classes__in=enrolled_classes).distinct().order_by("-created_at")
    my_results = QuizResult.objects.filter(student=user).select_related("quiz").order_by("-submitted_at")

    context = {
        "enrolled_classes": enrolled_classes,
        "available_quizzes": available_quizzes,
        "my_results": my_results,
    }
    return render(request, "distribution/student_dashboard.html", context)


@login_required
def unlock_quiz_view(request, quiz_id):
    """
    Verifies the access code entered by the student to access the quiz.
    """
    quiz = get_object_or_404(Quiz, pk=quiz_id)

    # Check if student is in target classes
    user = request.user
    if not (user.is_teacher_role() or user.is_admin_role()):
        has_access = quiz.target_classes.filter(students=user).exists()
        if not has_access:
            messages.error(request, "You are not enrolled in a class that has access to this quiz.")
            return redirect("student_dashboard")

    error = None
    unlocked = False

    if request.method == "POST":
        form = UnlockQuizForm(request.POST)
        if form.is_valid():
            code = form.cleaned_data["access_code"]
            if code == quiz.access_code:
                unlocked = True
                messages.success(request, f"Access code verified! Quiz '{quiz.title}' unlocked.")
            else:
                error = "Invalid access code. Please check with your teacher."
    else:
        form = UnlockQuizForm()

    return render(
        request,
        "distribution/unlock_quiz.html",
        {
            "quiz": quiz,
            "form": form,
            "error": error,
            "unlocked": unlocked,
        },
    )
