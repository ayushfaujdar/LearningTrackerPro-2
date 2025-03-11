import logging
import random
from typing import Dict, List, Any

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

def generate_insights(data: Dict[str, Any], optimization_result: Dict[str, Any]) -> Dict[str, Any]:
    """
    Generate AI-powered insights and explanations for the optimization results.
    
    In a real implementation, this would connect to an actual AI service like Grok.
    For this prototype, we generate deterministic insights based on the optimization data.
    
    Args:
        data: Original input data
        optimization_result: Results from the optimization algorithm
    
    Returns:
        Dictionary with insights and explanations
    """
    try:
        logger.info("Generating AI insights for optimization results")
        
        # Extract key metrics from the optimization results
        budget = data['budget']
        deadline = data['deadline']
        total_cost = optimization_result['total_cost']
        budget_remaining = optimization_result['budget_remaining']
        completion_time = optimization_result['completion_time']
        time_buffer = optimization_result['time_buffer']
        risks = optimization_result['risks']
        assignments = optimization_result['assignments']
        
        # Budget efficiency
        budget_efficiency = (budget - total_cost) / budget * 100
        
        # Time efficiency
        time_efficiency = (deadline - completion_time) / deadline * 100
        
        # Risk count by severity
        high_risks = sum(1 for r in risks if r['severity'] == 'high')
        medium_risks = sum(1 for r in risks if r['severity'] == 'medium')
        
        # Skill matching average
        avg_skill_match = sum(a['skill_match'] for a in assignments) / len(assignments) if assignments else 0
        
        # Generate explanation based on the metrics
        explanation = _generate_explanation(
            budget_efficiency, 
            time_efficiency, 
            high_risks, 
            medium_risks, 
            avg_skill_match,
            total_cost,
            completion_time,
            risks
        )
        
        # Generate recommendations
        recommendations = _generate_recommendations(
            budget_efficiency,
            time_efficiency,
            high_risks,
            medium_risks,
            avg_skill_match,
            risks,
            assignments,
            data
        )
        
        return {
            'explanation': explanation,
            'recommendations': recommendations,
            'metrics': {
                'budget_efficiency': round(budget_efficiency, 1),
                'time_efficiency': round(time_efficiency, 1),
                'avg_skill_match': round(avg_skill_match, 1)
            }
        }
    
    except Exception as e:
        logger.error(f"Error generating insights: {str(e)}")
        return {
            'explanation': "Unable to generate insights due to an error.",
            'recommendations': [],
            'metrics': {}
        }

def _generate_explanation(budget_efficiency: float, time_efficiency: float,
                         high_risks: int, medium_risks: int, avg_skill_match: float,
                         total_cost: float, completion_time: float, risks: List[Dict[str, Any]]) -> str:
    """Generate a human-friendly explanation of the optimization results"""
    
    # Base explanation
    explanation = f"This optimization will cost ${total_cost:.2f} and complete in {completion_time:.1f} days. "
    
    # Budget assessment
    if budget_efficiency > 30:
        explanation += f"You have a comfortable budget buffer ({budget_efficiency:.1f}% remaining). "
    elif budget_efficiency > 10:
        explanation += f"You have a reasonable budget buffer ({budget_efficiency:.1f}% remaining). "
    else:
        explanation += f"Your budget is tight with only {budget_efficiency:.1f}% remaining. "
    
    # Time assessment
    if time_efficiency > 30:
        explanation += f"The schedule has ample buffer ({time_efficiency:.1f}% of deadline remaining). "
    elif time_efficiency > 10:
        explanation += f"The schedule has a reasonable buffer ({time_efficiency:.1f}% of deadline remaining). "
    elif time_efficiency > 0:
        explanation += f"The schedule is tight with only {time_efficiency:.1f}% buffer. "
    else:
        explanation += f"The current plan exceeds your deadline by {-time_efficiency:.1f}% of the allocated time. "
    
    # Risk assessment
    if high_risks > 0:
        explanation += f"There are {high_risks} high-severity risks that require attention. "
    if medium_risks > 0:
        explanation += f"There are {medium_risks} medium-severity risks to consider. "
    if high_risks == 0 and medium_risks == 0:
        explanation += "No significant risks were identified. "
    
    # Skill match assessment
    if avg_skill_match > 90:
        explanation += f"Developer skill matching is excellent at {avg_skill_match:.1f}%. "
    elif avg_skill_match > 75:
        explanation += f"Developer skill matching is good at {avg_skill_match:.1f}%. "
    else:
        explanation += f"Developer skill matching is suboptimal at {avg_skill_match:.1f}%. "
    
    # Add risk details if present
    if risks:
        explanation += "Key concerns: " + "; ".join(r['message'] for r in risks if r['severity'] == 'high')
    
    return explanation

def _generate_recommendations(budget_efficiency: float, time_efficiency: float,
                             high_risks: int, medium_risks: int, avg_skill_match: float,
                             risks: List[Dict[str, Any]], assignments: List[Dict[str, Any]],
                             original_data: Dict[str, Any]) -> List[str]:
    """Generate actionable recommendations based on the optimization results"""
    recommendations = []
    
    # Budget recommendations
    if budget_efficiency < 10:
        recommendations.append("Consider increasing your budget by at least 15% to create a safer buffer.")
    
    # Timeline recommendations
    if time_efficiency < 10:
        recommendations.append("Add more developers or extend the deadline to reduce schedule risk.")
    
    # Skill matching recommendations
    if avg_skill_match < 80:
        recommendations.append("Look for developers with more relevant skills to improve project quality.")
    
    # Look for low skill matches
    low_skill_assignments = [a for a in assignments if a['skill_match'] < 70]
    if low_skill_assignments:
        dev_names = [a['developer'] for a in low_skill_assignments[:2]]
        recommendations.append(f"Consider replacing or training {', '.join(dev_names)} to improve skill matching.")
    
    # High-cost assignments
    expensive_assignments = sorted(assignments, key=lambda a: a['cost'], reverse=True)[:2]
    if expensive_assignments and any(a['cost'] > 1000 for a in expensive_assignments):
        project_names = [a['project'] for a in expensive_assignments]
        recommendations.append(f"Projects {', '.join(project_names)} have high costs. Consider alternative resourcing.")
    
    # Developer distribution
    dev_counts = {}
    for a in assignments:
        dev_counts[a['developer']] = dev_counts.get(a['developer'], 0) + 1
    
    overallocated_devs = [d for d, count in dev_counts.items() if count > 2]
    if overallocated_devs:
        recommendations.append(f"Developers {', '.join(overallocated_devs)} are assigned to too many projects, which may cause delays.")
    
    # Risk mitigations
    if any(r['severity'] == 'high' for r in risks):
        recommendations.append("Address high severity risks immediately to prevent project failure.")
    
    return recommendations[:5]  # Limit to top 5 recommendations
