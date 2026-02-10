import re
import io
from pdfminer.high_level import extract_text
import docx
import os

# A broad list of common professional and technical skills
SKILLS_LIST = {
    # Programming Languages
    'Python', 'JavaScript', 'Java', 'C++', 'C#', 'PHP', 'Ruby', 'Swift', 'Kotlin', 'Go', 'Rust', 'TypeScript', 'SQL', 'HTML', 'CSS',
    # Frameworks & Libraries
    'Django', 'React', 'Angular', 'Vue', 'Spring', 'Flask', 'Laravel', 'Express', 'Bootstrap', 'jQuery', 'Node.js', 'TensorFlow', 'PyTorch', 'FastAPI',
    # Backend & DevOps
    'AWS', 'Azure', 'Google Cloud', 'Docker', 'Kubernetes', 'CI/CD', 'Jenkins', 'Terraform', 'PostgreSQL', 'MySQL', 'MongoDB', 'Redis', 'Nginx',
    # Soft & Other Skills
    'Project Management', 'UI/UX Design', 'SEO', 'Data Analysis', 'Machine Learning', 'AI', 'Graphic Design', 'Excel', 'Agile', 'Scrum',
    'Marketing', 'Sales', 'Communication', 'Leadership', 'Content Writing', 'Research', 'Git', 'GitHub', 'Translation', 'Public Speaking'
}

def extract_text_from_file(file_obj):
    """Extracts text from PDF or DOCX file object."""
    file_extension = file_obj.name.split('.')[-1].lower()
    text = ""
    
    try:
        if file_extension == 'pdf':
            # Seek to start in case it was read before
            file_obj.seek(0)
            text = extract_text(file_obj)
        elif file_extension == 'docx':
            file_obj.seek(0)
            doc = docx.Document(file_obj)
            text = "\n".join([para.text for para in doc.paragraphs])
        
        # Clean up text: remove null bytes and strip whitespace
        if text:
            text = text.replace('\x00', '').strip()
            
    except Exception as e:
        import traceback
        print(f"Error extracting text from {file_obj.name}: {str(e)}")
        traceback.print_exc()
        
    return text

def parse_cv_data(text):
    """
    Parses text to find phone, location, linkedin, and github.
    Very basic regex-based extraction.
    """
    data = {
        'phone': None,
        'location': None,
        'linkedin': None,
        'github': None,
        'summary': None,
        'skills': [],
    }
    
    # Phone number regex (flexible)
    phone_pattern = r'(\+?\d{1,3}[-.\s]?)?\(?\d{3}\)?[-.\s]?\d{3}[-.\s]?\d{4}'
    phone_match = re.search(phone_pattern, text)
    if phone_match:
        data['phone'] = phone_match.group()
        
    # LinkedIn
    linkedin_pattern = r'linkedin\.com/in/[\w-]+'
    linkedin_match = re.search(linkedin_pattern, text)
    if linkedin_match:
        data['linkedin'] = "https://www." + linkedin_match.group()
        
    # GitHub
    github_pattern = r'github\.com/[\w-]+'
    github_match = re.search(github_pattern, text)
    if github_match:
        # Avoid matching generic github links if possible, but for a CV it's usually the profile
        data['github'] = "https://www." + github_match.group()

    # Location (looking for common patterns like "City, Country" or "City, State")
    # This is tricky without NLP, but let's try some common keywords
    lines = text.split('\n')
    for line in lines:
        stripped_line = line.strip()
        if not stripped_line:
            continue
            
        # Avoid lines that might be phone numbers or social links
        if any(keyword in stripped_line.lower() for keyword in ['phone', 'email', 'linkedin', 'github']):
            continue
            
        # Simple heuristic: line with comma and reasonable length
        if ',' in stripped_line and len(stripped_line) < 50:
            data['location'] = stripped_line
            break
                
    # Summary (looking for "Summary" or "Profile" header)
    # Updated regex to be more flexible with what follows the header
    summary_match = re.search(r'(?:Summary|Profile|About Me|Professional Summary)[:\s]*\n+(.*?)(?=\n+\s*\w+:|$)', text, re.IGNORECASE | re.DOTALL)
    if not summary_match:
        # Try even simpler if no newline
        summary_match = re.search(r'(?:Summary|Profile|About Me|Professional Summary)[:\s]+(.+)', text, re.IGNORECASE)

    if summary_match:
        data['summary'] = summary_match.group(1).strip()

    else:
        # Fallback: first 2-3 sentences if no header? or just the top part
        pass

    # Extract Skills
    data['skills'] = extract_skills(text)

    return data

def extract_skills(text):
    """Matches text against a predefined list of skills."""
    if not text:
        return []
        
    found_skills = []
    # Use word boundaries to avoid matching "Java" in "JavaScript"
    for skill in SKILLS_LIST:
        # Escape special characters in skill name for regex
        pattern = r'\b' + re.escape(skill) + r'\b'
        if re.search(pattern, text, re.IGNORECASE):
            found_skills.append(skill)
            
    return sorted(list(set(found_skills)))

def calculate_match_score(user_skills_str, job_skills_str):
    """
    Calculates a match score between 0 and 100 based on overlapping skills.
    Skills are stored as comma-separated strings.
    """
    if not user_skills_str or not job_skills_str:
        return 0
        
    user_skills = set(s.strip().lower() for s in user_skills_str.split(',') if s.strip())
    job_skills = set(s.strip().lower() for s in job_skills_str.split(',') if s.strip())
    
    if not job_skills:
        return 0
        
    matches = user_skills.intersection(job_skills)
    score = (len(matches) / len(job_skills)) * 100
    
    return round(score)

def process_cv_and_update_profile(user, cv_file):
    """
    Centralized function to process a CV file, update the CV model,
    and auto-fill the UserProfile.
    """
    from .models import CV, UserProfile
    
    # Save or update CV model
    cv, created = CV.objects.get_or_create(user=user)
    cv.resume_file = cv_file
    if not cv.title:
        cv.title = f"CV - {user.username}"
    cv.save()

    # Extract text and parse data
    try:
        text = extract_text_from_file(cv_file)
        if text:
            parsed_data = parse_cv_data(text)
            
            # Update UserProfile
            profile, created = UserProfile.objects.get_or_create(user=user)
            
            # Auto-fill profile fields if they are empty
            if not profile.phone and parsed_data.get('phone'):
                profile.phone = parsed_data['phone']
            if not profile.location and parsed_data.get('location'):
                profile.location = parsed_data['location']
            profile.save()
            
            # Update CV model specialized fields if they are empty
            if not cv.summary and parsed_data.get('summary'):
                cv.summary = parsed_data['summary']
            if not cv.linkedin and parsed_data.get('linkedin'):
                cv.linkedin = parsed_data['linkedin']
            if not cv.github and parsed_data.get('github'):
                cv.github = parsed_data['github']
            
            # Update Skills
            if parsed_data.get('skills'):
                # Combine existing skills with new ones, avoiding duplicates
                existing_skills = set(s.strip() for s in (cv.skills or "").split(',') if s.strip())
                new_skills = set(parsed_data['skills'])
                all_skills = sorted(list(existing_skills.union(new_skills)))
                cv.skills = ", ".join(all_skills)
                
            cv.save()
            
            return True, "CV uploaded and profile updated with extracted information!"
        else:
            return True, "CV uploaded successfully, but no text could be extracted for auto-fill."
    except Exception as e:
        print(f"Extraction error: {e}")
        return True, "CV uploaded successfully, but an error occurred during auto-fill extraction."
