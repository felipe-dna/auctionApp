from flask import render_template, url_for, redirect, flash
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)

from app import app, db
from app.models import User, Item
from app.forms import LoginForm, RegistrationForm, ItemRegisterForm


@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():
    form = ItemRegisterForm()

    # validando o formulário
    if form.validate_on_submit():
        
        # Nova instância de Item
        new_item = Item(
            name=form.name.data,
            initial_price=form.initial_price.data,
            expires_in=form.expires_in.data,
            owner=current_user
        )

        # salvando
        db.session.add(new_item)
        db.session.commit()

        # redirecionando
        flash("Novo Item cadastrado e pronto para os lances!")
        return redirect(url_for('index'))

    # Buscando todos os itens cadastrados
    itens = Item.query.order_by(Item.posted_at.desc()).all()

    return render_template('index.html', itens=itens, form=form)


@app.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('index'))


@app.route('/login', methods=['GET', 'POST'])
def login():

    # Se o usuário já esta logado ele redireciona para a página inicial
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Atribuindo o formulário
    form = LoginForm()

    # Formulário é enviado:
    if form.validate_on_submit():
        user = User.query.filter_by(username=form.username.data).first()
        
        if user is None or not user.check_password(form.password.data):
            flash('Nome de usuário ou senha inválida.')
            
            return redirect(url_for('login'))
        
        login_user(user, remember=form.remember_me.data)
        flash("Bem vindo!")

        return redirect(url_for('index'))
    
    return render_template('login.html', form=form)


@app.route('/register', methods=['GET', 'POST'])
def register():

    # Se o usuário estiver logado, ele redireciona para a página inicial.
    if current_user.is_authenticated:
        return redirect(url_for('index'))
    
    # Formulário.
    form = RegistrationForm()

    # Chamado quando o formulário é enviado e validado.
    if form.validate_on_submit():

        user = User(username=form.username.data, email=form.email.data)
        user.set_password(form.password1.data)

        db.session.add(user)
        db.session.commit()

        login_user(user)

        flash("Bem vindo, {}".format(user.username))

        return redirect(url_for('index'))

    return render_template('register.html', form=form)


@app.route('/item/<id>/')
def item(id):
    item = Item.query.filter_by(id=id)

    if item is None:
        flash("Item {} não encontrado".format(item_id))
        
        return redirect(url_for('index'))
    
    return render_template('item.html', item=item)