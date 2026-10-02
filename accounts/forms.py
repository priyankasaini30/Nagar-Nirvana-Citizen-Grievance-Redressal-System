from django import forms
import re
from django.contrib.auth.forms import UserCreationForm
from .models import User


class UserRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'address',
            'password1',
            'password2'
        ]

    def _clean_name(self, value, field_label):
        value = (value or "").strip()
        if not value:
            return value
        if not re.fullmatch(r"[A-Za-z]+", value):
            raise forms.ValidationError(f"{field_label} should contain letters only.")
        return value

    def clean_first_name(self):
        return self._clean_name(self.cleaned_data.get("first_name"), "First name")

    def clean_last_name(self):
        return self._clean_name(self.cleaned_data.get("last_name"), "Last name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.is_citizen = True
        user.is_authority = False
        user.is_active = True

        if commit:
            user.save()
        return user


class AuthorityRegistrationForm(UserCreationForm):
    email = forms.EmailField(required=True)
    phone = forms.CharField(max_length=15, required=False)
    address = forms.CharField(widget=forms.Textarea, required=False)
    first_name = forms.CharField(max_length=30, required=False)
    last_name = forms.CharField(max_length=30, required=False)

    class Meta:
        model = User
        fields = [
            'first_name',
            'last_name',
            'username',
            'email',
            'phone',
            'address',
            'password1',
            'password2'
        ]

    def _clean_name(self, value, field_label):
        value = (value or "").strip()
        if not value:
            return value
        if not re.fullmatch(r"[A-Za-z]+", value):
            raise forms.ValidationError(f"{field_label} should contain letters only.")
        return value

    def clean_first_name(self):
        return self._clean_name(self.cleaned_data.get("first_name"), "First name")

    def clean_last_name(self):
        return self._clean_name(self.cleaned_data.get("last_name"), "Last name")

    def save(self, commit=True):
        user = super().save(commit=False)
        user.email = self.cleaned_data['email']
        user.phone = self.cleaned_data['phone']
        user.address = self.cleaned_data['address']
        user.first_name = self.cleaned_data.get('first_name', '')
        user.last_name = self.cleaned_data.get('last_name', '')
        user.is_citizen = False
        user.is_authority = True
        user.is_active = False

        if commit:
            user.save()
        return user
