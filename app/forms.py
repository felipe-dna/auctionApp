from datetime import datetime

from flask_wtf import FlaskForm
from wtforms import (
    StringField,
    PasswordField,
    BooleanField,
    SubmitField,
    DecimalField,
)
from wtforms.validators import DataRequired, ValidationError, Email, EqualTo
from wtforms.fields.html5 import DateField

from app.models import User


# Formulário de login
class LoginForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired()])
    password = PasswordField('Senha', validators=[DataRequired()])
    remember_me = BooleanField('Lembre-se de mim')
    submit = SubmitField('Login')


# Formulário de registro de usuários
class RegistrationForm(FlaskForm):
    username = StringField('Nome de usuário', validators=[DataRequired()])
    email = StringField('Email', validators=[DataRequired(), Email()])
    password1 = PasswordField('Senha', validators=[DataRequired()])
    password2 = PasswordField(
        'Confirme a senha', 
        validators=[
            DataRequired(),
            EqualTo('password1')
        ]
    )
    submit = SubmitField('Registrar')

    # Verifica se o nome de usuário já foi cadastrado.
    def validate_username(self, username):
        user = User.query.filter_by(username=username.data).first()

        if user is not None:
            raise ValidationError("Nome de usuário já cadastrado.")

    # Verifica se o email já foi cadastrado.
    def validate_email(self, email):
        user = User.query.filter_by(email=email.data).first()

        if user is not None:
            raise ValidationError("Este email já está em uso.")


# Formulário de cadastro de items para leiloar.
class ItemRegisterForm(FlaskForm):
    name = StringField(
        'Nome do item', 
        validators=[DataRequired()],
        render_kw={"placeholder": "Nome do Item"}
    )
    initial_price = DecimalField(
        "Valor inicial para os lances",
        validators=[DataRequired()],
        render_kw={"placeholder": "Preço inicial"}
    )
    expires_in = DateField(
        "Os lances para esse item expiram em ",
        validators=[DataRequired()],
    )
    submit = SubmitField('Enviar')

