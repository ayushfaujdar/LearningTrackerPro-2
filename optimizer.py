import numpy as np
import logging
from typing import Dict, List, Any
import math

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def run_optimization(budget: float, deadline: float, 
                     developers: List[Dict[str, Any]], 
                     projects: List[Dict[str, Any]]) -> Dict[str, Any]:
    """
    Run the quantum-inspired optimization algorithm to assign developers to projects.
    
    Args:
        budget: Total available budget in dollars
        deadline: Project deadline in days
        developers: List of developer dictionaries with name, rate, hours_per_day, skills
        projects: List of project dictionaries with name, hours, priority, dependencies
    
    Returns:
        Dictionary with optimization results including assignments, costs, and metrics
    """
    logger.info(f"Starting optimization with budget ${budget}, deadline {deadline} days")
    logger.info(f"Optimizing for {len(developers)} developers and {len(projects)} projects")
    
    try:
        # Create dependency graph and determine execution order
        ordered_projects = _resolve_dependencies(projects)
        
        # Initialize result structure
        assignments = []
        total_cost = 0
        max_days = 0
        
        # Track developer availability (remaining hours)
        dev_availability = {dev['name']: dev['hours_per_day'] * deadline for dev in developers}
        
        # Quantum-inspired assignment algorithm
        for project in ordered_projects:
            # Find the best developer for this project
            best_dev, hours_needed, cost, skill_match = _assign_best_developer(
                project, developers, dev_availability
            )
            
            # Calculate days needed for this project with the assigned developer
            days_needed = hours_needed / best_dev['hours_per_day']
            max_days = max(max_days, days_needed)
            
            # Update developer availability
            dev_availability[best_dev['name']] -= hours_needed
            
            # Update total cost
            total_cost += cost
            
            # Add to assignments
            assignments.append({
                'developer': best_dev['name'],
                'project': project['name'],
                'hours': hours_needed,
                'cost': cost,
                'skill_match': skill_match
            })
        
        # Generate risks based on budget, timeline, and skill matches
        risks = _identify_risks(assignments, budget, deadline, total_cost, max_days)
        
        # Prepare the optimization result
        result = {
            'assignments': assignments,
            'total_cost': round(total_cost, 2),
            'budget_remaining': round(budget - total_cost, 2),
            'completion_time': round(max_days, 1),
            'time_buffer': round(deadline - max_days, 1),
            'risks': risks
        }
        
        return result
    
    except Exception as e:
        logger.error(f"Optimization failed: {str(e)}")
        raise

def _resolve_dependencies(projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
    """
    Resolve project dependencies and return projects in execution order.
    
    Args:
        projects: List of project dictionaries
    
    Returns:
        Ordered list of projects respecting dependencies
    """
    # Create a copy to avoid modifying the original
    projects_copy = [p.copy() for p in projects]
    
    # Build dependency graph
    dependency_graph = {}
    for project in projects_copy:
        project_name = project['name']
        dependency_graph[project_name] = project.get('dependencies', [])
    
    # Topological sort
    visited = set()
    temp = set()
    ordered = []
    
    def visit(project_name):
        if project_name in temp:
            raise ValueError(f"Circular dependency detected involving {project_name}")
        if project_name not in visited:
            temp.add(project_name)
            for dep in dependency_graph.get(project_name, []):
                if dep:  # Skip empty dependencies
                    visit(dep)
            temp.remove(project_name)
            visited.add(project_name)
            ordered.append(project_name)
    
    # Visit each project
    for project_name in dependency_graph:
        if project_name not in visited:
            visit(project_name)
    
    # Reorder the original projects list based on the dependency order
    project_map = {p['name']: p for p in projects_copy}
    ordered_projects = [project_map[name] for name in ordered]
    
    # Sort by priority for projects without dependencies
    ordered_projects.sort(key=lambda x: -x.get('priority', 1))
    
    return ordered_projects

def _assign_best_developer(project: Dict[str, Any], 
                          developers: List[Dict[str, Any]],
                          availability: Dict[str, float]) -> tuple:
    """
    Assign the best developer to a project using quantum-inspired probability amplitudes
    
    Args:
        project: Project dictionary
        developers: List of developer dictionaries
        availability: Dict of remaining available hours for each developer
    
    Returns:
        Tuple of (best developer, hours needed, cost, skill match percentage)
    """
    project_hours = project['hours']
    project_priority = project.get('priority', 3)
    project_skills = project.get('required_skills', [])
    
    # Calculate "quantum amplitudes" for each developer
    amplitudes = []
    
    for dev in developers:
        # Skip if developer doesn't have enough availability
        if availability[dev['name']] < project_hours:
            continue
        
        # Calculate skill match
        skill_match = 100
        if project_skills and dev['skills']:
            matched_skills = set(s.lower() for s in dev['skills']) & set(s.lower() for s in project_skills)
            skill_match = int(len(matched_skills) / len(project_skills) * 100) if project_skills else 100
        
        # Calculate cost
        cost = project_hours * dev['rate']
        
        # Create a quantum-inspired amplitude based on multiple factors
        # Higher amplitude = better match
        cost_factor = 1.0 / (cost + 1)  # Lower cost = higher amplitude
        skill_factor = skill_match / 100  # Higher skill match = higher amplitude
        priority_factor = project_priority / 5  # Higher priority = favor skilled developers
        
        # Combined amplitude with quantum-inspired weighting
        amplitude = cost_factor * (skill_factor ** priority_factor)
        
        amplitudes.append((dev, amplitude, cost, skill_match))
    
    if not amplitudes:
        raise ValueError(f"No developer has enough availability for project {project['name']}")
    
    # Sort by amplitude in descending order
    amplitudes.sort(key=lambda x: x[1], reverse=True)
    
    # Return the best match
    best_dev, _, cost, skill_match = amplitudes[0]
    return best_dev, project_hours, cost, skill_match

def _identify_risks(assignments: List[Dict[str, Any]], 
                   budget: float, deadline: float, 
                   total_cost: float, completion_time: float) -> List[Dict[str, Any]]:
    """
    Identify risks in the optimization result
    
    Args:
        assignments: List of assignment dictionaries
        budget: Total budget
        deadline: Project deadline
        total_cost: Total cost of assignments
        completion_time: Estimated completion time
    
    Returns:
        List of risk dictionaries with message and severity
    """
    risks = []
    
    # Budget risk
    budget_usage = (total_cost / budget) * 100
    if budget_usage > 95:
        risks.append({
            'message': f'Budget nearly exhausted ({budget_usage:.1f}% used)',
            'severity': 'high'
        })
    elif budget_usage > 80:
        risks.append({
            'message': f'Budget usage high ({budget_usage:.1f}% used)',
            'severity': 'medium'
        })
    
    # Timeline risk
    time_buffer_percent = ((deadline - completion_time) / deadline) * 100
    if completion_time > deadline:
        risks.append({
            'message': f'Projected completion exceeds deadline by {completion_time - deadline:.1f} days',
            'severity': 'high'
        })
    elif time_buffer_percent < 10:
        risks.append({
            'message': f'Tight timeline (only {time_buffer_percent:.1f}% buffer)',
            'severity': 'medium'
        })
    
    # Skill match risks
    low_skill_matches = [a for a in assignments if a['skill_match'] < 70]
    if low_skill_matches:
        risks.append({
            'message': f'{len(low_skill_matches)} assignments have low skill matches',
            'severity': 'medium' if len(low_skill_matches) < 3 else 'high'
        })
    
    # Developer overallocation risk
    dev_project_counts = {}
    for a in assignments:
        dev_project_counts[a['developer']] = dev_project_counts.get(a['developer'], 0) + 1
    
    overallocated_devs = [d for d, count in dev_project_counts.items() if count > 2]
    if overallocated_devs:
        risks.append({
            'message': f'Developer(s) {", ".join(overallocated_devs)} assigned to too many projects',
            'severity': 'medium'
        })
    
    return risks
