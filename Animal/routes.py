from flask import Blueprint, Response, request, flash, render_template, redirect
from Models.User import UsersManage
from Models.Animals import AnimalsManage
from Models.Images import filter_animal_image, insert_image


bp_animal = Blueprint('Animal', __name__, template_folder='templates')


@bp_animal.route("/cadastro/animal", methods=["POST", "GET"])
def register_animal():

    if request.method == 'POST':
        body = request.get_json()

        user_verify = UsersManage.verify_user(
            body["nome"], body["password"]
            )

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


@bp_animal.route('/Animal/adicionar-foto', methods=['POST'])
def adicionar_foto():
    file = request.files['imagem']
    body = request.form

    if UsersManage.verify_user(body['nome'], body['password']):
        minetype = file.mimetype
        insert_image(file, body['nomeAnimal'], minetype)
        return {'Sucesso': 'foto do animal adicionado!!'}

    else:
        return {'ERROR': 'voce não tem permissão para isso'}


@bp_animal.route("/Animal/modificar", methods=["PUT"])
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

@bp_animal.route("/Animal/deletar", methods=["DELETE"])
def delete_animal():
    body = request.get_json()

    user_verify = UsersManage.verify_user(body["nome"], body["password"])

    if user_verify:
        AnimalsManage.delete_animal_origin(body["nomeAnimalDelete"])

        return {"Sucesso": "Animal deletado"}

    else:
        {"Error": "usuario não econtrado"}

@bp_animal.route("/Animal/mostrar-informações", methods=["POST"])
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

@bp_animal.route("/Animal/imagem/<nomeAnimal>", methods=["GET"])
def show_animal_picture(nomeAnimal):
    animal_or_eception = filter_animal_image(nomeAnimal.capitalize())

    try:
        return Response(animal_or_eception.img, mimetype=animal_or_eception.mimetype)
    except:
        return {'ERROR': 'Aninaml não encontrado'}
