import pandas as pd
import os

# Create directory if it doesn't exist
os.makedirs('static/sample_data', exist_ok=True)

# Create metadata sheet
metadata = pd.DataFrame([
    ['Budget', 50000],
    ['Deadline', 60]
])

# Create developers sheet
developers = pd.DataFrame({
    'Name': ['John Smith', 'Maria Garcia', 'Alex Chen', 'Priya Patel', 'Carlos Rodriguez'],
    'Rate': [75, 90, 60, 100, 85],
    'Hours per day': [8, 6, 8, 4, 7],
    'Skills': [
        'Python, JavaScript, React, Database',
        'Python, Data Science, ML, API',
        'JavaScript, React, UI/UX, HTML, CSS',
        'Architecture, DevOps, Security, Cloud',
        'Backend, Database, Java, Kubernetes'
    ]
})

# Create projects sheet
projects = pd.DataFrame({
    'Name': ['Frontend Dashboard', 'API Development', 'Database Migration', 'User Authentication', 'Data Analytics', 'Cloud Deployment'],
    'Hours': [120, 80, 60, 40, 100, 70],
    'Priority': [2, 4, 3, 5, 1, 2],
    'Dependencies': ['', '', '', 'Frontend Dashboard', 'API Development', 'Database Migration'],
    'Required Skills': [
        'JavaScript, React, UI/UX',
        'Python, API',
        'Database, SQL',
        'Security, Backend',
        'Python, Data Science, ML',
        'DevOps, Cloud, Kubernetes'
    ]
})

# Create Excel writer
with pd.ExcelWriter('static/sample_data/sample_workflow.xlsx') as writer:
    metadata.to_excel(writer, sheet_name='Metadata', header=False, index=False)
    developers.to_excel(writer, sheet_name='Developers', index=False)
    projects.to_excel(writer, sheet_name='Projects', index=False)

print("Excel sample file created successfully")