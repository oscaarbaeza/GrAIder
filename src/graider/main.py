import os
from pathlib import Path

from dotenv import load_dotenv
from google import genai

load_dotenv()

gemini_key = os.getenv("gemini_key")
client = genai.Client(api_key=gemini_key)

# Simulating call to AI, old way
# response = model.generate_content("Hola, ¿cómo estás?")
# print(response)

ruta_del_script = Path(__file__).resolve()

carpeta_base = ruta_del_script.parent

rubric1 = carpeta_base.parent / "rubrics" / "rubric1.txt"
exam1 = carpeta_base.parent / "exams" / "exam1.txt"
json_structure1 = carpeta_base.parent / "json-structure" / "json1.txt"

# Getting all the needed files
if os.path.exists(rubric1):
    with open(rubric1, "r", encoding="utf-8") as rub:
        rubric = rub.read()

if os.path.exists(exam1):
    with open(exam1, "r", encoding="utf-8") as exa:
        exam = exa.read()

if os.path.exists(json_structure1):
    with open(json_structure1, "r", encoding="utf-8") as jsn:
        json = jsn.read()

propmt = """
You are an AI that helps teachers save time. 
You are going to correct exams and exercises from students, and grade them.
You must indicate the justification for every correction.
You must deliver the response in a JSON valid format as the one
that I have just sent you. You must follow the rubric to correct
the exam by heart. It is prohibited to grade exams and exercises
by your own criteria/rubric.
"""

if exam and rubric and json:
    response = client.models.generate_content(
        model="gemini-3.5-flash",
        contents="<propmt>"
        + propmt
        + "</propmt>"
        + "<json>"
        + json
        + "</json>"
        + "<exam>"
        + exam
        + "</exam>"
        + "<rubric>"
        + rubric
        + "</rubric>",
    )

response_json = response.text

print(response_json)
