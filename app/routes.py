from datetime import datetime
from flask import render_template, url_for, redirect, flash
from flask_login import (
    current_user,
    login_user,
    logout_user,
    login_required
)

from app import app, db
from app.models import User, Item, Bid
from app.forms import (
    LoginForm,
    RegistrationForm,
    ItemRegisterForm,
    BidRegisterForm,
)


# Rotas

# Rota de index
# + -------------------------------------------------------------------------- +
@app.route('/', methods=['GET', 'POST'])
@app.route('/index', methods=['GET', 'POST'])
def index():

    # Formulário
    form = ItemRegisterForm()

    # validando o formulário
    if form.validate_on_submit():

        # Caso a data limite seleciona já esteja passado
        now = datetime.utcnow().date()
        if now > form.expires_in.data:
            flash("A data tem que ser maior que o dia de hoje.")
            return redirect(url_for('index'))

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
# + -------------------------------------------------------------------------- +


# Roda de logout
# + -------------------------------------------------------------------------- +
@app.route('/logout')
@login_required
def logout():
    logout_user()

    return redirect(url_for('index'))
# + -------------------------------------------------------------------------- +


# Rota de login
# + -------------------------------------------------------------------------- +
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
        flash("Bem vindo, {}!".format(user.username))

        return redirect(url_for('index'))
    
    return render_template('login.html', form=form)
# + -------------------------------------------------------------------------- +


# Rota de registro de usuários
# + -------------------------------------------------------------------------- +
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
# + -------------------------------------------------------------------------- +


# Rota de detalhes sobre o item
# + -------------------------------------------------------------------------- +
@app.route('/item/<id>/', methods=['GET', 'POST'])
def item(id):

    # Buscando o item
    item = Item.query.filter_by(id=id).first_or_404()

    # buscando a melhor oferta neste item
    best_bid = Bid.query.filter_by(item=item, best_bid=True).first()
    if best_bid == None:
        item.best_bid = item.initial_price
    else:
        item.best_bid = best_bid

    # Formulário.
    form = BidRegisterForm()

    # formulário enviado.
    if form.validate_on_submit():
        
        # caso o usuário seja o dono do item.
        if item.owner.id == current_user.id:
            flash("Desculpe, você não pode dar lances no seu próprio item.")
            return redirect(url_for('item', id=item.id))
        
        """ Tratamento de erros | -------------------------------------------"""
        # 01 - caso já tenha passado do período de lances abertos.
        now = datetime.utcnow()
        if now > item.expires_in:
            flash("Desculpe, o período de lances deste item já passou.")
            return redirect(url_for('item', id=item.id))

        # 02 - caso o preço do lance seja menor que o valor estipulado pelo dono.
        min_value = item.initial_price
        bid_value = form.value.data
        if min_value > bid_value:
            flash("O valor do lance deve ser maior que preço mínimo.")
            return redirect(url_for('item', id=item.id))

        # 03 - caso o lance seja menor que o maior já feito.
        for bid in item.bids:
            if bid.value > bid_value:
                flash("O valor do lance deve ser maior que os lances já feitos.")
                return redirect(url_for('item', id=item.id))


        # Setando False na antiga melhor oferta
        if best_bid is not None:
            best_bid.best_bid = False
            db.session.commit()
        
        # Salvando o novo lance na base de dados.
        bid = Bid(
            value=form.value.data,
            item=item,
            author=current_user,
            best_bid=True
        )

        db.session.add(bid)
        db.session.commit()


        flash("Parabéns! Novo lance feito cadastrado com sucesso.")
        return redirect(url_for('item', id=item.id))

    # Item não encontrado.
    if item is None:
        flash("Item {} não encontrado".format(item_id))
        
        return redirect(url_for('index'))
    
    return render_template('item.html', form=form, item=item)
# + -------------------------------------------------------------------------- +
