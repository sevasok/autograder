"""
Backend - Manages lab creation and student submissions
"""

import os
import shutil
from grader import Grader


class LabBackend:
    """Handles lab folder creation and student submission management."""
    
    def __init__(self, labs_root="Labs"):
        self.labs_root = os.path.abspath(labs_root)
        if not os.path.exists(self.labs_root):
            os.makedirs(self.labs_root)
    
    def create_lab(self, lab_name, solution_code, test_config):
        """Create a new lab. If exists, deletes old version including submissions."""
        lab_path = os.path.join(self.labs_root, lab_name)
        
        if os.path.exists(lab_path):
            shutil.rmtree(lab_path)
        
        os.makedirs(lab_path)
        os.makedirs(os.path.join(lab_path, "Submissions"))
        
        with open(os.path.join(lab_path, "solution.py"), 'w') as f:
            f.write(solution_code)
        
        grader = Grader(lab_path)
        for test in test_config:
            grader.add_test(test["method"], test["params"], test.get("track_mutation", []))
        
        grader.create_test_suite()
        return lab_path
    
    def submit_student_code(self, lab_name, student_name, student_code):
        """Submit student code. Renames existing main.py to submission#.py."""
        student_folder = os.path.join(self.labs_root, lab_name, "Submissions", student_name)
        os.makedirs(student_folder, exist_ok=True)
        
        main_py_path = os.path.join(student_folder, "main.py")
        
        if os.path.exists(main_py_path):
            submission_num = 1
            while os.path.exists(os.path.join(student_folder, f"submission{submission_num}.py")):
                submission_num += 1
            shutil.move(main_py_path, os.path.join(student_folder, f"submission{submission_num}.py"))
        
        with open(main_py_path, 'w') as f:
            f.write(student_code)
        
        return main_py_path
    
    def get_lab_path(self, lab_name):
        return os.path.join(self.labs_root, lab_name)
    
    def get_student_folder(self, lab_name, student_name):
        return os.path.join(self.labs_root, lab_name, "Submissions", student_name)
    
    def list_labs(self):
        if not os.path.exists(self.labs_root):
            return []
        return [d for d in os.listdir(self.labs_root) 
                if os.path.isdir(os.path.join(self.labs_root, d))]
    
    def list_students(self, lab_name):
        submissions_path = os.path.join(self.labs_root, lab_name, "Submissions")
        if not os.path.exists(submissions_path):
            return []
        return [d for d in os.listdir(submissions_path)
                if os.path.isdir(os.path.join(submissions_path, d))]
    
    def grade_student(self, lab_name, student_name):
        """Grade a student's submission."""
        grader = Grader(self.get_lab_path(lab_name))
        return grader.grade_submission(student_name)
