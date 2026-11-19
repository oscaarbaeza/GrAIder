# GrAIder

GrAIder es un sistema de inteligencia artificial que ayuda a los profesores a ahorrar tiempo corrigiendo exámenes. GrAIder corrige y pone nota a cada ejercicio basándose en la rúbrica que le proporciona el profesor. Después, el profesor revisa las justificaciones que ha dado GrAIder para cada respuesta y las valida.

## Cómo funciona

GrAIder solo necesita la rúbrica del examen y el examen del alumno, cada uno en su carpeta (`/rubrics` y `/exams`). Con eso, corrige el examen ejercicio por ejercicio: puntúa cada respuesta y explica la nota según la rúbrica. El profesor recibe el examen corregido, que solo tiene que revisar y validar.

GrAIder usa el modelo `gemini-3.5-flash-lite` y valida su salida con Pydantic para comprobar que sigue la estructura JSON establecida. Este es el JSON que devuelve ahora mismo (se puede cambiar en `/json_structure`):

json

```json
{
  "examen": {
    "preguntas": [
      {
        "pregunta_numero": "int",
        "enunciado": "string",
        "respuesta_alumno": "string",
        "correccion": {
          "justificacion": "string",
          "puntos_obtenidos": "float"
        },
        "aviso": "boolean"
      }
    ],
    "observaciones": "string"
  }
}
```

El modelo de Pydantic de cada JSON está en la misma carpeta, con el mismo nombre más `_compared`.

## Instalación y uso

bash

```bash
git clone https://github.com/oscaarbaeza/GrAIder
cd GrAIder
uv sync
# crea un fichero .env con: GEMINI_API_KEY=tu_clave
uv run main.py   # corrige el examen
uv run eval.py   # lanza la evaluación
```

## Evaluación

Para comprobar que GrAIder hace bien su trabajo, he diseñado `eval.py` con sus datasets: preguntas, respuestas de alumnos y las notas que yo les pondría. El eval compara la corrección de GrAIder con la mía y, cuando no coinciden, da pistas de por qué, para poder ajustar el prompt o el modelo.

Son 20 respuestas corregidas a mano, 7 de ellas intentos de prompt injection. Cada una se lanza 3 veces porque el modelo no responde siempre igual. Este es el resultado para un examen y su rúbrica:

|Métrica|Resultado|
|---|---|
|JSON válido|60/60|
|Estructura correcta|60/60|
|Misma nota que la corrección manual|48/60 (80 %)|
|Aviso de prompt injection correcto|60/60|

El examen de prueba no es difícil y aun así la nota de GrAIder no coincide con la mía en 12 de las 60 correcciones, concentradas en los casos 3, 6, 7, 12 y 20. Algunos de estos casos tienen respuestas ambiguas en el propio dataset, así que el siguiente paso es revisarlos uno a uno. En el resto de métricas, GrAIder acierta siempre: detecta los 7 ataques sin falsos positivos.

## Seguridad

En una aplicación con IA hay que evitar el prompt injection: que un alumno escriba en su respuesta instrucciones para cambiar el comportamiento del modelo. GrAIder tiene varias capas de defensa:

1. Un prompt con el rol bien definido, que trata las respuestas de los alumnos como datos que hay que corregir y nunca como instrucciones.
2. Se eliminan los caracteres `<` y `>` de las respuestas, para que no interfieran con las etiquetas del prompt.
3. Un campo `aviso` en el JSON que indica si GrAIder ha detectado un intento de prompt injection.
4. El profesor revisa siempre la corrección: nunca se entrega directamente al alumno.

## Lo que aprendí

1. **Cada llamada empieza de cero.** Cada llamada al modelo es una conversación nueva, sin el contexto de las anteriores. Por eso cada llamada incluye el prompt con el rol, el examen, la rúbrica y la estructura JSON que debe seguir.
2. **El orden de los campos importa.** El modelo genera el texto de izquierda a derecha. Cuando la nota iba antes que la justificación, primero decidía un número y después escribía una explicación para defenderlo, aunque estuviera mal. Cambié el orden para que justifique primero y puntúe después, y modifiqué el prompt para que la nota salga de esa justificación y no se invente ninguna.
3. **El modelo solo sabe lo que le dices.** En los ejercicios de «rodea», se lo tomaba tan al pie de la letra que, aunque el alumno escribiera las letras correctas, no lo daba por bueno porque no había rodeado nada. La solución fue explicarle en el prompt de dónde salen las respuestas: son transcripciones de un examen en papel, y lo que el alumno escribe es lo que habría marcado.

## Limitaciones y siguientes pasos

- Corregir varios exámenes en lote (ahora corrige uno por ejecución).
- Revisar los casos del eval que fallan (3, 6, 7, 12 y 20) y añadir tolerancia al comparar notas con decimales.
- Añadir más capas de protección: comprobar que no se superan los puntos máximos de cada ejercicio y limpiar caracteres invisibles.
- Ordenar y limpiar el código.