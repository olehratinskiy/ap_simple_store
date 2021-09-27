from flask import Blueprint

api = Blueprint('api', __name__)

STUDENT_ID = 6


@api.route(f'/hello-world-{STUDENT_ID}')
def student_id_page():
    return f'Hello World {STUDENT_ID}'
