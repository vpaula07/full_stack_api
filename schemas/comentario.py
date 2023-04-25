from pydantic import BaseModel


class ComentarioSchema(BaseModel):
    """ Define como um novo comentário a ser inserido deve ser representado
    """
    cadastro_id: int = 1
    texto: str = "Só cadastrar uauários válidos com cpf !"