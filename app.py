from flask_openapi3 import OpenAPI, Info, Tag
from flask import redirect
from urllib.parse import unquote

from sqlalchemy.exc import IntegrityError

from model import Session, Cadastro, Comentario
from logger import logger
from schemas import *
from flask_cors import CORS

info = Info(title="Cadastro API", version="1.0.0")
app = OpenAPI(__name__, info=info)
CORS(app)

# definindo tags
home_tag = Tag(name="Documentação", description="Seleção de documentação: Swagger, Redoc ou RapiDoc")
cadastro_tag = Tag(name="Cadastro", description="Adição, visualização e remoção de cadastros à base")
comentario_tag = Tag(name="Comentario", description="Adição de um comentário à uma pessoa cadastrada na base")


@app.get('/', tags=[home_tag])
def home():
    """Redireciona para /openapi, tela que permite a escolha do estilo de documentação.
    """
    return redirect('/openapi')


@app.post('/cadastro', tags=[cadastro_tag],
          responses={"200": CadastroViewSchema, "409": ErrorSchema, "400": ErrorSchema})
def add_cadastro(form: CadastroSchema):
    """Adiciona um novo Cadastro à base de dados
    Retorna uma representação dos cadastros e comentários associados.
    """
    cadastro = Cadastro(
        usuario=form.usuario,
        cpf=form.cpf,
        email=form.email,
        senha=form.senha)
    logger.debug(f"Adicionando cadastro de usuario: '{cadastro.usuario}'")
    try:
        # criando conexão com a base
        session = Session()
        # adicionando cadastro
        session.add(cadastro)
        # efetivando o comando de adição de novo item na tabela
        session.commit()
        logger.debug(f"Adicionado cadastro de usuario: '{cadastro.usuario}'")
        return apresenta_cadastro(cadastro), 200

    except IntegrityError as e:
        # como a duplicidade do nome é a provável razão do IntegrityError
        error_msg = "Cadastro de mesmo nome já salvo na base :/"
        logger.warning(f"Erro ao adicionar cadastro '{cadastro.usuario}', {error_msg}")
        return {"mesage": error_msg}, 409

    except Exception as e:
        # caso um erro fora do previsto
        error_msg = "Não foi possível salvar novo item :/"
        logger.warning(f"Erro ao adicionar o cadastro '{cadastro.usuario}', {error_msg}")
        return {"mesage": error_msg}, 400


@app.get('/cadastros', tags=[cadastro_tag],
         responses={"200": ListagemCadastrosSchema, "404": ErrorSchema})
def get_cadastros():
    """Faz a busca por todos os cadastrados
    Retorna uma representação da listagem dos cadastrados.
    """
    logger.debug(f"Coletando cadastros ")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    cadastros = session.query(Cadastro).all()

    if not cadastros:
        # se não há produtos cadastrados
        return {"cadastros": []}, 200
    else:
        logger.debug(f"%d cadastros econtrados" % len(cadastros))
        # retorna a representação do cadastro
        print(cadastros)
        return apresenta_cadastros(cadastros), 200


@app.get('/cadastro', tags=[cadastro_tag],
         responses={"200": CadastroViewSchema, "404": ErrorSchema})
def get_cadastro(query: CadastroBuscaSchema):
    """Faz a busca por um Cadastro a partir do id do cadastro
    Retorna uma representação dos cadastrados e comentários associados.
    """
    cadastro_id = query.id
    logger.debug(f"Coletando dados sobre cadastro #{cadastro_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca
    cadastro = session.query(Cadastro).filter(Cadastro.id == cadastro_id).first()

    if not cadastro:
        # se o cadastro não foi encontrado
        error_msg = "Cadastro não encontrado na base :/"
        logger.warning(f"Erro ao buscar cadastro '{cadastro_id}', {error_msg}")
        return {"mesage": error_msg}, 404
    else:
        logger.debug(f"Cadastro econtrado: '{cadastro.usuario}'")
        # retorna a representação do cadastrro
        return apresenta_cadastro(cadastro), 200


@app.delete('/cadastro', tags=[cadastro_tag],
            responses={"200": CadastroDelSchema, "404": ErrorSchema})
def del_cadastro(query: CadastroBuscaSchema):
    """Deleta um Cadastro a partir do id informado
    Retorna uma mensagem de confirmação da remoção.
    """
    cadastro_usuario = unquote(unquote(query.usuario))
    print(cadastro_usuario)
    logger.debug(f"Deletando dados sobre o cadastro #{cadastro_usuario}")
    # criando conexão com a base
    session = Session()
    # fazendo a remoção
    count = session.query(Cadastro).filter(Cadastro.usuario == cadastro_usuario).delete()
    session.commit()

    if count:
        # retorna a representação da mensagem de confirmação
        logger.debug(f"Deletado cadastro #{cadastro_usuario}")
        return {"mesage": "Cadastro removido", "id": cadastro_usuario}
    else:
        # se o cadastro não foi encontrado
        error_msg = "Cadastro não encontrado na base :/"
        logger.warning(f"Erro ao deletar cadastro #'{cadastro_usuario}', {error_msg}")
        return {"mesage": error_msg}, 404


@app.post('/comentario', tags=[comentario_tag],
          responses={"200": CadastroViewSchema, "404": ErrorSchema})
def add_comentario(form: ComentarioSchema):
    """Adiciona de um novo comentário à um cadastrado na base identificado pelo id
    Retorna uma representação dos cadastrados e comentários associados.
    """
    cadastro_id  = form.cadastro_id
    logger.debug(f"Adicionando comentários ao cadastro #{cadastro_id}")
    # criando conexão com a base
    session = Session()
    # fazendo a busca pelo cadastro
    cadastro = session.query(Cadastro).filter(Cadastro.id == cadastro_id).first()

    if not cadastro:
        # se cadastro não encontrado
        error_msg = "Cadastro não encontrado na base :/"
        logger.warning(f"Erro ao adicionar comentário ao cadastro '{cadastro_id}', {error_msg}")
        return {"mesage": error_msg}, 404

    # criando o comentário
    texto = form.texto
    comentario = Comentario(texto)

    # adicionando o comentário ao cadastro
    cadastro.adiciona_comentario(comentario)
    session.commit()

    logger.debug(f"Adicionado comentário ao cadastro #{cadastro_id}")

    # retorna a representação do cadastro
    return apresenta_cadastro(cadastro), 200