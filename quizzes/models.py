from django.conf import settings
from django.db import models
from django.utils.text import slugify


class ClassTag(models.Model):
    """
    Classes or tags created by teachers.
    Students are assigned to multiple classes/tags.
    """
    name = models.CharField(max_length=100)
    code = models.SlugField(max_length=50, unique=True, blank=True)
    created_by = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_classes",
    )
    students = models.ManyToManyField(
        settings.AUTH_USER_MODEL,
        related_name="enrolled_classes",
        blank=True,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.code:
            base_slug = slugify(self.name) or "class"
            slug = base_slug
            counter = 1
            while ClassTag.objects.filter(code=slug).exclude(pk=self.pk).exists():
                slug = f"{base_slug}-{counter}"
                counter += 1
            self.code = slug
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.name} ({self.code})"


class Quiz(models.Model):
    """
    Quiz distribution model.
    Stores metadata, access code, target classes/tags, and quiz content.
    """
    title = models.CharField(max_length=200)
    creator = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="created_quizzes",
    )
    target_classes = models.ManyToManyField(
        ClassTag,
        related_name="quizzes",
        blank=True,
    )
    access_code = models.CharField(
        max_length=64,
        help_text="Access code required for students to unlock the quiz",
    )
    is_formal = models.BooleanField(
        default=False,
        help_text="Indicates if the test is formal (default: False)",
    )
    metadata = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quiz metadata (description, timing, question count, etc.)",
    )
    content = models.JSONField(
        default=dict,
        blank=True,
        help_text="Quiz JSON document (questions and options)",
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        formal_tag = " [Formal]" if self.is_formal else ""
        return f"{self.title}{formal_tag} (ID: {self.id})"


class QuizResult(models.Model):
    """
    Results of a quiz attempt by a student.
    Stores marks, answers marked (e.g. '01230...' where 0 is blank, 1-9 are options).
    """
    quiz = models.ForeignKey(
        Quiz,
        on_delete=models.CASCADE,
        related_name="results",
    )
    student = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="quiz_results",
    )
    answers = models.CharField(
        max_length=500,
        blank=True,
        default="",
        help_text="String of option numbers (0 for blank, 1-9 for chosen option)",
    )
    marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.0,
        help_text="Marks / score obtained",
    )
    total_marks = models.DecimalField(
        max_digits=6,
        decimal_places=2,
        default=0.0,
    )
    access_code_used = models.CharField(
        max_length=64,
        blank=True,
        default="",
    )
    is_formal = models.BooleanField(default=False)
    submitted_at = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        if not self.pk and self.quiz:
            self.is_formal = self.quiz.is_formal
        super().save(*args, **kwargs)

    def __str__(self):
        return f"{self.student.username} - {self.quiz.title} ({self.marks}/{self.total_marks})"
