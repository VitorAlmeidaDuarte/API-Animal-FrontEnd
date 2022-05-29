from flask_login.mixins import UserMixin
from flask_sqlalchemy import SQLAlchemy
from config import app_config, app_active
from passlib.hash import pbkdf2_sha512


config = app_config[app_active]

db = SQLAlchemy(config.APP)



class HashPassword():
    def create_hash(password):
        pass_hash = pbkdf2_sha512.hash(password.encode("utf-8"))

        return pass_hash


    def verify_hash(password, hash_password):
        if pbkdf2_sha512.verify(password, hash_password):
            return True

        else:
            return False
    

class Users(db.Model, UserMixin):
    id = db.Column(db.Integer, primary_key=True)
    nome = db.Column(db.String(40))
    hash = db.Column(db.LargeBinary)
    admin = db.Column(db.Boolean, default=0)

'''
@property
def is_authenticated(self):
    return True

@property
def is_active(self):
    return True

@property
def is_anonymous(self):
    return True

@property
def get_id(self):
    return str(self.id)     
'''

class UsersManage():
    def verify_user(nome, senha):
        objeto_usuario = Users.query.filter_by(nome=nome).first()

        if objeto_usuario == None:
            return False, 'Login ou senha incorretos'
        
        senha_vereficada = HashPassword.verify_hash(senha, objeto_usuario.hash)

        if senha_vereficada:
            return True, None, objeto_usuario
        else:
            return False, 'Login ou senha incorretos', None

    def insert_user_banco(nome_recebido, senha_recebida):

        if Users.query.filter_by(nome=nome_recebido).all():
            return False

        else:
            

            senha_convertida_in_hash = HashPassword.create_hash(senha_recebida)
            usuario = Users(
                    nome=nome_recebido,
                    hash=senha_convertida_in_hash.encode('utf-8'),
                )

            db.session.add(usuario)
            db.session.commit()
            return True
