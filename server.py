"""
Simple HTTP server for autograder
"""

import json
import os
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import parse_qs, urlparse
from backend import LabBackend


backend = LabBackend()

TEMPLATES_DIR = os.path.join(os.path.dirname(__file__), 'templates')


def load_html(filename):
    """Load HTML file from templates directory"""
    path = os.path.join(TEMPLATES_DIR, filename)
    with open(path, 'r', encoding='utf-8') as f:
        return f.read()


class AutograderHandler(BaseHTTPRequestHandler):
    
    def do_GET(self):
        """Handle GET requests"""
        path = urlparse(self.path).path
        
        if path == "/" or path == "/teacher":
            self.send_teacher_page()
        elif path == "/student":
            self.send_student_page()
        elif path == "/api/labs":
            self.send_labs_list()
        elif path == "/api/students":
            query = parse_qs(urlparse(self.path).query)
            lab_name = query.get('lab', [''])[0]
            self.send_students_list(lab_name)
        else:
            self.send_error(404, "Not Found")
    
    def do_POST(self):
        """Handle POST requests"""
        path = urlparse(self.path).path
        content_length = int(self.headers['Content-Length'])
        post_data = self.rfile.read(content_length).decode('utf-8')
        data = parse_qs(post_data)
        
        if path == "/api/create_lab":
            self.create_lab(data)
        elif path == "/api/submit":
            self.submit_code(data)
        elif path == "/api/grade":
            self.grade_submission(data)
        else:
            self.send_error(404, "Not Found")
    
    def send_teacher_page(self):
        """Send teacher interface HTML"""
        html = load_html('teacher.html')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_student_page(self):
        """Send student interface HTML"""
        html = load_html('student.html')
        
        self.send_response(200)
        self.send_header('Content-type', 'text/html')
        self.end_headers()
        self.wfile.write(html.encode())
    
    def send_labs_list(self):
        """Send list of labs as JSON"""
        labs = backend.list_labs()
        response = json.dumps({"labs": labs})
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def send_students_list(self, lab_name):
        """Send list of students for a lab"""
        students = backend.list_students(lab_name) if lab_name else []
        response = json.dumps({"students": students})
        
        self.send_response(200)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        self.wfile.write(response.encode())
    
    def create_lab(self, data):
        """Create a new lab"""
        try:
            lab_name = data['lab_name'][0]
            solution_code = data['solution_code'][0]
            
            # Parse test configuration from JSON
            test_config_json = data.get('test_config_json', ['[]'])[0]
            test_config = json.loads(test_config_json)
            
            print(f"Creating lab '{lab_name}' with {len(test_config)} tests")
            print(f"Test config: {test_config}")
            
            # Validate that tests exist
            if not test_config or len(test_config) == 0:
                raise ValueError("No tests configured! Please add at least one test method with parameters.")
            
            # Create the lab
            lab_path = backend.create_lab(lab_name, solution_code, test_config)
            
            response = json.dumps({
                "success": True,
                "message": f"Lab '{lab_name}' created successfully!",
                "path": lab_path
            })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            response = json.dumps({
                "success": False,
                "error": str(e)
            })
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
    
    def submit_code(self, data):
        """Submit student code"""
        try:
            lab_name = data['lab_name'][0]
            student_name = data['student_name'][0]
            student_code = data['student_code'][0]
            
            # Submit the code
            path = backend.submit_student_code(lab_name, student_name, student_code)
            
            response = json.dumps({
                "success": True,
                "message": f"Code submitted successfully for {student_name}!",
                "path": path
            })
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            response = json.dumps({
                "success": False,
                "error": str(e)
            })
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
    
    def grade_submission(self, data):
        """Grade a student submission"""
        try:
            lab_name = data['lab_name_grade'][0]
            student_name = data['student_name_grade'][0]
            
            # Grade the submission
            result = backend.grade_student(lab_name, student_name)
            
            response = json.dumps(result)
            
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())
            
        except Exception as e:
            response = json.dumps({
                "error": "Failed to grade submission",
                "details": str(e),
                "passed": 0,
                "total": 0,
                "results": []
            })
            
            self.send_response(500)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            self.wfile.write(response.encode())


def run_server(port=8000):
    """Run the HTTP server"""
    server_address = ('', port)
    httpd = HTTPServer(server_address, AutograderHandler)
    print(f"Server running on http://localhost:{port}")
    print(f"Teacher interface: http://localhost:{port}/teacher")
    print(f"Student interface: http://localhost:{port}/student")
    httpd.serve_forever()


if __name__ == "__main__":
    run_server()
