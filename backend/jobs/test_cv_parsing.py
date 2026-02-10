from django.test import TestCase
from .utils import parse_cv_data

class CVParsingTest(TestCase):
    def test_parse_cv_data(self):
        sample_text = """
        John Doe
        Software Engineer
        123-456-7890
        New York, NY
        Summary: Experienced software engineer with expertise in Python and Django.
        LinkedIn: linkedin.com/in/johndoe
        GitHub: github.com/johndoe
        """
        
        parsed_data = parse_cv_data(sample_text)
        print(f"\nParsed data 1: {parsed_data}")
        
        
        self.assertEqual(parsed_data['phone'], '123-456-7890')
        self.assertEqual(parsed_data['location'], 'New York, NY')
        self.assertEqual(parsed_data['linkedin'], 'https://www.linkedin.com/in/johndoe')
        self.assertEqual(parsed_data['github'], 'https://www.github.com/johndoe')
        self.assertIn('Experienced software engineer', parsed_data['summary'])

    def test_parse_cv_data_variations(self):
        sample_text = """
        Jane Smith
        Phone: +1 (555) 000-1111
        London, UK
        Profile
        Full-stack developer looking for new opportunities.
        """
        parsed_data = parse_cv_data(sample_text)
        self.assertEqual(parsed_data['phone'], '+1 (555) 000-1111')
        self.assertEqual(parsed_data['location'], 'London, UK')
        self.assertIn('Full-stack developer', parsed_data['summary'])
