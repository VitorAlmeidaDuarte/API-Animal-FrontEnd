
from Models.Animals import AnimalsManage, Animals
from Models.Images import filter_animal_image, insert_image
from Models.User import UsersManage, Users
from config import app_config, app_active
from flask import Flask, Response, request, render_template, redirect, flash
from flask_sqlalchemy import SQLAlchemy
from flask_login import LoginManager, login_required, login_user, logout_user


config = app_config[app_active]


def create_app(condig_name):
    app = Flask(__name__, template_folder="templates")

    app.secret_key = config.SECRET
    app.config.from_object(app_config[condig_name])
    app.config.from_pyfile("config.py")
    app.config["SQLALCHEMY_DATABASE_URI"] = config.SQLALCHEMY_DATABASE_URI
    app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

    db = SQLAlchemy(config.APP)
    db.init_app(app)

    login_manager = LoginManager()
    login_manager.init_app(app)

    @login_manager.user_loader
    def load_user(user_id):
        return Users.query.filter_by(id=user_id).first()

    @login_manager.unauthorized_handler
    def unauthorized():
        flash('Você precisa estar logado para acessar essa pagina')    
        return redirect('/login')


    @app.route('/')
    def index():
        return render_template('index.html')


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

    @app.route('/admin')
    @login_required      
    def admin():
        animais = Animals.query.all()

        return render_template('/admin.html', animais=animais)


    @app.route("/Cadastro/animal", methods=["POST"])
    def register_animal():
        body = request.get_json()

        user_verify = UsersManage.verify_user(body["nome"], body["password"])

        if user_verify == True:
            AnimalsManage.insert_animal_banco(
                body["nomeAnimal"],
                body["qtnEspecies"],
                body["comportamento"],
                body["alimentacao"],
            )

            return {
                "Sucesso": "Animal adicionado, não esqueça de adicionar uma foto dele :)"
            }

        else:
            return {"ERROR": "usuario não encontrado"}

    
    @app.route('/Animal/adicionar-foto', methods=['POST'])
    def adicionar_foto():
        file = request.files['imagem']
        body = request.form

        if UsersManage.verify_user(body['nome'], body['password']):
            minetype = file.mimetype
            insert_image(file, body['nomeAnimal'], minetype)
            return {'Sucesso': 'foto do animal adicionado!!'}

        else:
            return {'ERROR': 'voce não tem permissão para isso'}


    @app.route("/Animal/imagem/<nomeAnimal>", methods=["GET"])  
    def show_animal_picture(nomeAnimal):
        animal_or_eception = filter_animal_image(nomeAnimal.capitalize())
        
        try:
            return Response(animal_or_eception.img, mimetype=animal_or_eception.mimetype)
        except:
            return {'ERROR': 'Aninaml não encontrado'}
        
    @app.route("/Animal/modificar", methods=["PUT"])
    def edit_animal():
        body = request.get_json()

        user_verify = UsersManage.verify_user(body["nome"], body["password"])

        if user_verify == True:
            AnimalsManage.modify_animal_origin(
                nomeAnimal_modify=body["nomeAnimalModificate"],
                new_qtn_especies=body["newQtnEspecies"],
                new_alimentacao=body["newAlimentacao"],
            )

            return {"Sucesso": "animal modificado com exito"}

        else:
            return {"Error": "usuario não encontrado"}

    @app.route("/Animal/deletar", methods=["DELETE"])
    def delete_animal():
        body = request.get_json()

        user_verify = UsersManage.verify_user(body["nome"], body["password"])

        if user_verify:
            AnimalsManage.delete_animal_origin(body["nomeAnimalDelete"])

            return {"Sucesso": "Animal deletado"}

        else:
            {"Error": "usuario não econtrado"}

    @app.route("/Animal/mostrar-informações", methods=["POST"])
    def show_information_animals():
        nomeAnimal = request.form.get('nomeAnimal')

        if nomeAnimal == '':
            flash('Escreva um nome de um animal')
            return redirect('/')

        inf_animal = AnimalsManage.show_animals(nomeAnimal.capitalize())

        if inf_animal:
            return render_template('animal_inf.html', inf_animal=inf_animal)
        else:
            flash('Animal não econtrado')
            return redirect('/')            

    return app