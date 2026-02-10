function toggleMenu() {
    const navLinks = document.getElementById('navLinks');
    const loginBtns = document.querySelector('.login');
    navLinks.classList.toggle('active');
    loginBtns.classList.toggle('active');
}

function handleContactSubmit(e) {
    e.preventDefault();
    const name = document.getElementById('name').value;
    alert(`Thank you for your message, ${name}! We'll get back to you soon.`);
    e.target.reset();
}

function handleGoogleSignIn(response) {
    console.log('Google Sign-In Response received, sending to backend...');

    fetch('/google-login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',

        },
        body: JSON.stringify({
            credential: response.credential
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert(`Welcome ${data.user_name}! You've successfully signed in.`);
                window.location.href = data.redirect_url;
            } else {
                alert('Login failed: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error during Google Sign-In:', error);
            alert('An error occurred during Google Sign-In.');
        });
}

function parseJwt(token) {
    const base64Url = token.split('.')[1];
    const base64 = base64Url.replace(/-/g, '+').replace(/_/g, '/');
    const jsonPayload = decodeURIComponent(atob(base64).split('').map(function (c) {
        return '%' + ('00' + c.charCodeAt(0).toString(16)).slice(-2);
    }).join(''));
    return JSON.parse(jsonPayload);
}

function handleGoogleSignUpWithRole(response) {
    const selectedRole = document.getElementById('userRole').value;

    if (!selectedRole) {
        alert('Please select a role first by going back to role selection.');
        return;
    }

    console.log('Google Sign-Up with Role:', selectedRole);

    fetch('/google-login/', {
        method: 'POST',
        headers: {
            'Content-Type': 'application/json',
        },
        body: JSON.stringify({
            credential: response.credential,
            user_type: selectedRole
        })
    })
        .then(res => res.json())
        .then(data => {
            if (data.status === 'success') {
                alert(`Welcome ${data.user_name}! Your ${selectedRole} account has been created.`);
                window.location.href = data.redirect_url;
            } else {
                alert('Signup failed: ' + data.message);
            }
        })
        .catch(error => {
            console.error('Error during Google Sign-Up:', error);
            alert('An error occurred during Google Sign-Up.');
        });
}

function filterJobs() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const budgetFilter = document.getElementById('budgetFilter');
    const experienceFilter = document.getElementById('experienceFilter');

    const params = {
        keyword: searchInput?.value || '',
        category: categoryFilter?.value || '',
        budget: budgetFilter?.value || '',
        experience: experienceFilter?.value || ''
    };

    renderJobs(params);
}

function clearFilters() {
    const searchInput = document.getElementById('searchInput');
    const categoryFilter = document.getElementById('categoryFilter');
    const budgetFilter = document.getElementById('budgetFilter');
    const experienceFilter = document.getElementById('experienceFilter');

    if (searchInput) searchInput.value = '';
    if (categoryFilter) categoryFilter.value = 'all';
    if (budgetFilter) budgetFilter.value = 'all';
    if (experienceFilter) experienceFilter.value = 'all';

    filterJobs();
}

let cvData = {
    personal: {},
    experiences: [],
    education: [],
    skills: {
        technical: [],
        soft: [],
        languages: []
    },
    certifications: [],
    projects: []
};

function showCVTab(event, tabName) {
    event.preventDefault();

    const tabs = document.querySelectorAll('.cv-tab');
    tabs.forEach(tab => tab.classList.remove('active'));

    const navItems = document.querySelectorAll('.cv-nav-item');
    navItems.forEach(item => item.classList.remove('active'));

    const selectedTab = document.getElementById(tabName + 'Tab');
    if (selectedTab) {
        selectedTab.classList.add('active');
    }

    event.currentTarget.classList.add('active');
}

let experienceCounter = 0;

function addExperience() {
    experienceCounter++;
    const experienceList = document.getElementById('experienceList');

    const experienceItem = document.createElement('div');
    experienceItem.className = 'cv-item-card';
    experienceItem.id = `experience-${experienceCounter}`;
    experienceItem.innerHTML = `
        <div class="cv-item-header">
            <h4>Experience #${experienceCounter}</h4>
            <button class="cv-btn-delete" onclick="removeExperience(${experienceCounter})">
                <i class='bx bx-trash'></i>
            </button>
        </div>
        <div class="cv-form-grid">
            <div class="cv-form-group">
                <label>Job Title *</label>
                <input type="text" id="expTitle-${experienceCounter}" placeholder="e.g. Senior Developer">
            </div>
            <div class="cv-form-group">
                <label>Company *</label>
                <input type="text" id="expCompany-${experienceCounter}" placeholder="e.g. Tech Corp">
            </div>
            <div class="cv-form-group">
                <label>Start Date *</label>
                <input type="month" id="expStartDate-${experienceCounter}">
            </div>
            <div class="cv-form-group">
                <label>End Date</label>
                <input type="month" id="expEndDate-${experienceCounter}">
                <div class="cv-checkbox">
                    <input type="checkbox" id="expCurrent-${experienceCounter}" onchange="toggleEndDate(${experienceCounter}, 'exp')">
                    <label for="expCurrent-${experienceCounter}">Current Position</label>
                </div>
            </div>
            <div class="cv-form-group full-width">
                <label>Location</label>
                <input type="text" id="expLocation-${experienceCounter}" placeholder="e.g. New York, NY">
            </div>
            <div class="cv-form-group full-width">
                <label>Description</label>
                <textarea id="expDescription-${experienceCounter}" rows="4" placeholder="Describe your responsibilities and achievements..."></textarea>
            </div>
        </div>
    `;

    experienceList.appendChild(experienceItem);
}

function removeExperience(id) {
    const element = document.getElementById(`experience-${id}`);
    if (element) {
        element.remove();
    }
}

function toggleEndDate(id, type) {
    const checkbox = document.getElementById(`${type}Current-${id}`);
    const endDateInput = document.getElementById(`${type}EndDate-${id}`);

    if (checkbox.checked) {
        endDateInput.value = '';
        endDateInput.disabled = true;
    } else {
        endDateInput.disabled = false;
    }
}

let educationCounter = 0;

function addEducation() {
    educationCounter++;
    const educationList = document.getElementById('educationList');

    const educationItem = document.createElement('div');
    educationItem.className = 'cv-item-card';
    educationItem.id = `education-${educationCounter}`;
    educationItem.innerHTML = `
        <div class="cv-item-header">
            <h4>Education #${educationCounter}</h4>
            <button class="cv-btn-delete" onclick="removeEducation(${educationCounter})">
                <i class='bx bx-trash'></i>
            </button>
        </div>
        <div class="cv-form-grid">
            <div class="cv-form-group">
                <label>Degree *</label>
                <input type="text" id="eduDegree-${educationCounter}" placeholder="e.g. Bachelor of Science">
            </div>
            <div class="cv-form-group">
                <label>Field of Study *</label>
                <input type="text" id="eduField-${educationCounter}" placeholder="e.g. Computer Science">
            </div>
            <div class="cv-form-group full-width">
                <label>Institution *</label>
                <input type="text" id="eduInstitution-${educationCounter}" placeholder="e.g. Stanford University">
            </div>
            <div class="cv-form-group">
                <label>Start Date</label>
                <input type="month" id="eduStartDate-${educationCounter}">
            </div>
            <div class="cv-form-group">
                <label>End Date</label>
                <input type="month" id="eduEndDate-${educationCounter}">
                <div class="cv-checkbox">
                    <input type="checkbox" id="eduCurrent-${educationCounter}" onchange="toggleEndDate(${educationCounter}, 'edu')">
                    <label for="eduCurrent-${educationCounter}">Currently Studying</label>
                </div>
            </div>
            <div class="cv-form-group">
                <label>GPA (Optional)</label>
                <input type="text" id="eduGPA-${educationCounter}" placeholder="e.g. 3.8/4.0">
            </div>
            <div class="cv-form-group">
                <label>Location</label>
                <input type="text" id="eduLocation-${educationCounter}" placeholder="e.g. Stanford, CA">
            </div>
        </div>
    `;

    educationList.appendChild(educationItem);
}

function removeEducation(id) {
    const element = document.getElementById(`education-${id}`);
    if (element) {
        element.remove();
    }
}

function addSkill(type) {
    const inputId = type === 'technical' ? 'technicalSkillInput' :
        type === 'soft' ? 'softSkillInput' : 'languageInput';
    const listId = type === 'technical' ? 'technicalSkillsList' :
        type === 'soft' ? 'softSkillsList' : 'languagesList';

    const input = document.getElementById(inputId);
    if (!input) return;

    const skillValue = input.value.trim();

    if (skillValue === '') return;

    const skillsList = document.getElementById(listId);
    const skillTag = document.createElement('span');
    skillTag.className = 'cv-skill-tag';
    skillTag.innerHTML = `
        ${skillValue}
        <i class='bx bx-x' onclick="this.parentElement.remove()"></i>
    `;

    skillsList.appendChild(skillTag);
    input.value = '';
}

let certificationCounter = 0;

function addCertification() {
    certificationCounter++;
    const certificationList = document.getElementById('certificationList');

    const certItem = document.createElement('div');
    certItem.className = 'cv-item-card';
    certItem.id = `certification-${certificationCounter}`;
    certItem.innerHTML = `
        <div class="cv-item-header">
            <h4>Certification #${certificationCounter}</h4>
            <button class="cv-btn-delete" onclick="removeCertification(${certificationCounter})">
                <i class='bx bx-trash'></i>
            </button>
        </div>
        <div class="cv-form-grid">
            <div class="cv-form-group">
                <label>Certification Name *</label>
                <input type="text" id="certName-${certificationCounter}" placeholder="e.g. AWS Certified Solutions Architect">
            </div>
            <div class="cv-form-group">
                <label>Issuing Organization *</label>
                <input type="text" id="certOrg-${certificationCounter}" placeholder="e.g. Amazon Web Services">
            </div>
            <div class="cv-form-group">
                <label>Issue Date</label>
                <input type="month" id="certIssueDate-${certificationCounter}">
            </div>
            <div class="cv-form-group">
                <label>Expiration Date</label>
                <input type="month" id="certExpDate-${certificationCounter}">
            </div>
            <div class="cv-form-group full-width">
                <label>Credential ID</label>
                <input type="text" id="certID-${certificationCounter}" placeholder="e.g. ABC123XYZ">
            </div>
        </div>
    `;

    certificationList.appendChild(certItem);
}


function removeCertification(id) {
    const element = document.getElementById(`certification-${id}`);
    if (element) {
        element.remove();
    }
}

function toggleTheme() {
    document.body.classList.toggle('dark-mode');
    const isDark = document.body.classList.contains('dark-mode');
    localStorage.setItem('theme', isDark ? 'dark' : 'light');
    updateThemeIcon(isDark);
}

function updateThemeIcon(isDark) {
    const icon = document.querySelector('#themeToggle i');
    if (icon) {
        if (isDark) {
            icon.classList.replace('bx-moon', 'bx-sun');
        } else {
            icon.classList.replace('bx-sun', 'bx-moon');
        }
    }
}

document.addEventListener('DOMContentLoaded', () => {
    const savedTheme = localStorage.getItem('theme');
    if (savedTheme === 'dark') {
        document.body.classList.add('dark-mode');
        updateThemeIcon(true);
    }
});

function openApplicationModal(jobTitle) {
    const modal = document.getElementById('applicationModal');
    if (jobTitle) {
        modal.querySelector('h3').textContent = `Apply for ${jobTitle}`;
    }
    modal.classList.add('active');
}

function closeApplicationModal() {
    document.getElementById('applicationModal').classList.remove('active');
}

function handleApplicationSubmit(e) {
    e.preventDefault();

    const btn = e.target.querySelector('button[type="submit"]');
    const originalText = btn.textContent;
    btn.textContent = 'Sending...';

    setTimeout(() => {
        alert('Application Submitted Successfully!');
        btn.textContent = originalText;
        e.target.reset();
        closeApplicationModal();
    }, 1500);
}

const modal = document.getElementById('applicationModal');
if (modal) {
    modal.addEventListener('click', (e) => {
        if (e.target.id === 'applicationModal') {
            closeApplicationModal();
        }
    });
}

let projectCounter = 0;

function addProject() {
    projectCounter++;
    const projectList = document.getElementById('projectList');

    const projectItem = document.createElement('div');
    projectItem.className = 'cv-item-card';
    projectItem.id = `project-${projectCounter}`;
    projectItem.innerHTML = `
        <div class="cv-item-header">
            <h4>Project #${projectCounter}</h4>
            <button class="cv-btn-delete" onclick="removeProject(${projectCounter})">
                <i class='bx bx-trash'></i>
            </button>
        </div>
        <div class="cv-form-grid">
            <div class="cv-form-group">
                <label>Project Name *</label>
                <input type="text" id="projName-${projectCounter}" placeholder="e.g. E-commerce Platform">
            </div>
            <div class="cv-form-group">
                <label>Role</label>
                <input type="text" id="projRole-${projectCounter}" placeholder="e.g. Lead Developer">
            </div>
            <div class="cv-form-group">
                <label>Start Date</label>
                <input type="month" id="projStartDate-${projectCounter}">
            </div>
            <div class="cv-form-group">
                <label>End Date</label>
                <input type="month" id="projEndDate-${projectCounter}">
            </div>
            <div class="cv-form-group full-width">
                <label>Project URL</label>
                <input type="url" id="projURL-${projectCounter}" placeholder="https://project-demo.com">
            </div>
            <div class="cv-form-group full-width">
                <label>Description</label>
                <textarea id="projDescription-${projectCounter}" rows="4" placeholder="Describe the project, technologies used, and your contributions..."></textarea>
            </div>
        </div>
    `;

    projectList.appendChild(projectItem);
}

function removeProject(id) {
    const element = document.getElementById(`project-${id}`);
    if (element) {
        element.remove();
    }
}

function toggleCVPreview() {
    const editMode = document.getElementById('cvEditMode');
    const previewMode = document.getElementById('cvPreviewMode');
    const previewBtn = document.getElementById('previewBtnText');

    if (!editMode || !previewMode || !previewBtn) return;

    if (editMode.style.display === 'none') {
        editMode.style.display = 'grid';
        previewMode.style.display = 'none';
        previewBtn.textContent = 'Preview';
    } else {
        generatePreview();
        editMode.style.display = 'none';
        previewMode.style.display = 'block';
        previewBtn.textContent = 'Edit';
    }
}

function generatePreview() {
    const previewContent = document.getElementById('cvPreviewContent');
    if (!previewContent) return;

    const firstName = document.getElementById('cvFirstName')?.value || '';
    const lastName = document.getElementById('cvLastName')?.value || '';
    const title = document.getElementById('cvTitle')?.value || '';
    const email = document.getElementById('cvEmail')?.value || '';
    const phone = document.getElementById('cvPhone')?.value || '';
    const location = document.getElementById('cvLocation')?.value || '';
    const website = document.getElementById('cvWebsite')?.value || '';
    const linkedin = document.getElementById('cvLinkedin')?.value || '';
    const github = document.getElementById('cvGithub')?.value || '';
    const summary = document.getElementById('cvSummary')?.value || '';

    let html = `
        <div class="cv-preview-header">
            <h1>${firstName} ${lastName}</h1>
            <h2>${title}</h2>
            <div class="cv-preview-contact">
                ${email ? `<span><i class='bx bx-envelope'></i>${email}</span>` : ''}
                ${phone ? `<span><i class='bx bx-phone'></i>${phone}</span>` : ''}
                ${location ? `<span><i class='bx bx-map'></i>${location}</span>` : ''}
            </div>
            <div class="cv-preview-links">
                ${website ? `<a href="${website}" target="_blank"><i class='bx bx-globe'></i>Website</a>` : ''}
                ${linkedin ? `<a href="${linkedin}" target="_blank"><i class='bx bxl-linkedin'></i>LinkedIn</a>` : ''}
                ${github ? `<a href="${github}" target="_blank"><i class='bx bxl-github'></i>GitHub</a>` : ''}
            </div>
        </div>
    `;

    if (summary) {
        html += `
            <div class="cv-preview-section">
                <h3>Professional Summary</h3>
                <p>${summary}</p>
            </div>
        `;
    }

    const expHTML = generateExperiencePreview();
    if (expHTML) {
        html += `
            <div class="cv-preview-section">
                <h3>Work Experience</h3>
                ${expHTML}
            </div>
        `;
    }

    const eduHTML = generateEducationPreview();
    if (eduHTML) {
        html += `
            <div class="cv-preview-section">
                <h3>Education</h3>
                ${eduHTML}
            </div>
        `;
    }

    const skillsHTML = generateSkillsPreview();
    if (skillsHTML) {
        html += `
            <div class="cv-preview-section">
                <h3>Skills</h3>
                ${skillsHTML}
            </div>
        `;
    }

    const certHTML = generateCertificationsPreview();
    if (certHTML) {
        html += `
            <div class="cv-preview-section">
                <h3>Certifications</h3>
                ${certHTML}
            </div>
        `;
    }

    const projHTML = generateProjectsPreview();
    if (projHTML) {
        html += `
            <div class="cv-preview-section">
                <h3>Projects</h3>
                ${projHTML}
            </div>
        `;
    }

    previewContent.innerHTML = html;
}

function generateExperiencePreview() {
    let html = '';
    for (let i = 1; i <= experienceCounter; i++) {
        const element = document.getElementById(`experience-${i}`);
        if (!element) continue;

        const title = document.getElementById(`expTitle-${i}`)?.value || '';
        const company = document.getElementById(`expCompany-${i}`)?.value || '';
        const startDate = document.getElementById(`expStartDate-${i}`)?.value || '';
        const endDate = document.getElementById(`expEndDate-${i}`)?.value || '';
        const isCurrent = document.getElementById(`expCurrent-${i}`)?.checked || false;
        const location = document.getElementById(`expLocation-${i}`)?.value || '';
        const description = document.getElementById(`expDescription-${i}`)?.value || '';

        if (title || company) {
            html += `
                <div class="cv-preview-item">
                    <div class="cv-preview-item-header">
                        <div>
                            <h4>${title}</h4>
                            <p class="cv-preview-company">${company}${location ? ` • ${location}` : ''}</p>
                        </div>
                        <span class="cv-preview-date">${formatDate(startDate)} - ${isCurrent ? 'Present' : formatDate(endDate)}</span>
                    </div>
                    ${description ? `<p class="cv-preview-description">${description}</p>` : ''}
                </div>
            `;
        }
    }
    return html;
}

function generateEducationPreview() {
    let html = '';
    for (let i = 1; i <= educationCounter; i++) {
        const element = document.getElementById(`education-${i}`);
        if (!element) continue;

        const degree = document.getElementById(`eduDegree-${i}`)?.value || '';
        const field = document.getElementById(`eduField-${i}`)?.value || '';
        const institution = document.getElementById(`eduInstitution-${i}`)?.value || '';
        const startDate = document.getElementById(`eduStartDate-${i}`)?.value || '';
        const endDate = document.getElementById(`eduEndDate-${i}`)?.value || '';
        const isCurrent = document.getElementById(`eduCurrent-${i}`)?.checked || false;
        const gpa = document.getElementById(`eduGPA-${i}`)?.value || '';
        const location = document.getElementById(`eduLocation-${i}`)?.value || '';

        if (degree || institution) {
            html += `
                <div class="cv-preview-item">
                    <div class="cv-preview-item-header">
                        <div>
                            <h4>${degree}${field ? ` in ${field}` : ''}</h4>
                            <p class="cv-preview-company">${institution}${location ? ` • ${location}` : ''}</p>
                            ${gpa ? `<p class="cv-preview-gpa">GPA: ${gpa}</p>` : ''}
                        </div>
                        <span class="cv-preview-date">${formatDate(startDate)} - ${isCurrent ? 'Present' : formatDate(endDate)}</span>
                    </div>
                </div>
            `;
        }
    }
    return html;
}

function generateSkillsPreview() {
    let html = '';

    const technicalSkillsEl = document.getElementById('technicalSkillsList');
    const softSkillsEl = document.getElementById('softSkillsList');
    const languagesEl = document.getElementById('languagesList');

    const technicalSkills = technicalSkillsEl ? technicalSkillsEl.querySelectorAll('.cv-skill-tag') : [];
    const softSkills = softSkillsEl ? softSkillsEl.querySelectorAll('.cv-skill-tag') : [];
    const languages = languagesEl ? languagesEl.querySelectorAll('.cv-skill-tag') : [];

    if (technicalSkills.length > 0) {
        html += '<div class="cv-preview-skills-group"><h4>Technical Skills</h4><div class="cv-preview-skills">';
        technicalSkills.forEach(skill => {
            const text = skill.textContent.trim();
            html += `<span class="cv-preview-skill-tag">${text}</span>`;
        });
        html += '</div></div>';
    }

    if (softSkills.length > 0) {
        html += '<div class="cv-preview-skills-group"><h4>Soft Skills</h4><div class="cv-preview-skills">';
        softSkills.forEach(skill => {
            const text = skill.textContent.trim();
            html += `<span class="cv-preview-skill-tag">${text}</span>`;
        });
        html += '</div></div>';
    }

    if (languages.length > 0) {
        html += '<div class="cv-preview-skills-group"><h4>Languages</h4><div class="cv-preview-skills">';
        languages.forEach(lang => {
            const text = lang.textContent.trim();
            html += `<span class="cv-preview-skill-tag">${text}</span>`;
        });
        html += '</div></div>';
    }

    return html;
}

function generateCertificationsPreview() {
    let html = '';
    for (let i = 1; i <= certificationCounter; i++) {
        const element = document.getElementById(`certification-${i}`);
        if (!element) continue;

        const name = document.getElementById(`certName-${i}`)?.value || '';
        const org = document.getElementById(`certOrg-${i}`)?.value || '';
        const issueDate = document.getElementById(`certIssueDate-${i}`)?.value || '';
        const expDate = document.getElementById(`certExpDate-${i}`)?.value || '';
        const credID = document.getElementById(`certID-${i}`)?.value || '';

        if (name || org) {
            html += `
                <div class="cv-preview-item">
                    <div class="cv-preview-item-header">
                        <div>
                            <h4>${name}</h4>
                            <p class="cv-preview-company">${org}</p>
                            ${credID ? `<p class="cv-preview-credential">Credential ID: ${credID}</p>` : ''}
                        </div>
                        <span class="cv-preview-date">${formatDate(issueDate)}${expDate ? ` - ${formatDate(expDate)}` : ''}</span>
                    </div>
                </div>
            `;
        }
    }
    return html;
}

function generateProjectsPreview() {
    let html = '';
    for (let i = 1; i <= projectCounter; i++) {
        const element = document.getElementById(`project-${i}`);
        if (!element) continue;

        const name = document.getElementById(`projName-${i}`)?.value || '';
        const role = document.getElementById(`projRole-${i}`)?.value || '';
        const startDate = document.getElementById(`projStartDate-${i}`)?.value || '';
        const endDate = document.getElementById(`projEndDate-${i}`)?.value || '';
        const url = document.getElementById(`projURL-${i}`)?.value || '';
        const description = document.getElementById(`projDescription-${i}`)?.value || '';

        if (name) {
            html += `
                <div class="cv-preview-item">
                    <div class="cv-preview-item-header">
                        <div>
                            <h4>${name}</h4>
                            ${role ? `<p class="cv-preview-company">${role}</p>` : ''}
                            ${url ? `<p class="cv-preview-link"><a href="${url}" target="_blank">${url}</a></p>` : ''}
                        </div>
                        ${startDate ? `<span class="cv-preview-date">${formatDate(startDate)} - ${formatDate(endDate)}</span>` : ''}
                    </div>
                    ${description ? `<p class="cv-preview-description">${description}</p>` : ''}
                </div>
            `;
        }
    }
    return html;
}

function formatDate(dateString) {
    if (!dateString) return '';
    const date = new Date(dateString + '-01');
    return date.toLocaleDateString('en-US', { month: 'short', year: 'numeric' });
}

function saveCV() {
    collectCVData();

    localStorage.setItem('cvData', JSON.stringify(cvData));

    alert('CV saved successfully!');
}

function collectCVData() {
    cvData.personal = {
        firstName: document.getElementById('cvFirstName')?.value || '',
        lastName: document.getElementById('cvLastName')?.value || '',
        title: document.getElementById('cvTitle')?.value || '',
        email: document.getElementById('cvEmail')?.value || '',
        phone: document.getElementById('cvPhone')?.value || '',
        location: document.getElementById('cvLocation')?.value || '',
        website: document.getElementById('cvWebsite')?.value || '',
        linkedin: document.getElementById('cvLinkedin')?.value || '',
        github: document.getElementById('cvGithub')?.value || '',
        summary: document.getElementById('cvSummary')?.value || ''
    };
}

function downloadCV() {

    const editMode = document.getElementById('cvEditMode');
    if (editMode && editMode.style.display !== 'none') {
        toggleCVPreview();
    }

    generatePreview();

    const element = document.getElementById('cvPreviewContent');
    if (!element) return;

    const firstName = document.getElementById('cvFirstName')?.value || 'My';
    const lastName = document.getElementById('cvLastName')?.value || 'CV';
    const filename = `${firstName}_${lastName}_CV.pdf`;

    const opt = {
        margin: 0.5,
        filename: filename,
        image: { type: 'jpeg', quality: 0.98 },
        html2canvas: { scale: 2, useCORS: true },
        jsPDF: { unit: 'in', format: 'letter', orientation: 'portrait' }
    };

    if (typeof html2pdf !== 'undefined') {
        html2pdf().set(opt).from(element).save();
    } else {
        alert('PDF generation library not loaded. Please reload the page.');
    }
}

window.addEventListener('DOMContentLoaded', function () {
    const savedData = localStorage.getItem('cvData');
    if (savedData) {
        cvData = JSON.parse(savedData);
        loadCVData();
    }
});

function loadCVData() {
    if (cvData.personal) {
        const firstNameEl = document.getElementById('cvFirstName');
        const lastNameEl = document.getElementById('cvLastName');
        const titleEl = document.getElementById('cvTitle');
        const emailEl = document.getElementById('cvEmail');
        const phoneEl = document.getElementById('cvPhone');
        const locationEl = document.getElementById('cvLocation');
        const websiteEl = document.getElementById('cvWebsite');
        const linkedinEl = document.getElementById('cvLinkedin');
        const githubEl = document.getElementById('cvGithub');
        const summaryEl = document.getElementById('cvSummary');

        if (titleEl) titleEl.value = cvData.personal.title || '';
        if (emailEl) emailEl.value = cvData.personal.email || '';
        if (phoneEl) phoneEl.value = cvData.personal.phone || '';
        if (locationEl) locationEl.value = cvData.personal.location || '';
        if (websiteEl) websiteEl.value = cvData.personal.website || '';
        if (linkedinEl) linkedinEl.value = cvData.personal.linkedin || '';
        if (githubEl) githubEl.value = cvData.personal.github || '';
        if (summaryEl) summaryEl.value = cvData.personal.summary || '';
    }
}

function selectRole(role) {
    document.getElementById('roleSelection').style.display = 'none';

    document.getElementById('signupForm').style.display = 'block';

    document.getElementById('userRole').value = role;

    const roleIcon = document.getElementById('roleIcon');
    const roleText = document.getElementById('roleText');
    const companyNameGroup = document.getElementById('companyNameGroup');

    if (role === 'student') {
        roleIcon.className = 'bx bx-user';
        roleText.textContent = 'Signing up as Student';
        companyNameGroup.style.display = 'none';
        document.getElementById('company-name').removeAttribute('required');
    } else {
        roleIcon.className = 'bx bx-buildings';
        roleText.textContent = 'Signing up as Company';
        companyNameGroup.style.display = 'block';
        document.getElementById('company-name').setAttribute('required', 'required');
    }
}

function backToRoleSelection() {
    document.getElementById('roleSelection').style.display = 'block';
    document.getElementById('signupForm').style.display = 'none';
}

function handleSignupWithRole(e) {
    e.preventDefault();

    const name = document.getElementById('signup-name').value;
    const email = document.getElementById('signup-email').value;
    const password = document.getElementById('signup-password').value;
    const confirm = document.getElementById('signup-confirm').value;
    const role = document.getElementById('userRole').value;
    const companyName = document.getElementById('company-name').value;
    const termsAccepted = document.getElementById('terms').checked;

    if (password !== confirm) {
        alert('Passwords do not match!');
        return;
    }

    if (!termsAccepted) {
        alert('Please accept the Terms & Conditions');
        return;
    }

    const user = {
        name: name,
        email: email,
        role: role,
        companyName: role === 'company' ? companyName : null,
        createdAt: new Date().toISOString()
    };

    localStorage.setItem('currentUser', JSON.stringify(user));
    localStorage.setItem('isLoggedIn', 'true');

    if (role === 'student') {
        alert(`Welcome to Dominusoft, ${name}! Your student account has been created.`);
        window.location.href = '/student-dashboard/';
    } else {
        alert(`Welcome to Dominusoft, ${companyName}! Your company account has been created.`);
        window.location.href = '/company-dashboard/';
    }
}

const passwordInput = document.getElementById('signup-password');
if (passwordInput) {
    passwordInput.addEventListener('input', function () {
        const password = this.value;
        const strengthDiv = document.getElementById('passwordStrength');

        if (!strengthDiv) return;

        let strength = 0;
        if (password.length >= 8) strength++;
        if (/[a-z]/.test(password) && /[A-Z]/.test(password)) strength++;
        if (/\d/.test(password)) strength++;
        if (/[^a-zA-Z\d]/.test(password)) strength++;

        strengthDiv.className = 'password-strength';
        if (strength <= 1) {
            strengthDiv.classList.add('weak');
        } else if (strength <= 3) {
            strengthDiv.classList.add('medium');
        } else {
            strengthDiv.classList.add('strong');
        }
    });
}

function logout() {
    if (confirm('Are you sure you want to logout?')) {
        localStorage.removeItem('isLoggedIn');
        window.location.href = '/';
    }
}

function applyToJob(jobId) {
    alert(`Application submitted for job ${jobId}! The company will review your profile.`);
}

function viewApplications(jobId) {
    alert(`Viewing applications for job ${jobId}`);
}

function editJob(jobId) {
    alert(`Editing job ${jobId}`);
}

function closeApplications(jobId) {
    if (confirm('Are you sure you want to close applications for this job?')) {
        alert(`Applications closed for job ${jobId}`);
    }
}

function viewApplicantProfile(applicantId) {
    alert(`Viewing profile of applicant ${applicantId}`);
}

function acceptApplicant(applicantId) {
    if (confirm('Accept this applicant?')) {
        alert(`Applicant ${applicantId} accepted!`);
    }
}

function rejectApplicant(applicantId) {
    if (confirm('Reject this applicant?')) {
        alert(`Applicant ${applicantId} rejected.`);
    }
}

function showSection(sectionName) {
    alert(`Navigating to ${sectionName} section`);
}

function switchSearchType(type) {
    const jobsToggle = document.getElementById('jobsToggle');
    const studentsToggle = document.getElementById('studentsToggle');
    const jobsSearch = document.getElementById('jobsSearch');
    const studentsSearch = document.getElementById('studentsSearch');

    if (!jobsToggle || !studentsToggle) return;

    if (type === 'jobs') {
        jobsToggle.classList.add('active');
        studentsToggle.classList.remove('active');
        jobsSearch.style.display = 'block';
        studentsSearch.style.display = 'none';
    } else {
        studentsToggle.classList.add('active');
        jobsToggle.classList.remove('active');
        studentsSearch.style.display = 'block';
        jobsSearch.style.display = 'none';
    }
}

function toggleFilters(type) {
    const filtersPanel = document.getElementById(type + 'Filters');
    const filterIcon = document.getElementById(type + 'FilterIcon');
    const toggleBtn = event.currentTarget;

    if (filtersPanel.style.display === 'none') {
        filtersPanel.style.display = 'block';
        toggleBtn.classList.add('active');
    } else {
        filtersPanel.style.display = 'none';
        toggleBtn.classList.remove('active');
    }
}

function performJobSearch() {
    const keyword = document.getElementById('jobSearchInput')?.value || '';
    const location = document.getElementById('jobLocationInput')?.value || '';

    if (!keyword && !location) {
        alert('Please enter a job title or location');
        return;
    }

    const filters = {
        keyword: keyword,
        location: location,
        category: document.getElementById('jobCategory')?.value || '',
        experience: document.getElementById('jobExperience')?.value || '',
        type: document.getElementById('jobType')?.value || '',
        budget: document.getElementById('jobBudget')?.value || '',
        workLocation: document.getElementById('jobWorkLocation')?.value || '',
        posted: document.getElementById('jobPosted')?.value || ''
    };

    localStorage.setItem('jobSearchParams', JSON.stringify(filters));

    window.location.href = '/jobs/';
}

function performStudentSearch() {
    const keyword = document.getElementById('studentSearchInput')?.value || '';
    const location = document.getElementById('studentLocationInput')?.value || '';
    let url = '/students/?';
    if (keyword) url += 'keyword=' + encodeURIComponent(keyword) + '&';
    if (location) url += 'location=' + encodeURIComponent(location);
    window.location.href = url;
}

const filters = {
    keyword: keyword,
    location: location,
    category: document.getElementById('studentCategory')?.value || '',
    experience: document.getElementById('studentExperience')?.value || '',
    rate: document.getElementById('studentRate')?.value || '',
    availability: document.getElementById('studentAvailability')?.value || '',
    rating: document.getElementById('studentRating')?.value || '',
    success: document.getElementById('studentSuccess')?.value || ''
};

localStorage.setItem('studentSearchParams', JSON.stringify(filters));

alert(`Searching for students with:\nSkills: ${keyword}\nLocation: ${location}\n\nStudent browse page coming soon!`);

function quickJobSearch(keyword) {
    event.preventDefault();
    const searchInput = document.getElementById('jobSearchInput');
    if (searchInput) {
        searchInput.value = keyword;
        performJobSearch();
    }
}

function quickStudentSearch(keyword) {
    event.preventDefault();
    const searchInput = document.getElementById('studentSearchInput');
    if (searchInput) {
        searchInput.value = keyword;
        performStudentSearch();
    }
}

function clearJobFilters() {
    const selects = ['jobCategory', 'jobExperience', 'jobType', 'jobBudget', 'jobWorkLocation', 'jobPosted'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
}

function clearStudentFilters() {
    const selects = ['studentCategory', 'studentExperience', 'studentRate', 'studentAvailability', 'studentRating', 'studentSuccess'];
    selects.forEach(id => {
        const el = document.getElementById(id);
        if (el) el.value = '';
    });
}

function applyStudentFilters() {
    performStudentSearch();
}

function handleJobPost(e) {
    e.preventDefault();

    const job = {
        id: Date.now(),
        title: document.getElementById('jobTitle').value,
        category: document.getElementById('jobCategory').value,
        type: document.getElementById('jobType').value,
        location: document.getElementById('jobLocation').value,
        budget: document.getElementById('jobBudget').value,
        description: document.getElementById('jobDescription').value,
        requirements: document.getElementById('jobRequirements').value,
        postedAt: new Date().toISOString()
    };

    let postedJobs = JSON.parse(localStorage.getItem('postedJobs')) || [];
    postedJobs.push(job);
    localStorage.setItem('postedJobs', JSON.stringify(postedJobs));

    alert('Job Posted Successfully!');
    window.location.href = '/company-dashboard/';
}

function renderJobs(filterParams = {}) {
    const jobList = document.getElementById('jobList');
    if (!jobList) return;

    jobList.innerHTML = '';
    const postedJobs = JSON.parse(localStorage.getItem('postedJobs')) || [];

    if (postedJobs.length === 0) {

    }

    let visibleCount = 0;

    postedJobs.forEach(job => {

        if (filterParams.keyword && !job.title.toLowerCase().includes(filterParams.keyword.toLowerCase())) return;
        if (filterParams.category && filterParams.category !== 'all' && job.category !== filterParams.category) return;

        const jobCard = document.createElement('div');
        jobCard.className = 'job-card';
        jobCard.setAttribute('data-category', job.category);
        jobCard.setAttribute('data-budget', job.budget);

        jobCard.style.cssText = `
            background: #fff;
            padding: 25px;
            border-radius: 8px;
            box-shadow: 0 2px 10px rgba(0,0,0,0.05);
            border: 1px solid #eee;
            transition: transform 0.2s;
        `;

        jobCard.innerHTML = `
            <div style="display: flex; justify-content: space-between; align-items: start; margin-bottom: 15px;">
                <div>
                    <h3 style="margin: 0 0 5px 0; font-size: 20px; color: #0f2182;">${job.title}</h3>
                    <div style="color: #666; font-size: 14px;">
                        <span style="margin-right: 15px;"><i class='bx bx-building'></i> ${JSON.parse(localStorage.getItem('currentUser'))?.companyName || 'Company'}</span>
                        <span><i class='bx bx-map'></i> ${job.location}</span>
                    </div>
                </div>
                <span style="background: #e3f2fd; color: #0f2182; padding: 5px 12px; border-radius: 15px; font-size: 13px; font-weight: 500;">${job.type}</span>
            </div>

            <p class="job-description" style="color: #555; line-height: 1.6; margin-bottom: 15px;">${job.description.substring(0, 150)}...</p>

            <div style="display: flex; gap: 10px; flex-wrap: wrap; margin-bottom: 20px;">
                ${job.requirements ? job.requirements.split(',').map(req => `<span style="background: #f5f5f5; padding: 4px 10px; border-radius: 4px; font-size: 12px; color: #666;">${req.trim()}</span>`).join('') : ''}
            </div>

            <div style="display: flex; justify-content: space-between; align-items: center; border-top: 1px solid #eee; padding-top: 15px;">
                <span style="font-weight: 600; color: #333;">${job.budget}</span>
                <button onclick="applyToJob(${job.id})" style="background: #0f2182; color: white; border: none; padding: 8px 20px; border-radius: 5px; cursor: pointer;">Apply Now</button>
            </div>
        `;

        jobList.appendChild(jobCard);
        visibleCount++;
    });

    const resultsCount = document.getElementById('resultsCount');
    if (resultsCount) resultsCount.textContent = `Showing ${visibleCount} jobs`;

    const noResults = document.getElementById('noResults');
    if (noResults) noResults.style.display = visibleCount === 0 ? 'block' : 'none';
}

window.addEventListener('DOMContentLoaded', function () {

    if (window.location.pathname.includes('/jobs/')) {
        const searchParams = localStorage.getItem('jobSearchParams');
        let params = {};

        if (searchParams) {
            params = JSON.parse(searchParams);

            if (params.keyword && document.getElementById('searchInput')) {
                document.getElementById('searchInput').value = params.keyword;
            }

            if (params.category && document.getElementById('categoryFilter')) {
                document.getElementById('categoryFilter').value = params.category;
            }

            localStorage.removeItem('jobSearchParams');
        }

        renderJobs(params);
    }

    // Check for search parameter to switch tabs on index page
    const urlParams = new URLSearchParams(window.location.search);
    const searchType = urlParams.get('search');
    if (searchType === 'students' && window.location.pathname === '/' || window.location.pathname === '/index/') {
        switchSearchType('students');
    }

    const currentUser = localStorage.getItem('currentUser');
    const isLoggedIn = localStorage.getItem('isLoggedIn');

    const loginDiv = document.querySelector('.login');
    if (loginDiv && currentUser && isLoggedIn === 'true') {
        const user = JSON.parse(currentUser);
        const dashboardLink = user.role === 'company' ? '/company-dashboard/' : '/student-dashboard/';

        loginDiv.innerHTML = `
            <button class="signup" onclick="location.href='${dashboardLink}'">Dashboard</button>
            <button onclick="logout()">Logout</button>
        `;
    }

    if (currentUser && isLoggedIn === 'true') {
        const user = JSON.parse(currentUser);

        const userNameEl = document.getElementById('userName');
        const companyNameEl = document.getElementById('companyName');

        if (userNameEl) userNameEl.textContent = user.name;
        if (companyNameEl) companyNameEl.textContent = user.companyName || user.name;
    }
});

let conversations = [
    {
        id: 1,
        name: "Sarah Johnson",
        avatar: "https://ui-avatars.com/api/?name=Sarah+Johnson&background=0f2182&color=fff",
        online: true,
        lastMessage: "Thanks for your proposal! When can we...",
        time: "5m",
        unread: 2,
        messages: [
            { id: 1, sender: "received", text: "Hi! I saw your proposal for the website redesign project. Your portfolio looks impressive!", time: "10:30 AM", avatar: "https://ui-avatars.com/api/?name=Sarah+Johnson&background=0f2182&color=fff" },
            { id: 2, sender: "sent", text: "Thank you! I'd love to discuss the project in more detail. When would be a good time for a quick call?", time: "10:35 AM" },
            { id: 3, sender: "received", text: "How about tomorrow at 2 PM? We can discuss the scope and timeline.", time: "10:40 AM", avatar: "https://ui-avatars.com/api/?name=Sarah+Johnson&background=0f2182&color=fff" },
            { id: 4, sender: "received", text: "", time: "10:41 AM", avatar: "https://ui-avatars.com/api/?name=Sarah+Johnson&background=0f2182&color=fff", file: { name: "Project_Requirements.pdf", size: "2.4 MB", icon: "bxs-file-pdf" } },
            { id: 5, sender: "sent", text: "Perfect! 2 PM works great for me. I'll review the requirements document and prepare some questions.", time: "10:45 AM" },
            { id: 6, sender: "received", text: "Thanks for your proposal! When can we schedule a call to discuss? 📞", time: "11:30 AM", avatar: "https://ui-avatars.com/api/?name=Sarah+Johnson&background=0f2182&color=fff" }
        ]
    },
    {
        id: 2,
        name: "Tech Corp",
        avatar: "https://ui-avatars.com/api/?name=Tech+Corp&background=28a745&color=fff",
        online: false,
        lastMessage: "We reviewed your application and would...",
        time: "2h",
        unread: 0,
        messages: [
            { id: 1, sender: "received", text: "Hello! We reviewed your application for the Full Stack Developer position.", time: "9:00 AM", avatar: "https://ui-avatars.com/api/?name=Tech+Corp&background=28a745&color=fff" },
            { id: 2, sender: "sent", text: "Thank you for considering my application! I'm very excited about this opportunity.", time: "9:15 AM" }
        ]
    },
    {
        id: 3,
        name: "Michael Brown",
        avatar: "https://ui-avatars.com/api/?name=Michael+Brown&background=ff6b6b&color=fff",
        online: true,
        lastMessage: "Can you share your portfolio?",
        time: "1d",
        unread: 1,
        messages: [
            { id: 1, sender: "received", text: "Hi there! I came across your profile and I'm interested in your design work.", time: "Yesterday 3:00 PM", avatar: "https://ui-avatars.com/api/?name=Michael+Brown&background=ff6b6b&color=fff" },
            { id: 2, sender: "received", text: "Can you share your portfolio?", time: "Yesterday 3:05 PM", avatar: "https://ui-avatars.com/api/?name=Michael+Brown&background=ff6b6b&color=fff" }
        ]
    }
];

let currentConversationId = 1;
let typingTimeout;
let selectedFiles = [];

document.addEventListener('DOMContentLoaded', function () {
    if (window.location.pathname.includes('messages.html')) {
        loadConversation(currentConversationId);
        updateConversationList();
    }
});

function toggleNotifications() {
    const dropdown = document.getElementById('notificationDropdown');
    dropdown.classList.toggle('active');
}

function markAllAsRead() {
    const notifications = document.querySelectorAll('.notification-item.unread');
    notifications.forEach(notif => {
        notif.classList.remove('unread');
    });
    document.getElementById('notificationCount').textContent = '0';
    document.getElementById('notificationCount').style.display = 'none';
}

document.addEventListener('click', function (event) {
    const dropdown = document.getElementById('notificationDropdown');
    const notificationIcon = document.querySelector('.notification-icon');

    if (dropdown && notificationIcon && !dropdown.contains(event.target) && !notificationIcon.contains(event.target)) {
        dropdown.classList.remove('active');
    }
});

function openConversation(conversationId) {
    currentConversationId = conversationId;

    document.querySelectorAll('.conversation-item').forEach(item => {
        item.classList.remove('active');
    });

    const activeItem = document.querySelector(`[data-conversation-id="${conversationId}"]`);
    if (activeItem) {
        activeItem.classList.add('active');
        activeItem.classList.remove('unread');
        const unreadBadge = activeItem.querySelector('.unread-badge');
        if (unreadBadge) {
            unreadBadge.remove();
        }
    }

    loadConversation(conversationId);
}

function loadConversation(conversationId) {
    const conversation = conversations.find(c => c.id === conversationId);
    if (!conversation) return;

    document.getElementById('chatAvatar').src = conversation.avatar;
    document.getElementById('chatUserName').textContent = conversation.name;
    document.getElementById('chatUserStatus').textContent = conversation.online ? 'Active now' : 'Offline';

    const onlineStatus = document.getElementById('chatOnlineStatus');
    if (conversation.online) {
        onlineStatus.classList.add('online');
    } else {
        onlineStatus.classList.remove('online');
    }

    const chatMessages = document.getElementById('chatMessages');
    chatMessages.innerHTML = `
        <div class="chat-date-divider">
            <span>Today</span>
        </div>
    `;

    conversation.messages.forEach(message => {
        const messageElement = createMessageElement(message);
        chatMessages.appendChild(messageElement);
    });

    const typingIndicator = document.createElement('div');
    typingIndicator.className = 'typing-indicator';
    typingIndicator.id = 'typingIndicator';
    typingIndicator.style.display = 'none';
    typingIndicator.innerHTML = `
        <div class="message-avatar">
            <img src="${conversation.avatar}" alt="${conversation.name}">
        </div>
        <div class="typing-dots">
            <span></span>
            <span></span>
            <span></span>
        </div>
    `;
    chatMessages.appendChild(typingIndicator);

    scrollToBottom();
}

function createMessageElement(message) {
    const messageDiv = document.createElement('div');
    messageDiv.className = `message ${message.sender}`;

    let content = '';

    if (message.sender === 'received') {
        content += `
            <div class="message-avatar">
                <img src="${message.avatar}" alt="Avatar">
            </div>
        `;
    }

    content += '<div class="message-content">';

    if (message.file) {
        content += `
            <div class="message-bubble file-message">
                <div class="file-attachment">
                    <i class='bx ${message.file.icon}'></i>
                    <div class="file-info">
                        <span class="file-name">${message.file.name}</span>
                        <span class="file-size">${message.file.size}</span>
                    </div>
                    <button class="file-download-btn" onclick="downloadFile('${message.file.name}')">
                        <i class='bx bx-download'></i>
                    </button>
                </div>
            </div>
        `;
    } else {
        content += `
            <div class="message-bubble">
                <p>${escapeHtml(message.text)}</p>
            </div>
        `;
    }

    content += `<span class="message-time">${message.time}</span>`;
    content += '</div>';

    messageDiv.innerHTML = content;
    return messageDiv;
}

function sendMessage() {
    const input = document.getElementById('messageInput');
    const message = input.value.trim();

    if (!message && selectedFiles.length === 0) return;

    const conversation = conversations.find(c => c.id === currentConversationId);
    if (!conversation) return;

    const currentTime = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

    if (message) {
        const newMessage = {
            id: conversation.messages.length + 1,
            sender: "sent",
            text: message,
            time: currentTime
        };

        conversation.messages.push(newMessage);

        const chatMessages = document.getElementById('chatMessages');
        const typingIndicator = document.getElementById('typingIndicator');
        const messageElement = createMessageElement(newMessage);
        chatMessages.insertBefore(messageElement, typingIndicator);

        input.value = '';
        input.style.height = 'auto';
    }

    if (selectedFiles.length > 0) {
        selectedFiles.forEach(file => {
            const fileMessage = {
                id: conversation.messages.length + 1,
                sender: "sent",
                text: "",
                time: currentTime,
                file: {
                    name: file.name,
                    size: formatFileSize(file.size),
                    icon: getFileIcon(file.name)
                }
            };

            conversation.messages.push(fileMessage);

            const chatMessages = document.getElementById('chatMessages');
            const typingIndicator = document.getElementById('typingIndicator');
            const messageElement = createMessageElement(fileMessage);
            chatMessages.insertBefore(messageElement, typingIndicator);
        });

        clearSelectedFiles();
    }

    scrollToBottom();

    setTimeout(() => {
        simulateTyping();
    }, 2000);
}

function simulateTyping() {
    const typingIndicator = document.getElementById('typingIndicator');
    typingIndicator.style.display = 'flex';
    scrollToBottom();

    setTimeout(() => {
        typingIndicator.style.display = 'none';
        receiveMessage("Thanks! I'll send you the meeting link shortly.");
    }, 2000);
}

function receiveMessage(text) {
    const conversation = conversations.find(c => c.id === currentConversationId);
    if (!conversation) return;

    const currentTime = new Date().toLocaleTimeString('en-US', { hour: 'numeric', minute: '2-digit' });

    const newMessage = {
        id: conversation.messages.length + 1,
        sender: "received",
        text: text,
        time: currentTime,
        avatar: conversation.avatar
    };

    conversation.messages.push(newMessage);

    const chatMessages = document.getElementById('chatMessages');
    const typingIndicator = document.getElementById('typingIndicator');
    const messageElement = createMessageElement(newMessage);
    chatMessages.insertBefore(messageElement, typingIndicator);

    scrollToBottom();
}

function handleTyping() {

    clearTimeout(typingTimeout);

    typingTimeout = setTimeout(() => {

    }, 1000);
}

function autoResizeTextarea(textarea) {
    textarea.style.height = 'auto';
    textarea.style.height = Math.min(textarea.scrollHeight, 120) + 'px';
}

function scrollToBottom() {
    const chatMessages = document.getElementById('chatMessages');
    setTimeout(() => {
        chatMessages.scrollTop = chatMessages.scrollHeight;
    }, 100);
}

function handleFileSelect(event) {
    const files = Array.from(event.target.files);
    selectedFiles = selectedFiles.concat(files);
    displayFilePreview();
    event.target.value = '';
}

function displayFilePreview() {
    const previewArea = document.getElementById('filePreviewArea');
    const previewList = document.getElementById('filePreviewList');

    if (selectedFiles.length === 0) {
        previewArea.style.display = 'none';
        return;
    }

    previewArea.style.display = 'block';
    previewList.innerHTML = '';

    selectedFiles.forEach((file, index) => {
        const fileItem = document.createElement('div');
        fileItem.className = 'file-preview-item';
        fileItem.innerHTML = `
            <i class='bx ${getFileIcon(file.name)}'></i>
            <span class="file-preview-name">${file.name}</span>
            <button class="remove-file-btn" onclick="removeFile(${index})">
                <i class='bx bx-x'></i>
            </button>
        `;
        previewList.appendChild(fileItem);
    });
}

function removeFile(index) {
    selectedFiles.splice(index, 1);
    displayFilePreview();
}

function clearSelectedFiles() {
    selectedFiles = [];
    displayFilePreview();
}

function getFileIcon(filename) {
    const ext = filename.split('.').pop().toLowerCase();
    const iconMap = {
        'pdf': 'bxs-file-pdf',
        'doc': 'bxs-file-doc',
        'docx': 'bxs-file-doc',
        'xls': 'bxs-file',
        'xlsx': 'bxs-file',
        'ppt': 'bxs-file',
        'pptx': 'bxs-file',
        'jpg': 'bxs-image',
        'jpeg': 'bxs-image',
        'png': 'bxs-image',
        'gif': 'bxs-image',
        'zip': 'bxs-file-archive',
        'rar': 'bxs-file-archive'
    };
    return iconMap[ext] || 'bxs-file';
}

function formatFileSize(bytes) {
    if (bytes === 0) return '0 Bytes';
    const k = 1024;
    const sizes = ['Bytes', 'KB', 'MB', 'GB'];
    const i = Math.floor(Math.log(bytes) / Math.log(k));
    return Math.round(bytes / Math.pow(k, i) * 100) / 100 + ' ' + sizes[i];
}

function downloadFile(filename) {
    alert(`Downloading ${filename}...`);

}

function toggleChatInfo() {
    const sidebar = document.getElementById('chatInfoSidebar');
    sidebar.classList.toggle('active');
}

function archiveConversation() {
    if (confirm('Archive this conversation?')) {
        alert('Conversation archived successfully!');

    }
}

function blockUser() {
    if (confirm('Are you sure you want to block this user?')) {
        alert('User blocked successfully!');

    }
}

function deleteConversation() {
    if (confirm('Are you sure you want to delete this conversation? This cannot be undone.')) {
        alert('Conversation deleted!');

    }
}

function muteConversation() {
    alert('Notifications muted for this conversation');

}

function searchMessages() {
    const searchInput = document.getElementById('messageSearchInput').value.toLowerCase();
    const conversationItems = document.querySelectorAll('.conversation-item');

    conversationItems.forEach(item => {
        const name = item.querySelector('h4').textContent.toLowerCase();
        const preview = item.querySelector('.conversation-preview').textContent.toLowerCase();

        if (name.includes(searchInput) || preview.includes(searchInput)) {
            item.style.display = 'flex';
        } else {
            item.style.display = 'none';
        }
    });
}

function filterMessages(filter) {

    document.querySelectorAll('.filter-tab').forEach(tab => {
        tab.classList.remove('active');
    });
    event.target.classList.add('active');

    const conversationItems = document.querySelectorAll('.conversation-item');

    conversationItems.forEach(item => {
        switch (filter) {
            case 'all':
                item.style.display = 'flex';
                break;
            case 'unread':
                if (item.classList.contains('unread')) {
                    item.style.display = 'flex';
                } else {
                    item.style.display = 'none';
                }
                break;
            case 'archived':

                item.style.display = 'none';
                break;
        }
    });
}

function openNewMessage() {
    const modal = document.getElementById('newMessageModal');
    modal.classList.add('active');
}

function closeNewMessage() {
    const modal = document.getElementById('newMessageModal');
    modal.classList.remove('active');

    document.getElementById('newMessageRecipient').value = '';
    document.getElementById('newMessageSubject').value = '';
    document.getElementById('newMessageContent').value = '';
}

function sendNewMessage() {
    const recipient = document.getElementById('newMessageRecipient').value;
    const subject = document.getElementById('newMessageSubject').value;
    const content = document.getElementById('newMessageContent').value;

    if (!recipient || !content) {
        alert('Please fill in all required fields');
        return;
    }

    alert(`Message sent to ${recipient}!`);
    closeNewMessage();

}

function searchUsers(query) {
    if (!query) {
        document.getElementById('userSuggestions').classList.remove('active');
        return;
    }

    const users = [
        { name: 'John Doe', role: 'Frontend Developer' },
        { name: 'Jane Smith', role: 'UI/UX Designer' },
        { name: 'Mike Johnson', role: 'Product Manager' }
    ];

    const suggestions = document.getElementById('userSuggestions');
    suggestions.innerHTML = '';

    const filtered = users.filter(user =>
        user.name.toLowerCase().includes(query.toLowerCase())
    );

    if (filtered.length > 0) {
        suggestions.classList.add('active');
        filtered.forEach(user => {
            const item = document.createElement('div');
            item.className = 'user-suggestion-item';
            item.innerHTML = `
                <img src="https://ui-avatars.com/api/?name=${user.name.replace(' ', '+')}" alt="${user.name}">
                <div>
                    <div style="font-weight: 500;">${user.name}</div>
                    <div style="font-size: 12px; color: #666;">${user.role}</div>
                </div>
            `;
            item.onclick = () => selectUser(user.name);
            suggestions.appendChild(item);
        });
    } else {
        suggestions.classList.remove('active');
    }
}

function selectUser(name) {
    document.getElementById('newMessageRecipient').value = name;
    document.getElementById('userSuggestions').classList.remove('active');
}

function updateConversationList() {
    const conversationList = document.getElementById('conversationList');
    if (!conversationList) return;

    conversationList.innerHTML = '';

    conversations.forEach(conv => {
        const item = document.createElement('div');
        item.className = `conversation-item ${conv.id === currentConversationId ? 'active' : ''} ${conv.unread > 0 ? 'unread' : ''}`;
        item.setAttribute('data-conversation-id', conv.id);
        item.onclick = () => openConversation(conv.id);

        item.innerHTML = `
            <div class="conversation-avatar">
                <img src="${conv.avatar}" alt="${conv.name}">
                <span class="online-status ${conv.online ? 'online' : ''}"></span>
            </div>
            <div class="conversation-info">
                <div class="conversation-header">
                    <h4>${conv.name}</h4>
                    <span class="conversation-time">${conv.time}</span>
                </div>
                <p class="conversation-preview">${conv.lastMessage}</p>
                ${conv.unread > 0 ? `<span class="unread-badge">${conv.unread}</span>` : ''}
            </div>
        `;

        conversationList.appendChild(item);
    });
}

function escapeHtml(text) {
    const div = document.createElement('div');
    div.textContent = text;
    return div.innerHTML;
}

function toggleEmojiPicker() {
    alert('Emoji picker feature coming soon! 😊');

}

document.addEventListener('DOMContentLoaded', function () {
    const messageInput = document.getElementById('messageInput');
    if (messageInput) {
        messageInput.addEventListener('keydown', function (e) {
            if (e.key === 'Enter' && !e.shiftKey) {
                e.preventDefault();
                sendMessage();
            }
        });
    }
});

window.addEventListener('click', function (event) {
    const modal = document.getElementById('newMessageModal');
    if (event.target === modal) {
        closeNewMessage();
    }
});

document.addEventListener('DOMContentLoaded', function () {
    const cvRadios = document.querySelectorAll('input[name="cv_source"]');
    if (cvRadios.length > 0) {
        cvRadios.forEach(radio => {
            radio.addEventListener('change', function () {
                const uploadGroup = document.getElementById('cv-upload-group');
                if (uploadGroup) {
                    if (this.value === 'upload') {
                        uploadGroup.classList.remove('d-none');
                        const resumeFile = document.getElementById('resumeFile');
                        if (resumeFile) resumeFile.required = true;
                    } else {
                        uploadGroup.classList.add('d-none');
                        const resumeFile = document.getElementById('resumeFile');
                        if (resumeFile) resumeFile.required = false;
                    }
                }
            });
        });
    }
});

document.addEventListener('DOMContentLoaded', () => {
    const cvSourceRadios = document.querySelectorAll('input[name="cv_source"]');
    if (cvSourceRadios.length > 0) {
        cvSourceRadios.forEach(radio => {
            radio.addEventListener('change', (e) => {
                const uploadContainer = document.getElementById('upload-container');
                if (uploadContainer) {
                    if (e.target.value === 'upload') {
                        uploadContainer.classList.remove('display-none');
                    } else {
                        uploadContainer.classList.add('display-none');
                    }
                }
            });
        });
    }

    const uploadBox = document.getElementById('upload-container');
    const fileInput = document.getElementById('resumeFile');
    if (uploadBox && fileInput) {
        fileInput.addEventListener('change', () => {
            if (fileInput.files.length > 0) {
                uploadBox.style.borderColor = '#0f2182';
                uploadBox.style.background = '#f0f4ff';
            }
        });
    }
});

function openProjectModal() {
    const modal = document.getElementById('projectModal');
    if (modal) {
        modal.classList.add('active');
    }
}

function closeProjectModal() {
    const modal = document.getElementById('projectModal');
    if (modal) {
        modal.classList.remove('active');
    }
}

function deleteAccount() {
    if (confirm('Are you sure you want to delete your account? This action cannot be undone.')) {
        alert('Account deletion feature coming soon!');
    }
}

window.addEventListener('click', function (event) {
    const projectModal = document.getElementById('projectModal');
    const applicationModal = document.getElementById('applicationModal');
    const newMessageModal = document.getElementById('newMessageModal');

    if (event.target === projectModal) {
        closeProjectModal();
    }
    if (event.target === applicationModal) {
        closeApplicationModal();
    }
    if (event.target === newMessageModal) {
        closeNewMessage();
    }
});

function showProfileTab(event, tabId) {
    if (event) event.preventDefault();

    document.querySelectorAll('.profile-tab').forEach(tab => {
        tab.style.display = 'none';
        tab.classList.remove('active');
    });

    const selectedTab = document.getElementById(tabId + 'Tab');
    if (selectedTab) {
        selectedTab.style.display = 'block';
        selectedTab.classList.add('active');
    }

    document.querySelectorAll('.cv-nav-item').forEach(item => {
        item.classList.remove('active');
    });

    if (event) {
        event.currentTarget.classList.add('active');
    } else {
        document.querySelectorAll('.cv-nav-item').forEach(item => {
            const onclick = item.getAttribute('onclick');
            if (onclick && onclick.includes(tabId)) {
                item.classList.add('active');
            }
        });
    }

    window.location.hash = tabId;
}

window.addEventListener('load', () => {
    if (document.querySelector('.profile-tab')) {
        const hash = window.location.hash.replace('#', '');
        if (hash) {
            showProfileTab(null, hash);
        }
    }
});
