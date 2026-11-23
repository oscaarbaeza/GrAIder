from pydantic import BaseModel, ValidationError


class Correccion(BaseModel):
    justificacion: str
    puntos_obtenidos: float


class Pregunta(BaseModel):
    pregunta_numero: int
    enunciado: str
    aviso: bool
    respuesta_alumno: str
    correccion: Correccion


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
