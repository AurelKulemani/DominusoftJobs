import os
import django
import sys

sys.path.append(os.path.join(os.getcwd(), 'backend'))
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'domijobs.settings')
django.setup()

from jobs.utils import extract_text_from_file, parse_cv_data

def test_cv_extraction():
    cv_path = r'backend\media\resumes\My_CV_CV_1.pdf'
    if not os.path.exists(cv_path):
        print(f"File not found: {cv_path}")
        return

    with open(cv_path, 'rb') as f:
        # Mocking the file object as it would come from request.FILES
        class MockFile:
            def __init__(self, file, name):
                self.file = file
                self.name = name
            def read(self, *args, **kwargs):
                return self.file.read(*args, **kwargs)
            def seek(self, *args, **kwargs):
                return self.file.seek(*args, **kwargs)

        from pdfminer.high_level import extract_text as pdf_extract
        try:
            text = pdf_extract(cv_path)
            print("--- Direct Extraction Text Preview ---")
            print(text[:500] + "...")
        except Exception as e:
            print(f"Direct extraction error: {e}")

        mock_file = MockFile(f, 'My_CV_CV_1.pdf')
        text = extract_text_from_file(mock_file)
        print("--- Extracted Text Preview ---")
        print(text[:500] + "...")
        print("------------------------------")
        
        parsed_data = parse_cv_data(text)
        print("--- Parsed Data ---")
        for key, value in parsed_data.items():
            print(f"{key}: {value}")
        print("-------------------")

if __name__ == "__main__":
    test_cv_extraction()
