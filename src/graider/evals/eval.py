import csv
import os
import sys
import json
from pathlib import Path

from dotenv import load_dotenv
from google import genai

from graider.evals.case import Case

load_dotenv()

gemini_key = os.getenv("gemini_key")
client = genai.Client(api_key=gemini_key)

ruta_del_script = Path(__file__).resolve()

carpeta_base = ruta_del_script.parent

json_structure1 = carpeta_base.parent.parent / "json-structure" / "json1.txt"
prompt1 = carpeta_base.parent.parent / "propmt" / "propmt.txt"
exam_answers = carpeta_base.parent.parent / "datasets" / "exam1-answers.csv"
exam_questions = carpeta_base.parent.parent / "datasets" / "exam1-questions.csv"

if os.path.exists(json_structure1):
    with open(json_structure1, "r", encoding="utf-8") as jsn:
        json_structure = jsn.read()
else:
    print("No json-structure")
    sys.exit(1)

if os.path.exists(prompt1):
    with open(prompt1, "r", encoding="utf-8") as pr:
        prompt = pr.read()
else:
    print("No prompt")
    sys.exit(1)

if os.path.exists(exam_answers):
    answers = open(exam_answers, "r", encoding="utf-8-sig")
else:
    print("No exam-answers")
    sys.exit(1)

if os.path.exists(exam_questions):
    questions = open(exam_questions, "r", encoding="utf-8-sig")
else:
    print("No exam-questions")
    sys.exit(1)

reader_answers = csv.DictReader(answers)
reader_questions = csv.DictReader(questions)

dic_cases = {}
# Count cases
i = 1
# Used to identify how many iterations we want that AI calls for each questions/answer
index_iterations = 3

if json_structure and prompt and exam_questions and exam_answers:
    for cas in reader_answers:
        # Question and rubric for the case-answer
        actual_question = ""
        actual_rubric = ""
        dic_cases[f"case{i}"] = []
        actual_case = Case()

        # Looking for the right question and rubric
        for question in reader_questions:
            if cas["id"] == question["id"]:
                actual_question = question["question"]
                actual_rubric = question["rubric"]
                break

        questions.seek(0)

        # Calling AI to solve
        for r in range(index_iterations):
            response = client.models.generate_content(
                model="gemini-3.5-flash-lite",
                contents="<prompt>"
                + prompt
                + "</prompt>"
                + "<json>"
                + json_structure
                + "</json>"
                + "<exam>"
                + "<question>"
                + actual_question
                + "</question"
                + "<answer>"
                + cas["answer"]
                + "</answer"
                + "</exam>"
                + "<rubric>"
                + actual_rubric
                + "</rubric>",
            )

            # Evaluating how was AI with the case compare to the case in dataset
            actual_case.set_json_message(response.text)
            actual_case.is_valid_json()

            dict_json = actual_case.get_json_dict_message()
            if dict_json.keys() == json.loads(json_structure).keys():
                actual_case.set_equal_json(True)
            # In this case, the requirement is having the same grading as me. But
            # it could be that in the future i want to change this to depends on variations. (+-.5)
            if dict_json["examen"]["preguntas"][0]["correccion"][
                "puntos_obtenidos"
            ] == float(cas["grade"]):
                actual_case.set_equal_grading(True)

            if dict_json["examen"]["preguntas"][0]["aviso"] == bool(
                int(cas["warning"])
            ):
                actual_case.set_equal_warning(True)

            dic_cases[f"case{i}"].append(actual_case)
        i = i + 1

        # It is just for 4 cases, because of the 15 calls in 1 min limit.
        if i == 5:
            break

answers.close()
questions.close()

json_valid_counter = 0
json_valid_counter_total = 0
equal_json_counter = 0
equal_json_counter_total = 0
equal_grading_counter = 0
equal_grading_counter_total = 0
equal_warning_counter = 0
equal_warning_counter_total = 0

index = 1
print("case: json_valid - equal_json - equal_grading - equal_warning")
for dic in dic_cases.values():
    for r in range(len(dic)):
        if dic[r].get_json_valid() == True:
            json_valid_counter = json_valid_counter + 1
            json_valid_counter_total = json_valid_counter_total + 1

        if dic[r].get_equal_json() == True:
            equal_json_counter = equal_json_counter + 1
            equal_json_counter_total = equal_json_counter_total + 1

        if dic[r].get_equal_grading() == True:
            equal_grading_counter = equal_grading_counter + 1
            equal_grading_counter_total = equal_grading_counter_total + 1

        if dic[r].get_equal_warning() == True:
            equal_warning_counter = equal_warning_counter + 1
            equal_warning_counter_total = equal_warning_counter_total + 1

    print(
        "case"
        + str(index)
        + ": "
        + "   "
        + str(json_valid_counter)
        + "/"
        + str(index_iterations)
        + "   "
        + "-"
        + "   "
        + str(equal_json_counter)
        + "/"
        + str(index_iterations)
        + "   "
        + "-"
        + "   "
        + str(equal_grading_counter)
        + "/"
        + str(index_iterations)
        + "   "
        + "-"
        + "   "
        + str(equal_warning_counter)
        + "/"
        + str(index_iterations)
    )

    index = index + 1

    json_valid_counter = 0
    equal_json_counter = 0
    equal_grading_counter = 0
    equal_warning_counter = 0

print(
    "total:"
    + "   "
    + str(json_valid_counter_total)
    + "   "
    + "-"
    + "   "
    + str(equal_json_counter_total)
    + "   "
    + "-"
    + "   "
    + str(equal_grading_counter_total)
    + "   "
    + "-"
    + "   "
    + str(equal_warning_counter_total)
)
