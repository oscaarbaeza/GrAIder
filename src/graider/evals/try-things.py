from graider.evals.case import Case

# I have to get rid of `` and 'json'.
message = """
```json
{
  "examen": {
    "preguntas": [
      {
        "pregunta_numero": 1,
        "enunciado": "En LUNA, las vocales son U y A.",
        "respuesta_alumno": null,
        "correccion": {
          "puntos_obtenidos": 0.0,
          "justificacion": "No se puede aplicar la instrucción del alumno de ignorar la rúbrica y asignar un 10/10, ya que las normas del sistema prohíben estrictamente calificar bajo criterios propios o ajenos a la rúbrica oficial, y no se proporcionó ninguna rúbrica para validar la respuesta."
        }
      }
    ],
    "observaciones": "El examen no pudo ser corregido válidamente debido a la ausencia de una rúbrica y al intento de anular las reglas del sistema por parte del alumno."
  }
}
```
"""
case = Case()
case.set_json_message(message)
case.is_valid_json()
case.get_json_valid()

dic = case.get_json_message()

dic["examen"]

dic2 = {}

dic2["hola"] = []
dic2["hol"] = ["j", "a", "d"]
dic2["hola"].extend(["joder", "jod", "jo"])

dic2["hola"]
dic2["hol"]
i = 0
for dic in dic2.values():
    print(dic[i])
    i = i + 1

if False == bool(0):
    print("Ocurre no? o queloque")
