import os

import google.generativeai as genai
from dotenv import load_dotenv

load_dotenv()

gemini_key = os.getenv("gemini_key")
genai.configure(api_key=gemini_key)

model = genai.GenerativeModel("gemini-3.5-flash-lite")

# Simulating call to AI
# response = model.generate_content("Hola, ¿cómo estás?")
# print(response)

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
    response = model.generate_content(propmt + json + exam + rubric)

response_json = response._result.candidates[0].content.parts[0].text
