from django.test import TestCase
from .utils import extract_skills, calculate_match_score

class MatchingLogicTest(TestCase):
    def test_skill_extraction(self):
        text = "I am a Python developer with experience in Django, React, and AWS."
        skills = extract_skills(text)
        expected = ['AWS', 'Django', 'Python', 'React']
        self.assertEqual(skills, expected)

    def test_skill_extraction_case_insensitive(self):
        text = "python, dJaNgO, react"
        skills = extract_skills(text)
        expected = ['Django', 'Python', 'React']
        self.assertEqual(skills, expected)

    def test_match_calculation_perfect(self):
        user_skills = "Python, Django, React"
        job_skills = "Python, Django"
        score = calculate_match_score(user_skills, job_skills)
        self.assertEqual(score, 100)

    def test_match_calculation_partial(self):
        user_skills = "Python, AWS"
        job_skills = "Python, Django, AWS, React"
        # 2 out of 4 skills = 50%
        score = calculate_match_score(user_skills, job_skills)
        self.assertEqual(score, 50)

    def test_match_calculation_none(self):
        user_skills = "Marketing, Sales"
        job_skills = "Python, Django"
        score = calculate_match_score(user_skills, job_skills)
        self.assertEqual(score, 0)
