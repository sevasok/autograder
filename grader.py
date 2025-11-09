"""
Autograder - Generates test files and answer keys from solution code
"""

import ast
import os
import subprocess
import tempfile
from test_cases import TestCaseGenerator
from run_in_sandbox import run_script


class Grader:
    """Creates test files and answer keys for grading student submissions."""
    
    def __init__(self, solution_folder):
        self.solution_folder = os.path.abspath(solution_folder)
        self.generator = TestCaseGenerator()
        self.tests = []
        self.test_metadata = []
    
    def add_test(self, method_name, params, track_mutation=None):
        """
        Add a method to test.
        
        Args:
            method_name: Name of the method
            params: Dict of {param_name: [values]} or {param_name: generator_config}
            track_mutation: List of param names (arrays/dicts) to track for mutation
        """
        self.tests.append({
            "method": method_name, 
            "params": params,
            "track_mutation": track_mutation or []
        })
    
    def _get_values(self, config):
        """Get test values from config."""
        # If it's already a list, check if it contains generator configs
        if isinstance(config, list):
            values = []
            for item in config:
                if isinstance(item, dict) and "type" in item:
                    # Generate values from config
                    values.extend(self._generate_from_config(item))
                else:
                    # Add literal value
                    values.append(item)
            return values
        
        # If it's a dict with type, generate values
        if isinstance(config, dict) and "type" in config:
            return self._generate_from_config(config)
        
        return []
    
    def _generate_from_config(self, config):
        """Generate values from a config dict."""
        type_name = config.get("type", "num")
        
        if type_name == "num":
            return self.generator.generate_num(**{k: v for k, v in config.items() if k != "type"})
        elif type_name == "string":
            return self.generator.generate_string(**{k: v for k, v in config.items() if k != "type"})
        elif type_name == "bool_or_none":
            return self.generator.generate_bool_or_none(**{k: v for k, v in config.items() if k != "type"})
        elif type_name == "array":
            return self.generator.generate_array(**{k: v for k, v in config.items() if k != "type"})
        elif type_name == "dict":
            return self.generator.generate_dict(**{k: v for k, v in config.items() if k != "type"})
        
        return []
    
    def generate_test_calls(self, output=None):
        """Generate test calls file."""
        if output is None:
            output = os.path.join(self.solution_folder, "test_calls.txt")
            
        calls = []
        
        for test in self.tests:
            method = test["method"]
            params = test["params"]
            track_mutation = test.get("track_mutation", [])
            
            # Get test values for each param
            param_values = {name: self._get_values(config) for name, config in params.items()}
            
            # Create test calls
            max_tests = max(len(vals) for vals in param_values.values()) if param_values else 1
            for i in range(max_tests):
                args = []
                tracked_values = {}
                
                for name in params.keys():
                    value = param_values[name][i % len(param_values[name])]
                    args.append(repr(value))
                    # Only store values we need to track
                    if name in track_mutation:
                        tracked_values[name] = value
                
                calls.append(f"{method}({','.join(args)})")
                self.test_metadata.append(tracked_values)
        
        # Write to file, one per line
        with open(output, 'w') as f:
            f.write('\n'.join(calls))
        
        # Save metadata alongside test calls
        metadata_file = output.replace('.txt', '_metadata.txt')
        with open(metadata_file, 'w') as f:
            f.write(repr(self.test_metadata))
        
        return output
    
    def _load_test_metadata(self, test_calls):
        """Load test metadata from file."""
        metadata_file = test_calls.replace('.txt', '_metadata.txt')
        if os.path.exists(metadata_file):
            with open(metadata_file) as f:
                self.test_metadata = ast.literal_eval(f.read())
    
    def _write_test_execution(self, file, test_calls):
        """Write test execution code with mutation tracking."""
        # Load metadata if not already loaded
        if not self.test_metadata:
            self._load_test_metadata(test_calls)
        
        file.write('_results = []\n')
        with open(test_calls) as f:
            lines = [line.strip() for line in f if line.strip()]
            for idx, line in enumerate(lines):
                tracked_values = self.test_metadata[idx] if idx < len(self.test_metadata) else {}
                
                if tracked_values:
                    # Create variables for tracked params
                    for param_name, value in tracked_values.items():
                        var_name = f"_{param_name}"
                        file.write(f"{var_name} = {repr(value)}\n")
                        # Replace value with var in the call
                        line = line.replace(repr(value), var_name, 1)
                    
                    # Execute and capture return + heap
                    file.write(f"_ret = {line}\n")
                    heap = "{" + ", ".join([f"'{p}': _{p}" for p in tracked_values.keys()]) + "}"
                    file.write(f"_results.append({{'return_value': _ret, 'heap_param_values': {heap}}})\n")
                else:
                    # Just capture return value
                    file.write(f"_results.append({{'return_value': {line}, 'heap_param_values': {{}}}})\n")
        
        file.write('print(_results)\n')
    
    def generate_answer_key(self, test_calls=None, output=None):
        """Run solution with test calls and save outputs."""
        if test_calls is None:
            test_calls = os.path.join(self.solution_folder, "test_calls.txt")
        if output is None:
            output = os.path.join(self.solution_folder, "answer_key.txt")
            
        temp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        
        try:
            # Embed solution code
            solution_path = os.path.join(self.solution_folder, "solution.py")
            temp.write(open(solution_path).read())
            temp.write('\n\n')
            
            # Write test execution code
            self._write_test_execution(temp, test_calls)
            temp.close()
            
            # Run directly without sandbox
            result = subprocess.run(
                ['python', temp.name],
                capture_output=True,
                text=True,
                timeout=5
            )
            
            if result.returncode == 0:
                with open(output, 'w') as f:
                    f.write(result.stdout.strip())
                return output
            else:
                raise RuntimeError(f"Failed: {result.stderr}")
        finally:
            os.unlink(temp.name)
    
    def create_test_suite(self):
        """Generate test calls and answer key."""
        test_calls = self.generate_test_calls()
        answer_key = self.generate_answer_key(test_calls)
        return test_calls, answer_key
    
    def grade_submission(self, student_name):
        """Grade a student's submission against the answer key."""
        test_calls = os.path.join(self.solution_folder, "test_calls.txt")
        answer_key = os.path.join(self.solution_folder, "answer_key.txt")
        student_path = os.path.join(self.solution_folder, "Submissions", student_name, "main.py")
        
        temp = tempfile.NamedTemporaryFile(mode='w', suffix='.py', delete=False)
        
        try:
            # Embed student code
            temp.write(open(student_path).read())
            temp.write('\n\n')
            
            # Write test execution code
            self._write_test_execution(temp, test_calls)
            temp.close()
            
            # Run student code in sandbox
            result = run_script(temp.name, timeout=5)
            
            if not result['success']:
                return {"error": result['stderr'], "passed": 0, "total": 0, "results": []}
            
            # Parse student results and answer key
            student_results = ast.literal_eval(result['stdout'].strip())
            with open(answer_key) as f:
                expected_results = ast.literal_eval(f.read().strip())
            
            # Compare results
            total = len(expected_results)
            passed = 0
            results = []
            
            for i, (student, expected) in enumerate(zip(student_results, expected_results)):
                return_match = student['return_value'] == expected['return_value']
                heap_match = student['heap_param_values'] == expected['heap_param_values']
                match = return_match and heap_match
                
                if match:
                    passed += 1
                results.append({
                    "test": i + 1,
                    "passed": match,
                    "expected_return": expected['return_value'],
                    "got_return": student['return_value'],
                    "expected_heap": expected['heap_param_values'],
                    "got_heap": student['heap_param_values']
                })
            
            return {
                "passed": passed,
                "total": total,
                "results": results,
                "error": None
            }
            
        finally:
            os.unlink(temp.name)


# Example usage
if __name__ == "__main__":
    
    grader = Grader("Labs/testlab")
    
    # Add tests: use lists for hardcoded values or dicts for generation
    grader.add_test("fibonacci", {
        "n": [0, 1, 5, 10, 15] + [{"type": "num", "lower": 0, "upper": 20, "total_tests": 20}]
    })
    
    grader.add_test("is_palindrome", {
        "s": ["racecar", "hello", "A man a plan a canal Panama", "python"] + [{"type": "string", "lower_len": 3, "upper_len": 10, "total_tests": 20}]
    })
    
    grader.add_test("factorial", {
        "n": [0, 1, 5, 10] + [{"type": "num", "lower": 0, "upper": 12, "total_tests": 20}]
    })
    
    # Array tests with mutation tracking
    grader.add_test("sort_array", {
        "arr": [{"type": "array", "elements": [{"type": "num", "lower": 0, "upper": 100}, {"type": "num", "lower": 0, "upper": 100}, {"type": "num", "lower": 0, "upper": 100}], "total_tests": 3}]
    }, track_mutation=["arr"])
    
    # Dict tests (no mutation)
    grader.add_test("sum_dict_values", {
        "d": [{"type": "dict", "keys": [{"type": "string", "lower_len": 3, "upper_len": 5}], "values": [{"type": "num", "lower": 0, "upper": 10}], "total_tests": 3}]
    })
    
    # Array reverse with mutation tracking
    grader.add_test("reverse_array", {
        "arr": [{"type": "array", "elements": [{"type": "num", "lower": 0, "upper": 10}, {"type": "num", "lower": 0, "upper": 10}, {"type": "num", "lower": 0, "upper": 10}, {"type": "num", "lower": 0, "upper": 10}], "total_tests": 3}]
    }, track_mutation=["arr"])
    
    # Generate test suite
    test_calls, answer_key = grader.create_test_suite()
    print(f"Created: {test_calls}, {answer_key}")
    
    # Grade a student submission
    score = grader.grade_submission("TestStudent")
    print(f"\nGrade: {score['passed']}/{score['total']} passed")
    print(score["results"])
    print(f"Error: {score.get('error', 'None')}")
