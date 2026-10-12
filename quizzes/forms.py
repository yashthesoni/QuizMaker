from django import forms
from .models import ClassTag, Quiz


class ClassTagForm(forms.ModelForm):
    class Meta:
        model = ClassTag
        fields = ("name",)
        widgets = {
            "name": forms.TextInput(attrs={"placeholder": "e.g. Grade-10A, Physics-Honor", "class": "form-control"}),
        }


class QuizDistributionForm(forms.ModelForm):
    description = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={"rows": 3, "placeholder": "Quiz instructions or description", "class": "form-control"}),
        label="Description / Instructions",
    )
    time_limit_minutes = forms.IntegerField(
        initial=30,
        min_value=1,
        label="Time Limit (Minutes)",
        widget=forms.NumberInput(attrs={"class": "form-control"}),
    )

    class Meta:
        model = Quiz
        fields = ("title", "access_code", "is_formal", "target_classes")
        widgets = {
            "title": forms.TextInput(attrs={"placeholder": "Quiz Title (e.g. Midterm Physics)", "class": "form-control"}),
            "access_code": forms.TextInput(attrs={"placeholder": "e.g. PHYS-2026", "class": "form-control"}),
            "is_formal": forms.CheckboxInput(attrs={"class": "form-check-input"}),
            "target_classes": forms.CheckboxSelectMultiple(),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields["target_classes"].queryset = ClassTag.objects.filter(created_by=teacher)

    def save(self, creator, commit=True):
        quiz = super().save(commit=False)
        quiz.creator = creator
        quiz.metadata = {
            "description": self.cleaned_data.get("description", ""),
            "time_limit_minutes": self.cleaned_data.get("time_limit_minutes", 30),
        }
        # Placeholder quiz document until the quiz creation module is added
        if not quiz.content:
            quiz.content = {
                "version": "1.0",
                "questions": [],
                "status": "ready_for_quiz_module",
            }
        if commit:
            quiz.save()
            self.save_m2m()
        return quiz


class UnlockQuizForm(forms.Form):
    access_code = forms.CharField(
        max_length=64,
        widget=forms.TextInput(attrs={"placeholder": "Enter Access Code", "class": "form-control"}),
        label="Access Code",
    )
