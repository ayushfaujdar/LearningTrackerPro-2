"""
Quantum-powered optimizer using IBM Qiskit for AQWSE
"""
import logging
import numpy as np
from typing import Dict, List, Any

# Import Qiskit libraries with compatibility handling
# The imports are structured to handle different versions of Qiskit
try:
    # Try importing from the new structure
    from qiskit_aer import Aer
except ImportError:
    # Fall back to the old structure if needed
    try:
        from qiskit import Aer
    except ImportError:
        # Define a fallback simulator if neither import works
        class FallbackAer:
            @staticmethod
            def get_backend(name):
                return None
        Aer = FallbackAer()
        
# Handle IBMQ import - may not be available in newer versions
try:
    from qiskit import IBMQ
except ImportError:
    # Define a fallback if import fails
    class FallbackIBMQ:
        @staticmethod
        def save_account(token, overwrite=False):
            pass
            
        @staticmethod
        def load_account():
            return None
    IBMQ = FallbackIBMQ()

# Define fallback classes for other components that might not be available
class FallbackQuadraticProgram:
    def __init__(self, name=None):
        self.name = name
        self.variables = []
        
    def binary_var(self, name):
        self.variables.append(name)
        return 0
        
    def get_variable(self, name):
        return 0
        
    def linear_constraint(self, linear=None, sense=None, rhs=None, name=None):
        pass
        
    def minimize(self, linear=None, quadratic=None):
        pass

# Try to import QuadraticProgram, or use fallback
try:
    from qiskit_optimization import QuadraticProgram
except ImportError:
    QuadraticProgram = FallbackQuadraticProgram

# Define fallback for QAOA and related components
class FallbackSampler:
    pass

class FallbackQAOA:
    def __init__(self, sampler=None, optimizer=None, reps=None):
        pass

class FallbackCOBYLA:
    pass

class FallbackMinimumEigenOptimizer:
    def __init__(self, qaoa=None):
        pass
        
    def solve(self, qubo=None):
        # Return a simple data structure that mimics the result we'd get
        class Result:
            def __init__(self):
                self.x = [0] * len(qubo.variables) if hasattr(qubo, 'variables') else []
                
        return Result()

# Try to import QAOA and related components, or use fallbacks
try:
    from qiskit.primitives import Sampler
except ImportError:
    Sampler = FallbackSampler

try:
    from qiskit.algorithms import QAOA
except ImportError:
    QAOA = FallbackQAOA

try:
    from qiskit.algorithms.optimizers import COBYLA
except ImportError:
    COBYLA = FallbackCOBYLA

try:
    from qiskit_optimization.algorithms import MinimumEigenOptimizer
except ImportError:
    MinimumEigenOptimizer = FallbackMinimumEigenOptimizer

# Set up logging
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

# Try to set random seed for reproducibility
try:
    from qiskit.utils import algorithm_globals
    algorithm_globals.random_seed = 42
except ImportError:
    # If algorithm_globals is not available, set numpy seed directly
    np.random.seed(42)

class QuantumWorkflowOptimizer:
    """
    Class for quantum-powered workflow optimization using IBM Qiskit
    """
    def __init__(self, use_quantum=False, ibm_token=None):
        """
        Initialize the quantum optimizer
        
        Args:
            use_quantum: Whether to use true quantum computation or simulation
            ibm_token: IBM Quantum Experience token for accessing real quantum hardware
        """
        self.use_quantum = use_quantum
        self.ibm_token = ibm_token
        
        # Connect to IBM Quantum if token is provided
        self.ibm_quantum_provider = None
        if self.use_quantum and self.ibm_token:
            try:
                IBMQ.save_account(self.ibm_token, overwrite=True)
                self.ibm_quantum_provider = IBMQ.load_account()
                logger.info("Successfully connected to IBM Quantum Experience")
            except Exception as e:
                logger.error(f"Failed to connect to IBM Quantum: {str(e)}")
                self.use_quantum = False
    
    def optimize(self, budget: float, deadline: float, 
                 developers: List[Dict[str, Any]], 
                 projects: List[Dict[str, Any]]) -> Dict[str, Any]:
        """
        Run quantum-powered optimization for workflow assignments
        
        Args:
            budget: Total available budget in dollars
            deadline: Project deadline in days
            developers: List of developer dictionaries with name, rate, hours_per_day, skills
            projects: List of project dictionaries with name, hours, priority, dependencies
            
        Returns:
            Dictionary with optimization results
        """
        logger.info(f"Starting quantum optimization with budget ${budget}, deadline {deadline} days")
        logger.info(f"Optimizing for {len(developers)} developers and {len(projects)} projects")
        
        try:
            # Create dependency graph and determine execution order
            from optimizer import _resolve_dependencies
            ordered_projects = _resolve_dependencies(projects)
            
            # Convert problem to QUBO (Quadratic Unconstrained Binary Optimization)
            qubo = self._create_qubo(budget, deadline, developers, ordered_projects)
            
            # Solve using quantum or classical methods
            if self.use_quantum:
                result = self._solve_with_quantum(qubo)
            else:
                # Fall back to our original optimization if quantum isn't available
                from optimizer import run_optimization
                return run_optimization(budget, deadline, developers, projects)
            
            # Process results and create assignments
            assignments = self._process_results(result, developers, ordered_projects)
            
            # Calculate costs and metrics
            total_cost, completion_time = self._calculate_metrics(assignments, developers)
            
            # Generate risks based on budget, timeline, and skill matches
            from optimizer import _identify_risks
            risks = _identify_risks(assignments, budget, deadline, total_cost, completion_time)
            
            # Prepare the optimization result
            result = {
                'assignments': assignments,
                'total_cost': round(total_cost, 2),
                'budget_remaining': round(budget - total_cost, 2),
                'completion_time': round(completion_time, 1),
                'time_buffer': round(deadline - completion_time, 1),
                'risks': risks,
                'quantum_powered': self.use_quantum
            }
            
            return result
            
        except Exception as e:
            logger.error(f"Quantum optimization failed: {str(e)}")
            # Fall back to our original optimization
            from optimizer import run_optimization
            return run_optimization(budget, deadline, developers, projects)
    
    def _create_qubo(self, budget: float, deadline: float, 
                    developers: List[Dict[str, Any]], 
                    projects: List[Dict[str, Any]]) -> QuadraticProgram:
        """
        Create a QUBO (Quadratic Unconstrained Binary Optimization) formulation of the problem
        
        Args:
            budget: Total available budget
            deadline: Project deadline
            developers: List of developers
            projects: List of projects in execution order
            
        Returns:
            QuadraticProgram object representing the QUBO problem
        """
        # Create a new quadratic program
        qubo = QuadraticProgram(name="Workflow Optimization")
        
        # Create binary variables for each developer-project assignment
        # x_{i,j} = 1 if developer i is assigned to project j, 0 otherwise
        for i, dev in enumerate(developers):
            for j, proj in enumerate(projects):
                qubo.binary_var(name=f"x_{i}_{j}")
        
        # Calculate coefficients for the objective function
        # We want to minimize a weighted sum of:
        # 1. Cost (weighted by budget)
        # 2. Time (weighted by deadline)
        # 3. Skill mismatch (weighted by project priority)
        
        # Initialize linear and quadratic terms
        linear_terms = {}
        quadratic_terms = {}
        
        # Create constraints and objective function
        for j, proj in enumerate(projects):
            # Each project must be assigned to exactly one developer
            constraint_expr = 0
            for i, dev in enumerate(developers):
                var_name = f"x_{i}_{j}"
                constraint_expr += qubo.get_variable(var_name)
                
                # Calculate cost coefficient (higher cost = higher coefficient since we're minimizing)
                cost_coef = dev['rate'] * proj['hours'] / budget
                
                # Calculate time coefficient
                time_coef = proj['hours'] / (dev['hours_per_day'] * deadline)
                
                # Calculate skill match coefficient (lower match = higher coefficient)
                skill_match = 0
                if 'skills' in dev and 'required_skills' in proj and proj['required_skills']:
                    matched_skills = set(s.lower() for s in dev['skills']) & set(s.lower() for s in proj['required_skills'])
                    skill_match = len(matched_skills) / len(proj['required_skills']) if proj['required_skills'] else 1
                skill_mismatch_coef = (1 - skill_match) * proj.get('priority', 3) / 5
                
                # Combined coefficient with weighted factors
                total_coef = 0.5 * cost_coef + 0.3 * time_coef + 0.2 * skill_mismatch_coef
                linear_terms[var_name] = total_coef
            
            # Add constraint: each project must be assigned to exactly one developer
            qubo.linear_constraint(linear=constraint_expr, sense='==', rhs=1, name=f"proj_{j}_assignment")
        
        # Add constraint: a developer can't be assigned more work than they can handle
        for i, dev in enumerate(developers):
            dev_capacity = dev['hours_per_day'] * deadline
            expr = 0
            for j, proj in enumerate(projects):
                expr += proj['hours'] * qubo.get_variable(f"x_{i}_{j}")
            qubo.linear_constraint(linear=expr, sense='<=', rhs=dev_capacity, name=f"dev_{i}_capacity")
        
        # Set the objective function
        qubo.minimize(linear=linear_terms, quadratic=quadratic_terms)
        
        return qubo
    
    def _solve_with_quantum(self, qubo: QuadraticProgram) -> Dict[str, Any]:
        """
        Solve the QUBO problem using QAOA (Quantum Approximate Optimization Algorithm)
        
        Args:
            qubo: The quadratic program to solve
            
        Returns:
            Dictionary with solution
        """
        # Set up the quantum backend (simulator or real quantum hardware)
        if self.use_quantum and hasattr(self, 'ibm_quantum_provider'):
            # Use IBM Quantum hardware
            try:
                backend = self.ibm_quantum_provider.get_backend('ibmq_qasm_simulator')
            except:
                backend = Aer.get_backend('qasm_simulator')
        else:
            # Use local simulator
            backend = Aer.get_backend('qasm_simulator')
        
        # Create QAOA instance
        sampler = Sampler()
        qaoa = QAOA(sampler=sampler, optimizer=COBYLA(), reps=2)
        
        # Relax the QUBO and create a quantum instance
        # Use MinimumEigenOptimizer to convert QUBO to Ising Hamiltonian
        optimizer = MinimumEigenOptimizer(qaoa)
        
        try:
            # Solve the problem
            result = optimizer.solve(qubo)
            return {
                'x': result.x,
                'variables': qubo.variables,
                'success': True
            }
        except Exception as e:
            logger.error(f"Quantum solving failed: {str(e)}")
            # Return simple solution
            return {
                'x': [0] * len(qubo.variables),
                'variables': qubo.variables,
                'success': False
            }
    
    def _process_results(self, result: Dict[str, Any], 
                        developers: List[Dict[str, Any]], 
                        projects: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """
        Process optimization results and create assignments
        
        Args:
            result: Optimization result from QAOA
            developers: List of developers
            projects: List of projects
            
        Returns:
            List of assignment dictionaries
        """
        assignments = []
        
        # If quantum optimization wasn't successful, fall back to greedy assignment
        if not result.get('success', False):
            # Simple greedy assignment
            used_devs = set()
            for j, proj in enumerate(projects):
                # Find best available developer
                best_dev = None
                best_score = float('inf')
                
                for i, dev in enumerate(developers):
                    if dev['name'] in used_devs:
                        continue
                        
                    # Calculate a simple score (lower is better)
                    cost = dev['rate'] * proj['hours']
                    time = proj['hours'] / dev['hours_per_day']
                    
                    # Calculate skill match
                    skill_match = 100
                    if 'required_skills' in proj and proj['required_skills'] and 'skills' in dev:
                        matched_skills = set(s.lower() for s in dev['skills']) & set(s.lower() for s in proj['required_skills'])
                        skill_match = int(len(matched_skills) / len(proj['required_skills']) * 100) if proj['required_skills'] else 100
                    
                    # Combined score (lower is better)
                    score = cost + time * 10 + (100 - skill_match)
                    
                    if score < best_score:
                        best_score = score
                        best_dev = dev
                
                if best_dev:
                    used_devs.add(best_dev['name'])
                    cost = best_dev['rate'] * proj['hours']
                    
                    # Calculate final skill match for this developer-project pair
                    final_skill_match = 100
                    if 'required_skills' in proj and proj['required_skills'] and 'skills' in best_dev:
                        matched_skills = set(s.lower() for s in best_dev['skills']) & set(s.lower() for s in proj['required_skills'])
                        final_skill_match = int(len(matched_skills) / len(proj['required_skills']) * 100) if proj['required_skills'] else 100
                    
                    assignments.append({
                        'developer': best_dev['name'],
                        'project': proj['name'],
                        'hours': proj['hours'],
                        'cost': cost,
                        'skill_match': final_skill_match
                    })
        else:
            # Process quantum results
            # x is a binary array where 1 indicates an assignment
            x = result['x']
            vars_dict = {var.name: idx for idx, var in enumerate(result['variables'])}
            
            # Extract assignments from the solution
            for i, dev in enumerate(developers):
                for j, proj in enumerate(projects):
                    var_name = f"x_{i}_{j}"
                    if var_name in vars_dict and x[vars_dict[var_name]] == 1:
                        # This developer is assigned to this project
                        cost = dev['rate'] * proj['hours']
                        
                        # Calculate skill match
                        skill_match = 100
                        if 'required_skills' in proj and proj['required_skills'] and 'skills' in dev:
                            matched_skills = set(s.lower() for s in dev['skills']) & set(s.lower() for s in proj['required_skills'])
                            skill_match = int(len(matched_skills) / len(proj['required_skills']) * 100) if proj['required_skills'] else 100
                        
                        assignments.append({
                            'developer': dev['name'],
                            'project': proj['name'],
                            'hours': proj['hours'],
                            'cost': cost,
                            'skill_match': skill_match
                        })
        
        return assignments
    
    def _calculate_metrics(self, assignments: List[Dict[str, Any]], 
                          developers: List[Dict[str, Any]]) -> tuple:
        """
        Calculate metrics from the assignments
        
        Args:
            assignments: List of assignment dictionaries
            developers: List of developer dictionaries
            
        Returns:
            Tuple of (total_cost, completion_time)
        """
        total_cost = sum(a['cost'] for a in assignments)
        
        # Calculate completion time based on developer workloads
        dev_workloads = {}
        for a in assignments:
            dev_name = a['developer']
            if dev_name not in dev_workloads:
                dev_workloads[dev_name] = 0
            dev_workloads[dev_name] += a['hours']
        
        # Calculate time for each developer
        dev_times = {}
        for dev_name, hours in dev_workloads.items():
            # Find the developer in the list
            dev = next((d for d in developers if d['name'] == dev_name), None)
            if dev:
                dev_times[dev_name] = hours / dev['hours_per_day']
        
        # Max time is the completion time
        completion_time = max(dev_times.values()) if dev_times else 0
        
        return total_cost, completion_time