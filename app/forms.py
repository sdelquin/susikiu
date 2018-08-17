# coding: utf-8

from __future__ import unicode_literals
from django import forms
from django.conf import settings
from django.contrib.auth.models import User
from .models import DancingLevel
from .models import DancingStyle
from functools import partial
DateInput = partial(forms.DateInput, {'class': 'datepicker'})


class LoginForm(forms.Form):
    username = forms.CharField(
        label="Nombre de usuario",
        required=True
    )
    password = forms.CharField(
        label="Contraseña",
        required=True,
        widget=forms.PasswordInput()
    )


class RegisterForm(forms.Form):
    token = forms.CharField(
        label="Token",
        required=True,
        help_text="Palabra clave que debes conocer para poder registrarte.",
        widget=forms.PasswordInput()
    )
    first_name = forms.CharField(
        label="Nombre",
        required=True
    )
    last_name = forms.CharField(
        label="Apellidos",
        required=True
    )
    username = forms.SlugField(
        label="Nombre de usuario",
        required=True
    )
    email = forms.EmailField(
        label="Correo electrónico",
        required=True
    )
    password = forms.CharField(
        label="Contraseña",
        required=True,
        widget=forms.PasswordInput()
    )
    repeated_password = forms.CharField(
        label="Repetir contraseña",
        required=True,
        widget=forms.PasswordInput()
    )

    def clean_token(self):
        data = self.cleaned_data["token"]
        if data != settings.ELEBE_TOKEN:
            raise forms.ValidationError("Token incorrecto.")
        return data

    def clean_username(self):
        data = self.cleaned_data["username"]
        if User.objects.filter(username=data):
            raise forms.ValidationError("Ya existe este nombre de usuario.")
        return data

    def clean_email(self):
        data = self.cleaned_data["email"]
        if User.objects.filter(email=data):
            raise forms.ValidationError("Ya existe esta dirección de "
                                        "correo electrónico.")
        return data

    def clean(self):
        cleaned_data = super(RegisterForm, self).clean()
        password = cleaned_data.get("password")
        repeated_password = cleaned_data.get("repeated_password")
        if password and repeated_password:
            if password != repeated_password:
                raise forms.ValidationError("Las contraseñas no coinciden.")


class RemindCredentialsForm(forms.Form):
    email = forms.EmailField(
        label="Correo electrónico",
        required=True
    )

    def clean_email(self):
        data = self.cleaned_data["email"]
        if not User.objects.filter(email=data):
            raise forms.ValidationError("No existe ninguna cuenta con "
                                        "el correo electrónico especificado.")
        return data


class ResetPasswordForm(forms.Form):
    password = forms.CharField(
        label="Contraseña",
        required=True,
        widget=forms.PasswordInput()
    )
    repeated_password = forms.CharField(
        label="Repetir contraseña",
        required=True,
        widget=forms.PasswordInput()
    )

    def clean(self):
        cleaned_data = super(ResetPasswordForm, self).clean()
        password = cleaned_data.get("password")
        repeated_password = cleaned_data.get("repeated_password")
        if password and repeated_password:
            if password != repeated_password:
                raise forms.ValidationError("Las contraseñas no coinciden.")


class ProfileForm(forms.Form):

    def __init__(self, *args, **kwargs):
        self.request = kwargs.pop("request", None)
        super(ProfileForm, self).__init__(*args, **kwargs)

    first_name = forms.CharField(
        label="Nombre",
    )
    last_name = forms.CharField(
        label="Apellidos",
    )
    username = forms.SlugField(
        label="Nombre de usuario",
    )
    email = forms.EmailField(
        label="Correo electrónico",
    )
    password = forms.CharField(
        label="Nueva contraseña",
        required=False,
        widget=forms.PasswordInput()
    )
    repeated_password = forms.CharField(
        label="Repetir contraseña",
        required=False,
        widget=forms.PasswordInput()
    )
    dancing_level = forms.ChoiceField(
        label="Nivel de baile",
        required=False,
        choices=DancingLevel.get_choices()
    )
    favourite_dancing_style = forms.ChoiceField(
        label="Estilo de baile preferido",
        required=False,
        choices=DancingStyle.get_choices()
    )
    teacher = forms.BooleanField(
        label="¿Eres profesor de baile?",
        required=False
    )
    avatar = forms.ImageField(
        label="Foto de perfil",
        required=False
    )
    date_of_birth = forms.DateField(
        label="Fecha de nacimiento",
        widget=DateInput(),
        required=False
    )
    why_dance = forms.CharField(
        label="¿Por qué bailas?",
        max_length=140,
        required=False
    )
    bio = forms.CharField(
        label="Bio. Cuéntanos algo sobre ti.",
        widget=forms.Textarea,
        required=False
    )
    twitter_username = forms.CharField(
        label="Twitter (nombre de usuario)",
        required=False
    )
    facebook_username = forms.CharField(
        label="Facebook (nombre de usuario)",
        required=False
    )
    snapchat_username = forms.CharField(
        label="Snapchat (nombre de usuario)",
        required=False
    )
    instagram_username = forms.CharField(
        label="Instagram (nombre de usuario)",
        required=False
    )

    def clean_username(self):
        data = self.cleaned_data["username"]
        if User.objects.filter(username=data).\
                exclude(username=self.request.user.username):
            raise forms.ValidationError("Ya existe este nombre de usuario.")
        return data

    def clean_email(self):
        data = self.cleaned_data["email"]
        if User.objects.filter(email=data).\
                exclude(email=self.request.user.email):
            raise forms.ValidationError("Ya existe esta dirección de "
                                        "correo electrónico.")
        return data

    def clean(self):
        cleaned_data = super(ProfileForm, self).clean()
        password = cleaned_data.get("password")
        repeated_password = cleaned_data.get("repeated_password")
        if password and repeated_password:
            if password != repeated_password:
                raise forms.ValidationError("Las contraseñas no coinciden.")
