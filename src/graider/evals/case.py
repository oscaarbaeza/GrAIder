import json


class Case:
    def __init__(
        self,
        json_message=None,
        json_valid=False,
        equal_json=False,
        equal_grading=False,
        equal_warning=False,
    ):
        self.json_message = json_message
        self.json_valid = json_valid
        self.equal_json = equal_json
        self.equal_grading = equal_grading
        self.equal_warning = equal_warning

    def clean_json(self, json_dirty):
        json_clean = json_dirty.strip()

        if json_clean.startswith("```"):
            lines = json_clean.splitlines()

            if lines[0].startswith("```"):
                lines.pop(0)

            if lines and lines[-1].strip() == "```":
                lines.pop()

            json_clean = "\n".join(lines).strip()

        return json_clean

    def is_valid_json(self):
        self.json_message = self.clean_json(self.json_message)
        try:
            # Try to decode the json message
            json.loads(self.json_message)
            self.json_valid = True
            return True
        except json.JSONDecodeError:
            # If fail, the format is not json valid
            self.json_valid = False
            return False

    def set_json_message(self, json_message):
        self.json_message = json_message

    def set_json_valid(self, json_valid):
        self.json_valid = json_valid

    def set_equal_json(self, equal_json):
        self.equal_json = equal_json

    def set_equal_grading(self, equal_grading):
        self.equal_grading = equal_grading

    def set_equal_warning(self, equal_warning):
        self.equal_warning = equal_warning

    def get_json_message(self):
        return self.json_message

    def get_json_valid(self):
        return self.json_valid

    def get_json_dict_message(self):
        return json.loads(self.json_message)

    def get_equal_json(self):
        return self.equal_json

    def get_equal_grading(self):
        return self.equal_grading

    def get_equal_warning(self):
        return self.equal_warning
