from django import forms
from django.core.exceptions import ValidationError
from datetime import date, time
from .models import Employee


class RegistrationForm(forms.ModelForm):
    password = forms.CharField(
        label='Password',
        widget=forms.PasswordInput,
        help_text='Enter a strong password.'
    )
    confirm_password = forms.CharField(
        label='Confirm Password',
        widget=forms.PasswordInput,
        help_text='Repeat the same password as before.'
    )

    class Meta:
        model = Employee
        fields = [
            'employee_id', 'first_name', 'last_name',
            'email', 'phone', 'department', 'position'
        ]
        widgets = {
            'employee_id': forms.TextInput(attrs={'placeholder': 'Employee ID'}),
            'first_name': forms.TextInput(attrs={'placeholder': 'First Name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last Name'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email'}),
            'phone': forms.TextInput(attrs={'placeholder': 'Phone Number'}),
            'department': forms.Select(),
            'position': forms.TextInput(attrs={'placeholder': 'Position'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise ValidationError("Passwords do not match.")

        return cleaned_data

    def save(self, commit=True):
        user = super().save(commit=False)
        user.set_password(self.cleaned_data["password"])
        if commit:
            user.save()
        return user


class ManualEntryForm(forms.Form):
    date = forms.DateField(
        initial=date.today,
        widget=forms.DateInput(attrs={'type': 'date'})
    )
    start_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    end_time = forms.TimeField(
        widget=forms.TimeInput(attrs={'type': 'time'})
    )
    break_hours = forms.FloatField(
        initial=0.0,
        min_value=0,
        max_value=24,
        required=False
    )
    description = forms.CharField(
        widget=forms.Textarea(attrs={'rows': 3}),
        required=False
    )
    project = forms.CharField(
        max_length=100,
        required=False
    )