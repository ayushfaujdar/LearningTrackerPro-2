"""
File parser module for AQWSE application.
Handles import of CSV and Excel files with project and developer data.
"""

import csv
import io
import traceback
import logging
from typing import Dict, List, Any, Tuple
import os

def parse_uploaded_file(file_content: bytes, filename: str) -> Dict[str, Any]:
    """
    Parse uploaded file (CSV or Excel) and extract project and developer data.

    Args:
        file_content: Bytes of the uploaded file
        filename: Name of the uploaded file

    Returns:
        Dictionary with extracted data
    """
    try:
        # Determine file type from extension
        _, ext = os.path.splitext(filename)
        ext = ext.lower()

        logging.info(f"Attempting to parse file: {filename} with extension {ext}")

        if ext == '.csv':
            # Parse CSV file
            logging.info("Parsing as CSV file")
            return _parse_csv(file_content)
        elif ext in ['.xlsx', '.xls']:
            # Parse Excel file
            logging.info("Parsing as Excel file")
            return _parse_excel(file_content)
        else:
            # Unsupported file type
            logging.error(f"Unsupported file type: {ext}")
            return {
                'success': False,
                'error': f"Unsupported file type: {ext}"
            }

    except Exception as e:
        logging.error(f"Error parsing uploaded file: {str(e)}")
        import traceback
        logging.error(f"Traceback: {traceback.format_exc()}")
        return {
            'success': False,
            'error': f"Error parsing file: {str(e)}"
        }

def _parse_csv(file_content: bytes) -> Dict[str, Any]:
    """
    Parse CSV file content and extract data.

    Args:
        file_content: Bytes of the uploaded CSV file

    Returns:
        Dictionary with extracted data
    """
    content_str = file_content.decode('utf-8')
    csv_reader = csv.reader(io.StringIO(content_str))

    # Process the CSV content
    all_rows = list(csv_reader)

    try:
        # Extract metadata from the first rows
        budget, deadline = _extract_metadata(all_rows)

        # Find the developers and projects sections
        dev_start_idx, proj_start_idx = _find_section_indices(all_rows)

        if dev_start_idx == -1 or proj_start_idx == -1:
            return {
                "success": False,
                "error": "Could not find 'Developers' or 'Projects' sections in the CSV file."
            }

        # Extract developers data
        developers = _extract_developers(all_rows, dev_start_idx)
        if not developers:
            return {"success": False, "error": "No developers found in CSV file."}

        # Extract projects data
        projects = _extract_projects(all_rows, proj_start_idx)
        if not projects:
            return {"success": False, "error": "No projects found in CSV file."}

        return {
            "success": True,
            "budget": budget,
            "deadline": deadline,
            "developers": developers,
            "projects": projects
        }

    except Exception as e:
        logging.exception(f"CSV parsing error: {str(e)}") #Improved logging
        return {
            "success": False,
            "error": f"CSV parsing error: {str(e)}"
        }

def _parse_excel(file_content: bytes) -> Dict[str, Any]:
    """
    Parse Excel file content and extract data.

    Args:
        file_content: Bytes of the uploaded Excel file

    Returns:
        Dictionary with extracted data
    """
    try:
        import pandas as pd

        # Read Excel file
        excel_file = io.BytesIO(file_content)

        # Try to read metadata sheet first
        metadata_df = pd.read_excel(excel_file, sheet_name='Metadata', header=None)
        budget = float(metadata_df.iloc[0, 1])
        deadline = float(metadata_df.iloc[1, 1])

        # Reset file pointer
        excel_file.seek(0)

        # Read developers sheet
        dev_df = pd.read_excel(excel_file, sheet_name='Developers')
        developers = []

        for _, row in dev_df.iterrows():
            skills = row['Skills'].split(',') if isinstance(row['Skills'], str) else []
            skills = [skill.strip() for skill in skills]

            developer = {
                "name": row['Name'],
                "rate": float(row['Rate']),
                "hours_per_day": float(row['Hours per day']),
                "skills": skills
            }
            developers.append(developer)

        # Reset file pointer
        excel_file.seek(0)

        # Read projects sheet
        proj_df = pd.read_excel(excel_file, sheet_name='Projects')
        projects = []

        for _, row in proj_df.iterrows():
            dependencies = []
            if 'Dependencies' in proj_df.columns and pd.notna(row['Dependencies']):
                deps = str(row['Dependencies']).split(',')
                dependencies = [dep.strip() for dep in deps if dep.strip()]

            required_skills = []
            if 'Required Skills' in proj_df.columns and pd.notna(row['Required Skills']):
                skills = str(row['Required Skills']).split(',')
                required_skills = [skill.strip() for skill in skills if skill.strip()]

            project = {
                "name": row['Name'],
                "hours": float(row['Hours']),
                "priority": int(row['Priority']),
                "dependencies": dependencies,
                "required_skills": required_skills
            }
            projects.append(project)

        if not developers or not projects:
            return {"success": False, "error": "Excel file does not contain valid developer or project data"}

        return {
            "success": True,
            "budget": budget,
            "deadline": deadline,
            "developers": developers,
            "projects": projects
        }

    except ImportError:
        return {
            "success": False,
            "error": "Pandas library is required for Excel parsing but was not found."
        }
    except Exception as e:
        logging.exception(f"Excel parsing error: {str(e)}") #Improved logging
        return {
            "success": False,
            "error": f"Excel parsing error: {str(e)}"
        }

def _extract_metadata(rows: List[List[str]]) -> Tuple[float, float]:
    """
    Extract budget and deadline from CSV rows.

    Args:
        rows: List of CSV rows

    Returns:
        Tuple of (budget, deadline)
    """
    budget = 0.0
    deadline = 0.0

    for row in rows[:10]:  # Check first 10 rows for metadata
        if len(row) >= 2:
            if row[0].lower() == 'budget':
                try:
                    budget = float(row[1])
                    logging.info(f"Found budget: {budget}")
                except ValueError:
                    logging.warning(f"Invalid budget value in CSV: {row[1]}")
            elif row[0].lower() == 'deadline':
                try:
                    deadline = float(row[1])
                    logging.info(f"Found deadline: {deadline}")
                except ValueError:
                    logging.warning(f"Invalid deadline value in CSV: {row[1]}")

    return budget, deadline

def _find_section_indices(rows: List[List[str]]) -> Tuple[int, int]:
    """
    Find indices of 'Developers' and 'Projects' sections in CSV.

    Args:
        rows: List of CSV rows

    Returns:
        Tuple of (developers_start_index, projects_start_index)
    """
    dev_start_idx = -1
    proj_start_idx = -1

    for i, row in enumerate(rows):
        if len(row) > 0:
            # Strip whitespace and check for exact match
            if row[0].strip().lower() == 'developers':
                dev_start_idx = i
                logging.info(f"Found Developers section at row {i}")
            elif row[0].strip().lower() == 'projects':
                proj_start_idx = i
                logging.info(f"Found Projects section at row {i}")

    return dev_start_idx, proj_start_idx

def _extract_developers(rows: List[List[str]], start_idx: int) -> List[Dict[str, Any]]:
    """
    Extract developers data from CSV rows.

    Args:
        rows: List of CSV rows
        start_idx: Starting index of developers section

    Returns:
        List of developer dictionaries
    """
    developers = []
    if start_idx == -1:
        return developers #Return empty list if section not found

    headers = [h.lower() for h in rows[start_idx + 1]]

    for row in rows[start_idx + 2:]:
        if not row or not row[0] or row[0].lower() == 'projects':
            break

        developer = {}
        for i, cell in enumerate(row):
            if i < len(headers):
                header = headers[i]

                try:
                    if header == 'name':
                        developer['name'] = cell
                    elif header == 'rate':
                        developer['rate'] = float(cell) if cell else 0.0
                    elif header == 'hours per day' or header == 'hours_per_day':
                        developer['hours_per_day'] = float(cell) if cell else 0.0
                    elif header == 'skills':
                        skills = [s.strip() for s in cell.split(',') if s.strip()]
                        developer['skills'] = skills
                except ValueError as e:
                    logging.warning(f"Error processing developer data: {e}")

        if 'name' in developer and developer['name']:
            developers.append(developer)

    return developers

def _extract_projects(rows: List[List[str]], start_idx: int) -> List[Dict[str, Any]]:
    """
    Extract projects data from CSV rows.

    Args:
        rows: List of CSV rows
        start_idx: Starting index of projects section

    Returns:
        List of project dictionaries
    """
    projects = []
    if start_idx == -1:
        return projects #Return empty list if section not found

    headers = [h.lower() for h in rows[start_idx + 1]]

    for row in rows[start_idx + 2:]:
        if not row or not row[0]:
            break

        project = {}
        for i, cell in enumerate(row):
            if i < len(headers):
                header = headers[i]
                try:
                    if header == 'name':
                        project['name'] = cell
                    elif header == 'hours':
                        project['hours'] = float(cell) if cell else 0.0
                    elif header == 'priority':
                        project['priority'] = int(cell) if cell else 1
                    elif header == 'dependencies':
                        deps = [d.strip() for d in cell.split(',') if d.strip()]
                        project['dependencies'] = deps
                    elif header == 'required skills' or header == 'required_skills':
                        skills = [s.strip() for s in cell.split(',') if s.strip()]
                        project['required_skills'] = skills
                except ValueError as e:
                    logging.warning(f"Error processing project data: {e}")

        if 'name' in project and project['name']:
            projects.append(project)

    return projects