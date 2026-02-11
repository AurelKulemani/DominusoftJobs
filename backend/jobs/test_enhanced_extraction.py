from django.test import TestCase
from .utils import parse_cv_data, TECHNICAL_SKILLS, SOFT_SKILLS, LANGUAGES

class EnhancedExtractionTest(TestCase):
    def test_categorized_skills_extraction(self):
        sample_text = """
        John Doe
        Python Developer
        Skills: Python, Django, JavaScript, Teamwork, Leadership, Communication, English, Spanish
        Summary: Expert in Python and Django.
        """
        
        parsed_data = parse_cv_data(sample_text)
        
        # Check Technical Skills
        self.assertIn('Python', parsed_data['technical_skills'])
        self.assertIn('Django', parsed_data['technical_skills'])
        self.assertIn('JavaScript', parsed_data['technical_skills'])
        
        # Check Soft Skills
        self.assertIn('Teamwork', parsed_data['soft_skills'])
        self.assertIn('Leadership', parsed_data['soft_skills'])
        self.assertIn('Communication', parsed_data['soft_skills'])
        
        # Check Languages
        self.assertIn('English', parsed_data['languages'])
        self.assertIn('Spanish', parsed_data['languages'])
        
    def test_summary_and_experience_extraction(self):
        sample_text = """
        John Doe
        Summary: A highly motivated developer with background in web technologies.
        Work Experience:
        Software Engineer at Google
        Mountain View, CA
        Jun 2021 - Present
        - Developing scalable web applications using Python and Django.
        - Mentoring junior developers.
        Skills: Python, Django, Leadership
        """
        
        parsed_data = parse_cv_data(sample_text)
        
        # Check Summary
        self.assertEqual(parsed_data['summary'], "A highly motivated developer with background in web technologies.")
        
        # Check Experience
        self.assertEqual(len(parsed_data['experiences']), 1)
        self.assertEqual(parsed_data['experiences'][0]['position'], "Software Engineer")
        self.assertEqual(parsed_data['experiences'][0]['company'], "Google")
        self.assertIn("Python and Django", parsed_data['experiences'][0]['description'])
        self.assertIn("Present", parsed_data['experiences'][0]['date_str'])

    def test_empty_categories(self):
        sample_text = "Just some text with no identifiable skills."
        parsed_data = parse_cv_data(sample_text)
        
        self.assertEqual(parsed_data['technical_skills'], [])
        self.assertEqual(parsed_data['soft_skills'], [])
        self.assertEqual(parsed_data['languages'], [])
