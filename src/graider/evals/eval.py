import csv
import os
import sys
import time
from pathlib import Path

from dotenv import load_dotenv
from google import genai
from google.genai.errors import APIError
from tenacity import (
    retry,
    retry_if_exception,
    stop_after_attempt,
    wait_exponential,
)

from graider.evals.case import Case
from json_structure.json1_compared import Exam


def is_retryable_error(exception):
    return isinstance(exception, APIError) and exception.code in (429, 503)


@retry(
    retry=retry_if_exception(is_retryable_error),
    wait=wait_exponential(multiplier=2, min=2, max=30),  # Espera 2s, 4s, 8s, 16s...
    stop=stop_after_attempt(5),  # Máximo 5 intentos
)
def call_gemini(prompt, jsn_structure, question, answer, rubric):
    return client.models.generate_content(
        model="gemini-3.5-flash-lite",
        contents="<prompt>"
        + prompt
        + "</prompt>"
        + "<json>"
        + jsn_structure
        + "</json>"
        + "<exam>"
        + "<question>"
        + actual_question
        + "</question>"
        + "<answer>"
        + cas["answer"]
        + "</answer>"
        + "</exam>"
        + "<rubric>"
        + actual_rubric
        + "</rubric>",
    )


load_dotenv()

gemini_key = os.getenv("gemini_key")
client = genai.Client(api_key=gemini_key)

ruta_del_script = Path(__file__).resolve()

carpeta_base = ruta_del_script.parent

json_structure1 = carpeta_base.parent.parent / "json_structure" / "json1.txt"
prompt1 = carpeta_base.parent.parent / "propmt" / "propmt.txt"
exam_answers = carpeta_base.parent.parent / "datasets" / "exam1-answers.csv"
exam_questions = carpeta_base.parent.parent / "datasets" / "exam1-questions.csv"

if os.path.exists(json_structure1):
    with open(json_structure1, "r", encoding="utf-8") as jsn:
        jsn_structure = jsn.read()
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

if jsn_structure and prompt and exam_questions and exam_answers:
    for cas in reader_answers:
        # Question and rubric for the case-answer
        actual_question = ""
        actual_rubric = ""
        dic_cases[f"case{i}"] = []

        # Looking for the right question and rubric
        for question in reader_questions:
            if cas["id"] == question["id"]:
                actual_question = question["question"]
                actual_rubric = question["rubric"]
                break

        questions.seek(0)

        # Calling AI to solve
        for r in range(index_iterations):
            response = call_gemini(
                prompt, jsn_structure, actual_question, cas["answer"], actual_rubric
            )

            actual_case = Case()
            # Evaluating how was AI with the case compare to the case in dataset
            actual_case.set_json_message(response.text)
            if actual_case.is_valid_json():
                dict_json = actual_case.get_json_dict_message()
                dict_json_model = actual_case.get_json_message()
                if Exam.es_json_valido(dict_json_model):
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
            else:
                actual_case.set_equal_json(False)
                actual_case.set_equal_grading(False)
                actual_case.set_equal_warning(False)

            dic_cases[f"case{i}"].append(actual_case)
        i = i + 1

        # after 15 calls, needs to wait 1 min so the rpm restarts and can do 15 calls again.
        # this is mod 5 because we are doing 3 calls to ai in 5 rounds. But if we change the
        # number of calls to ai, needs to be modified.
        if i % 5 == 0:
            time.sleep(60)

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

print(dic_cases["case2"][1].get_equal_grading())
print(dic_cases["case3"][0].get_json_message())
print(dic_cases["case3"][1].get_json_message())
print(dic_cases["case3"][2].get_json_message())
