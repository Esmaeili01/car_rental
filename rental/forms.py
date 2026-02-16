from django import forms
from .models import User, Car, Rent, Review

class SignUpForm(forms.ModelForm):
    password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Create password'}))
    confirm_password = forms.CharField(widget=forms.PasswordInput(attrs={'placeholder': 'Confirm password'}))

    class Meta:
        model = User
        fields = ['first_name', 'last_name', 'phone_number', 'email', 'birthdate', 'address', 'password']
        widgets = {
            'first_name': forms.TextInput(attrs={'placeholder': 'First name'}),
            'last_name': forms.TextInput(attrs={'placeholder': 'Last name'}),
            'phone_number': forms.TextInput(attrs={'placeholder': 'Phone number'}),
            'email': forms.EmailInput(attrs={'placeholder': 'Email address'}),
            'birthdate': forms.DateInput(attrs={'type': 'date'}),
            'address': forms.Textarea(attrs={'rows': 2, 'placeholder': 'Address'}),
        }

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        confirm_password = cleaned_data.get("confirm_password")

        if password != confirm_password:
            raise forms.ValidationError("Passwords do not match")
        return cleaned_data

class LoginForm(forms.Form):
    identifier = forms.CharField(
        max_length=254,
        label='Email or Phone Number',
        widget=forms.TextInput(attrs={'placeholder': 'Enter email or phone number'}),
    )
    password = forms.CharField(widget=forms.PasswordInput)

class CarForm(forms.ModelForm):
    class Meta:
        model = Car
        exclude = ['owner', 'status']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['fee'].label = 'Price Per Day'
        self.fields['max_days'].label = 'Max Reservation Days'

class RentRequestForm(forms.ModelForm):
    class Meta:
        model = Rent
        fields = ['start_datetime', 'end_datetime']
        widgets = {
            'start_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
            'end_datetime': forms.DateTimeInput(attrs={'type': 'datetime-local'}),
        }

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['comment']
