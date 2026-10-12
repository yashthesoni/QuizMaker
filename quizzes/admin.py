from django.contrib import admin
from .models import ClassTag, Quiz, QuizResult


@admin.register(ClassTag)
class ClassTagAdmin(admin.ModelAdmin):
    list_display = ("name", "code", "created_by", "created_at")
    search_fields = ("name", "code", "created_by__username")
    filter_horizontal = ("students",)


@admin.register(Quiz)
class QuizAdmin(admin.ModelAdmin):
    list_display = ("title", "creator", "access_code", "is_formal", "created_at")
    list_filter = ("is_formal", "created_at")
    search_fields = ("title", "access_code", "creator__username")
    filter_horizontal = ("target_classes",)


@admin.register(QuizResult)
class QuizResultAdmin(admin.ModelAdmin):
    list_display = ("student", "quiz", "marks", "total_marks", "is_formal", "submitted_at")
    list_filter = ("is_formal", "submitted_at")
    search_fields = ("student__username", "quiz__title", "answers")
