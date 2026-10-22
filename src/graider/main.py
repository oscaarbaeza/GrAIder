import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("gemini_key")
genai.configure(api_key=gemini_key)

model = genai.GenerativeModel("gemini-3.5-flash-lite")

response = model.generate_content("Hola, ¿cómo estás?")
print(response)

rubric1 = "../rubrics/rubric1.txt"
exam1 = "../exams/exam1.txt"
json_structure1 = "../json-structure/json1.txt"

# Getting all the needed files
if os.path.exists(rubric1):
    with open(rubric1, "r", encoding="utf-8") as rub:
        rubric = rub.read()

if os.path.exists(exam1):
    with open(exam1, "r", encoding="utf-8") as exa:
        exam = exa.read()

if os.path.exists(rubric1):
    with open(json_structure1, "r", encoding="utf-8") as jsn:
        json = jsn.read()

if exam and rubric and json:
    print("hola")
