from django import forms
from .models import User
import re
from django.contrib.auth.hashers import check_password
from argon2 import PasswordHasher
from argon2.exceptions import VerifyMismatchError

ph = PasswordHasher()

class UserForm(forms.ModelForm):
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_password'}),
        min_length=8,
        max_length=128,
        label='Password',
        required=False  # Required will be enforced in clean() for sign-up
    )
    check_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control', 'id': 'id_check_password'}),
        min_length=8,
        max_length=128,
        label='Confirm Password',
        required=False  # Required will be enforced in clean() for sign-up
    )

    class Meta:
        model = User
        fields = ['name', 'email', 'phone', 'password', 'check_password', 'image']
        widgets = {
            'name': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_name'}),
            'email': forms.EmailInput(attrs={'class': 'form-control', 'id': 'id_email'}),
            'phone': forms.TextInput(attrs={'class': 'form-control', 'id': 'id_phone'}),
            'image': forms.FileInput(attrs={'class': 'form-control', 'id': 'id_image'}),
        }

    def __init__(self, *args, **kwargs):
        self.is_signup = kwargs.get('instance') is None
        super().__init__(*args, **kwargs)

    def clean_name(self):
        name = self.cleaned_data.get('name')
        if self.is_signup and not name:
            raise forms.ValidationError("Name is required.")
        if not name:
            return name
        
        if not re.match(r'^[A-Za-z]{2,}$', name):
            raise forms.ValidationError("Name must be at least 2 letters and contain only letters.")
        return name


    def clean_email(self):
        email = self.cleaned_data.get('email')
        if self.is_signup and not email:
            raise forms.ValidationError("Email is required.")
        if not email:
            return email
        
        if not email.endswith('@gmail.com'):
            raise forms.ValidationError("Only Gmail addresses are allowed (e.g., example@gmail.com).")
        
        existing_users = User.objects.filter(email=email).exclude(pk=self.instance.pk if self.instance else None)
        if existing_users.exists():
            raise forms.ValidationError('This email is already registered.')
        return email

    def clean_phone(self):
        phone = self.cleaned_data.get('phone')
        if self.is_signup and not phone:
            raise forms.ValidationError("Phone number is required.")
        if not phone:
            return phone
        
        # Check if the phone number matches the pattern: optional + followed by digits
        if not re.match(r'^\+?\d+$', phone):
            raise forms.ValidationError('Enter a valid phone number (digits only, optional + at the start).')
        
        # Extract the digits (remove the + if present)
        digits = phone.replace('+', '')
        
        # Check if the number of digits is exactly 10
        if len(digits) != 10:
            raise forms.ValidationError('Phone number must be exactly 10 digits long.')
        
        return phone

    def clean_image(self):
        image = self.cleaned_data.get('image')
        if image:
            if not image.name.lower().endswith(('.jpg', '.png')):
                raise forms.ValidationError('Only JPG and PNG images are allowed.')
            if image.size > 5 * 1024 * 1024:
                raise forms.ValidationError('Image size must be less than 5MB.')
        return image

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if self.is_signup and not password:
            raise forms.ValidationError("Password is required.")
        if not password:
            return password
        
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', password):
            raise forms.ValidationError(
                "Password must be at least 8 characters long, include 1 uppercase letter, 1 number, and 1 special character."
            )
        return password

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        check_password = cleaned_data.get('check_password')

        if self.is_signup:
            if not password:
                raise forms.ValidationError("Password is required.")
            if not check_password:
                raise forms.ValidationError("Please confirm your password.")
        
        if password and not check_password:
            raise forms.ValidationError("Please confirm your password.")
        
        if password and check_password and password != check_password:
            raise forms.ValidationError("Passwords do not match.")

        return cleaned_data

class UserLoginForm(forms.Form):
    email = forms.EmailField(
        max_length=255,
        widget=forms.EmailInput(attrs={'id': 'id_email', 'class': 'form-control'}),
        required=True
    )
    password = forms.CharField(
        widget=forms.PasswordInput(attrs={'id': 'id_password', 'class': 'form-control'}),
        required=True
    )

    def clean_email(self):
        email = self.cleaned_data.get('email')
        if not email:
            raise forms.ValidationError("Email is required.")
        return email

    def clean_password(self):
        password = self.cleaned_data.get('password')
        if not password:
            raise forms.ValidationError("Password is required.")
        if len(password) < 8:
            raise forms.ValidationError("Password must be at least 8 characters long.")
        return password

class PasswordChangeForm(forms.Form):
    old_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        label="Old Password",
        max_length=128,
        required=True
    )
    new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        max_length=128,
        label="New Password",
        required=True
    )
    confirm_new_password = forms.CharField(
        widget=forms.PasswordInput(attrs={'class': 'form-control'}),
        min_length=8,
        max_length=128,
        label="Confirm New Password",
        required=True
    )

    def __init__(self, user, *args, **kwargs):
        self.user = user
        super().__init__(*args, **kwargs)

    def clean_old_password(self):
        old_password = self.cleaned_data.get('old_password')
        try:
            if not ph.verify(self.user.password, old_password):
                raise forms.ValidationError("Old password is incorrect.")
        except VerifyMismatchError:
            raise forms.ValidationError("Old password is incorrect.")
        return old_password

    def clean_new_password(self):
        new_password = self.cleaned_data.get('new_password')
        if not re.match(r'^(?=.*[a-z])(?=.*[A-Z])(?=.*\d)(?=.*[@$!%*?&])[A-Za-z\d@$!%*?&]{8,}$', new_password):
            raise forms.ValidationError(
                'New password must be at least 8 characters long, contain an uppercase letter, '
                'a lowercase letter, a number, and a special character (@$!%*?&).'
            )
        return new_password

    def clean(self):
        cleaned_data = super().clean()
        new_password = cleaned_data.get('new_password')
        confirm_new_password = cleaned_data.get('confirm_new_password')

        if new_password and confirm_new_password and new_password != confirm_new_password:
            raise forms.ValidationError("New passwords do not match.")

        return cleaned_data