from django import forms
from django.contrib.auth import get_user_model
from quizzes.models import ClassTag

User = get_user_model()


class TeacherRegisterForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Password",
            "autocomplete": "new-password",
            "data-lpignore": "true",
            "data-1p-ignore": "true",
        }),
        label="Password",
    )
    password_confirm = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Confirm Password",
            "autocomplete": "new-password",
            "data-lpignore": "true",
            "data-1p-ignore": "true",
        }),
        label="Confirm Password",
    )

    class Meta:
        model = User
        fields = ("username", "email", "first_name", "last_name")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Teacher Username", "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"placeholder": "Email Address", "autocomplete": "off"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First Name", "autocomplete": "off"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name", "autocomplete": "off"}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")

        if password and password_confirm and password != password_confirm:
            self.add_error("password_confirm", "Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        user.role = User.Role.TEACHER
        if commit:
            user.save()
        return user


class StudentCreationByTeacherForm(forms.ModelForm):
    """
    Teacher's form to create student accounts.
    Students cannot create their own accounts; teachers do this for them.
    """
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={
            "placeholder": "Temporary Password for Student",
            "autocomplete": "new-password",
            "data-lpignore": "true",
            "data-1p-ignore": "true",
        }),
        label="Initial Password",
    )
    assigned_classes = forms.ModelMultipleChoiceField(
        queryset=ClassTag.objects.none(),
        widget=forms.CheckboxSelectMultiple,
        required=False,
        label="Assign Classes (Tags)",
    )

    class Meta:
        model = User
        fields = ("username", "first_name", "last_name", "email")
        widgets = {
            "username": forms.TextInput(attrs={"placeholder": "Student Username / Roll No", "autocomplete": "off"}),
            "first_name": forms.TextInput(attrs={"placeholder": "First Name", "autocomplete": "off"}),
            "last_name": forms.TextInput(attrs={"placeholder": "Last Name", "autocomplete": "off"}),
            "email": forms.EmailInput(attrs={"placeholder": "Student Email (optional)", "autocomplete": "off"}),
        }

    def __init__(self, *args, teacher=None, **kwargs):
        super().__init__(*args, **kwargs)
        if teacher:
            self.fields["assigned_classes"].queryset = ClassTag.objects.filter(created_by=teacher)

    def save(self, commit=True):
        student = super().save(commit=False)
        student.set_password(self.cleaned_data["password"])
        student.role = User.Role.STUDENT
        if commit:
            student.save()
            assigned_classes = self.cleaned_data.get("assigned_classes")
            if assigned_classes:
                for cls in assigned_classes:
                    cls.students.add(student)
        return student
