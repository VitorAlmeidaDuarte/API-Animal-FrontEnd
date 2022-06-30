
from Models.User import UsersManage, Users
from config import app_config, app_active
from flask import Flask, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user
from Animal.routes import bp_animal


config = app_config[app_active]


def create_app(condig_name):
    app = Flask(__name__, template_folder="templates")

    app.secret_key = config.SECRET
    app.config.from_object(app_config[condig_name])
    app.config.from_pyfile("config.py")
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False
    app.register_blueprint(bp_animal)

    db = SQLAlchemy(config.APP)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @app.route('/')
    def index():
        return render_template('index.html')

    @app.route('/admin')
    @login_required      
    def admin():
        return render_template('/admin.html')           

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(id=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Você precisa estar logado para acessar essa pagina')    
        return redirect('/login')


    @app.route('/login', methods=['GET'])
    def login():
        return render_template('login.html')
    

    @app.route('/autenticar', methods=['POST'])
    def autenticar():
        usuario = request.form.get('usuario')
        senha = request.form.get('senha')

        test_user, str_error, objeto_usuario = UsersManage.verify_user(usuario, senha)
       
        if test_user:
            login_user(objeto_usuario)
            return redirect('/admin')
        else:
            flash(str_error)
            return redirect('/login')

    @app.route("/logout", methods=['GET'])
    @login_required
    def logout():
        logout_user()
        return redirect('/login')            


    return app