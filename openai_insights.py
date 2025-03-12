"""
OpenAI-powered insights generation for AQWSE workflow optimization
"""
import logging
import json
import os
from typing import Dict, List, Any

# Import OpenAI
import openai

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

class OpenAIInsightsGenerator:
    """
    Generate AI-powered insights for workflow optimization using OpenAI
    """
    def __init__(self, api_key=None):
        """
        Initialize the OpenAI insights generator
        
        Args:
            api_key: OpenAI API key for accessing GPT models
        """
        self.api_key = api_key or os.environ.get("OPENAI_API_KEY")
        self.client = None
        
        if self.api_key:
            try:
                # Validate the API key format first (basic check)
                if len(self.api_key) < 20 or not self.api_key.startswith(('sk-', 'org-')):
                    logger.warning("OpenAI API key appears to be invalid - using fallback insights")
                    return
                    
                # Initialize the OpenAI client - handle different package versions
                if hasattr(openai, 'OpenAI'):
                    # New OpenAI package structure
                    self.client = openai.OpenAI(api_key=self.api_key)
                else:
                    # Legacy OpenAI package structure
                    openai.api_key = self.api_key
                    self.client = openai
                logger.info("Successfully initialized OpenAI client")
            except Exception as e:
                logger.error(f"Failed to initialize OpenAI client: {str(e)}")
                self.client = None
    
    def generate_insights(self, data: Dict[str, Any], 
                          optimization_result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Generate AI-powered insights and explanations for the optimization results.
        
        Uses OpenAI if available, otherwise falls back to deterministic insights.
        
        Args:
            data: Original input data
            optimization_result: Results from the optimization algorithm
        
        Returns:
            Dictionary with insights and explanations
        """
        try:
            logger.info("Generating AI insights for optimization results")
            
            if self.client is None:
                logger.warning("No OpenAI client available, using fallback insights generation")
                # Use the existing insights generator as fallback
                import ai_insights
                return ai_insights.generate_insights(data, optimization_result)
            
            # Extract key metrics for AI to analyze
            budget = data['budget']
            deadline = data['deadline']
            total_cost = optimization_result['total_cost']
            budget_remaining = optimization_result['budget_remaining']
            completion_time = optimization_result['completion_time']
            time_buffer = optimization_result['time_buffer']
            risks = optimization_result['risks']
            assignments = optimization_result['assignments']
            
            # Prepare the data for the AI model
            budget_efficiency = round((budget - total_cost) / budget * 100, 1)
            time_efficiency = round((deadline - completion_time) / deadline * 100, 1)
            high_risks = sum(1 for r in risks if r['severity'] == 'high')
            medium_risks = sum(1 for r in risks if r['severity'] == 'medium')
            avg_skill_match = round(sum(a['skill_match'] for a in assignments) / len(assignments), 1) if assignments else 0
            
            # Create a prompt for the AI
            prompt = self._create_prompt(data, optimization_result, budget_efficiency, 
                                        time_efficiency, high_risks, medium_risks, 
                                        avg_skill_match)
            
            # Call OpenAI
            response = self._call_openai_api(prompt)
            
            # Parse the response
            parsed_response = self._parse_response(response)
            
            # Format the final insights
            result = {
                'explanation': parsed_response['explanation'],
                'recommendations': parsed_response['recommendations'],
                'metrics': {
                    'budget_efficiency': budget_efficiency,
                    'time_efficiency': time_efficiency,
                    'avg_skill_match': avg_skill_match
                },
                'ai_powered': True
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Error generating OpenAI insights: {str(e)}")
            # Fall back to deterministic insights
            import ai_insights
            return ai_insights.generate_insights(data, optimization_result)
    
    def _create_prompt(self, data: Dict[str, Any], 
                      optimization_result: Dict[str, Any],
                      budget_efficiency: float, time_efficiency: float,
                      high_risks: int, medium_risks: int,
                      avg_skill_match: float) -> Dict[str, str]:
        """
        Create a detailed prompt for the OpenAI API
        
        Args:
            Various metrics and data from the optimization
            
        Returns:
            Dictionary containing system and user prompts for OpenAI
        """
        # Format the data as a JSON string for AI to analyze
        data_json = json.dumps({
            'input': {
                'budget': data['budget'],
                'deadline': data['deadline'],
                'developers_count': len(data['developers']),
                'projects_count': len(data['projects'])
            },
            'results': {
                'total_cost': optimization_result['total_cost'],
                'budget_remaining': optimization_result['budget_remaining'],
                'completion_time': optimization_result['completion_time'],
                'time_buffer': optimization_result['time_buffer'],
                'budget_efficiency': budget_efficiency,
                'time_efficiency': time_efficiency,
                'high_risks': high_risks,
                'medium_risks': medium_risks,
                'avg_skill_match': avg_skill_match,
                'risks': [r['message'] for r in optimization_result['risks']],
                'quantum_powered': optimization_result.get('quantum_powered', False)
            }
        }, indent=2)
        
        # Create a system prompt for the AI
        system_prompt = (
            "You are an expert project management and resource optimization AI assistant. "
            "You are analyzing the results of a quantum-inspired workflow optimization algorithm "
            "that has assigned developers to projects based on various constraints. "
            "Provide insightful analysis, explanations, and actionable recommendations based on the data."
        )
        
        # Create a user prompt with the data
        user_prompt = (
            f"Please analyze the following optimization results and provide:\n"
            f"1. A detailed but concise explanation (2-3 paragraphs) of what the optimization achieved, "
            f"highlighting any concerns or notable insights\n"
            f"2. 3-5 specific, actionable recommendations for improvement\n\n"
            f"Here's the data:\n{data_json}"
        )
        
        return {"system": system_prompt, "user": user_prompt}
    
    def _call_openai_api(self, prompt):
        """
        Call the OpenAI API with the prepared prompt
        
        Args:
            prompt: Dictionary with system and user prompts
            
        Returns:
            The AI's response as a string
        """
        try:
            # Construct the messages
            messages = [
                {"role": "system", "content": prompt["system"]},
                {"role": "user", "content": prompt["user"]}
            ]
            
            # Call the OpenAI Chat API - handle different client versions
            try:
                if hasattr(self.client, 'chat') and hasattr(self.client.chat, 'completions'):
                    # New OpenAI client structure
                    response = self.client.chat.completions.create(
                        model="gpt-4",  # Can use gpt-3.5-turbo for faster, cheaper responses
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000
                    )
                    # Extract the response text
                    return response.choices[0].message.content
                else:
                    # Legacy OpenAI client structure
                    response = self.client.ChatCompletion.create(
                        model="gpt-4",  # Can use gpt-3.5-turbo for faster, cheaper responses
                        messages=messages,
                        temperature=0.7,
                        max_tokens=1000
                    )
                    # Extract the response text
                    return response.choices[0].message.content
            except AttributeError:
                # Final fallback for very old API versions
                response = self.client.Completion.create(
                    engine="davinci",
                    prompt=prompt["user"],
                    temperature=0.7,
                    max_tokens=1000
                )
                return response.choices[0].text
            
        except Exception as e:
            logger.error(f"OpenAI API call failed: {str(e)}")
            # Return a default response on error
            return "The AI-powered analysis could not be generated. The optimization shows a balanced approach to resource allocation."
    
    def _parse_response(self, response: str) -> Dict[str, Any]:
        """
        Parse the OpenAI response into a structured format
        
        Args:
            response: Raw text response from OpenAI
            
        Returns:
            Dictionary with explanation and recommendations
        """
        try:
            # Split the response into explanation and recommendations
            explanation = ""
            recommendations = []
            
            # Simple parsing, assuming the explanation comes first, followed by recommendations
            parts = response.split("Recommendations:")
            
            if len(parts) > 1:
                explanation = parts[0].strip()
                recommendations_text = parts[1].strip()
                
                # Extract recommendations (assuming they're in numbered or bulleted format)
                import re
                recommendation_items = re.split(r'\n\s*[\d\.\-\*]+\s*', recommendations_text)
                recommendations = [item.strip() for item in recommendation_items if item.strip()]
            else:
                # If no clear separation, use the entire response as explanation
                explanation = response.strip()
                
                # Try to extract recommendations from the text
                import re
                recommendation_matches = re.findall(r'(\d+\.\s*[^\.]+\.)', response)
                if recommendation_matches:
                    recommendations = [match.strip() for match in recommendation_matches]
            
            # Ensure we have at least one recommendation
            if not recommendations:
                recommendations = ["Consider adjusting resource allocation to optimize efficiency."]
            
            return {
                'explanation': explanation,
                'recommendations': recommendations
            }
            
        except Exception as e:
            logger.error(f"Failed to parse OpenAI response: {str(e)}")
            return {
                'explanation': "AI analysis unavailable. The optimization shows a balanced approach to resource allocation.",
                'recommendations': [
                    "Consider reviewing the highest-cost assignments for possible adjustments.",
                    "Monitor projects with tight deadlines closely.",
                    "Ensure developers have appropriate skills for their assigned projects."
                ]
            }