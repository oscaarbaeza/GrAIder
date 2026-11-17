from pydantic import BaseModel, ValidationError


class Correccion(BaseModel):
    puntos_obtenidos: float
    justificacion: str


class Pregunta(BaseModel):
    pregunta_numero: int
    enunciado: str
    respuesta_alumno: str
    correccion: Correccion
    aviso: bool


class Preguntas(BaseModel):
    preguntas: list[Pregunta]
    observaciones: str


class Exam(BaseModel):
    examen: Preguntas

    def es_json_valido(json_data: str) -> bool:
        try:
            Exam.model_validate_json(json_data)
            return True
        except ValidationError as e:
            for error in e.errors():
                print("Tipo:", error["type"])
                print("Campo:", error["loc"])
                print("Mensaje:", error["msg"])
            return False
