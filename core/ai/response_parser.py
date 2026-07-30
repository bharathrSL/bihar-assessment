"""Validate the LLM answer contract while tolerating harmless extra fields."""

import json
import re
import warnings

from core.models import Answer, StudentInfo


class ResponseParser:
    REQUIRED = {
        "question_id",
        "selected_codes",
        "answer_text",
        "confidence",
        "review_required",
        "raw_observations",
    }

    STUDENT_FIELDS = {
        "student_name",
        "gender",
        "school_name",
        "school_udise",
        "crc_name",
        "crc_udise",
        "block",
        "district",
        "grade",
        "meena_manch_participation",
    }

    def parse(self, text: str) -> tuple[StudentInfo, list[Answer]]:

        match = re.search(r"\{[\s\S]*\}", text)
        if not match:
            raise ValueError("AI response did not contain a JSON object")

        payload = json.loads(match.group())

        if not isinstance(payload, dict):
            raise ValueError("AI response must be a JSON object")

        if "student" not in payload:
            raise ValueError("Missing 'student' object")

        if "answers" not in payload:
            raise ValueError("Missing 'answers' array")

        student_data = payload["student"]
        answers_data = payload["answers"]

        if not isinstance(student_data, dict):
            raise ValueError("'student' must be an object")

        if not isinstance(answers_data, list):
            raise ValueError("'answers' must be an array")

        # ---------------- Student ----------------

        missing = self.STUDENT_FIELDS - set(student_data)

        if missing:
            raise ValueError(
                f"Student object missing fields: {sorted(missing)}"
            )

        extras = set(student_data) - self.STUDENT_FIELDS

        if extras:
            warnings.warn(
                f"Ignoring unexpected student fields: {sorted(extras)}",
                RuntimeWarning,
            )

        student = StudentInfo(
            student_name=str(student_data["student_name"]),
            gender=str(student_data["gender"]),
            school_name=str(student_data["school_name"]),
            school_udise=str(student_data["school_udise"]),
            crc_name=str(student_data["crc_name"]),
            crc_udise=str(student_data["crc_udise"]),
            block=str(student_data["block"]),
            district=str(student_data["district"]),
            grade=str(student_data["grade"]),
            meena_manch_participation=str(student_data["meena_manch_participation"]),
        )

        # ---------------- Answers ----------------

        answers = []

        for item in answers_data:

            if not isinstance(item, dict):
                raise ValueError(
                    "Every answer must be an object"
                )

            missing = self.REQUIRED - set(item)

            if missing:
                raise ValueError(
                    f"AI response is missing required fields: {sorted(missing)}"
                )

            extras = set(item) - self.REQUIRED

            if extras:
                warnings.warn(
                    f"Ignoring unexpected answer fields: {sorted(extras)}",
                    RuntimeWarning,
                )

            answers.append(
                Answer(
                    question_id=item["question_id"],
                    selected_codes=list(item["selected_codes"]),
                    answer_text=str(item["answer_text"]),
                    confidence=float(item["confidence"]),
                    review_required=bool(item["review_required"]),
                    raw_observations=str(item["raw_observations"]),
                )
            )

        return student, answers