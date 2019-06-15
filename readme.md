<h1>Instalação</h1>


<h2>Ambiente virtual</h2>

```
$ virtualenv --python='/usr/bin/python3.7' venv
$ source venv/bin/activate
```

<h2>Dependências</h2>

```
$ pip install -r requirements.txt
```

<h2>Setando o app</h2>

```
$ export FLASK_APP=manage.py
$ export FLASK_ENV=development
$ export FLASK_DEBUG=1
```

<h2>Banco de dados</h2>

```
$ flask db init
$ flask db migrate
$ flask db upgrade
```

<h2>Rodando a aplicação</h2>

```
$ flask run
```