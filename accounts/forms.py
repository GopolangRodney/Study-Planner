from django import forms
from .models import Task
from django.contrib.auth.models import User

class TaskForm(forms.ModelForm):
    class Meta:
        model = Task
        fields = ['title', 'due_date']  # Only these fields are required
        widgets = {
            'due_date': forms.DateInput(attrs={'type': 'date'})  # Ensure date input uses a proper date picker
        }

class UserProfileForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(), required=False)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    # Optionally, if you want to handle the profile picture upload (see optional model below)
    profile_pic = forms.ImageField(required=False)