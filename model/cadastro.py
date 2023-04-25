from sqlalchemy import Column, String, Integer, DateTime, Float
from sqlalchemy.orm import relationship
from datetime import datetime
from typing import Union

from  model import Base, Comentario


class Cadastro(Base):
    __tablename__ = 'cadastro'

    id = Column("pk_cadastro", Integer, primary_key=True)
    usuario = Column(String(50), unique=True)
    cpf = Column(Integer)
    email = Column(String(120))
    senha = Column(String(10))
    data_insercao = Column(DateTime, default=datetime.now())

    # Definição do relacionamento entre o cadastrado e o comentário.
    # Essa relação é implicita, não está salva na tabela 'produto',
    # mas aqui estou deixando para SQLAlchemy a responsabilidade
    # de reconstruir esse relacionamento.
    comentarios = relationship("Comentario")

    def __init__(self, usuario:str, cpf:int, email:str, senha:str,
                 data_insercao:Union[DateTime, None] = None):
        """
        Cria um Usuário
        Arguments:
           usuario: nome do usuario cadstrado.
            cpf: inseri o cpf do usuario.
            email: e-mail do usuário a ser cadastrado.
            senha: senha que o uauário inserir.
            data_insercao: data de quando o produto foi inserido à base
        """
        self.usuario = usuario
        self.cpf = cpf
        self.email = email
        self.senha = senha

        # se não for informada, será o data exata da inserção no banco
        if data_insercao:
            self.data_insercao = data_insercao

    def adiciona_comentario(self, comentario:Comentario):
        """ Adiciona um novo comentário ao Cadastro
        """
        self.comentarios.append(comentario)