from django import forms
from django.contrib.auth.forms import UserCreationForm
from .models import CustomUser, ThesisTopic


class StudentSignUpForm(UserCreationForm):
    class Meta:
        model = CustomUser
        fields = (
            "first_name",
            "last_name",
            "username",
            "email",
            "matric_number",
            "faculty",
            "department",
            "level",
            "phone_number",
            "password1",
            "password2",
        )

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })

        self.fields["first_name"].widget.attrs["placeholder"] = "Enter first name"
        self.fields["last_name"].widget.attrs["placeholder"] = "Enter last name"
        self.fields["username"].widget.attrs["placeholder"] = "Choose a username"
        self.fields["email"].widget.attrs["placeholder"] = "Enter your email"
        self.fields["department"].widget.attrs["placeholder"] = "Computer Science"
        self.fields["matric_number"].widget.attrs["placeholder"] = "e.g CSC/2024/001"
        self.fields["faculty"].widget.attrs["placeholder"] = "Faculty of Science & Computing"
        self.fields["phone_number"].widget.attrs["placeholder"] = "080243....."
        self.fields["password1"].widget.attrs["placeholder"] = "Enter password"
        self.fields["password2"].widget.attrs["placeholder"] = "Confirm password"

    def save(self, commit=True):
        user = super().save(commit=False)

        user.is_student = True
        user.is_supervisor = False
        user.is_active = False
        user.is_approved = False

        if commit:
            user.save()

        return user


class ThesisTopicForm(forms.ModelForm):
    class Meta:
        model = ThesisTopic
        fields = [
            "title", 
            "research_area", 
            "description",
            "proposal",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for field in self.fields.values():
            field.widget.attrs.update({
                "class": "form-control"
            })

        self.fields["title"].widget.attrs["placeholder"] = "Enter your proposed thesis title"
        self.fields["research_area"].empty_label = "Search Research Area"
        self.fields["description"].widget.attrs.update({"placeholder": "Describe your proposed research topic", "row": 6,})
        self.fields["proposal"].widget.attrs.update({
            "class": "form-control"
        })
        