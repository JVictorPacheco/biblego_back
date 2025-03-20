from flask import Blueprint, jsonify, request
from app.Service.task_service import TaskService

task_blueprint = Blueprint('task', __name__)


@task_blueprint.route('/tasks_come', methods=['GET'])
def get_tasks():
    task_service = TaskService()
    tasks = task_service.get_all_tasks()
    return jsonify({"tasks": tasks})
                    # [task.to_dict() for task in tasks]})


@task_blueprint.route('/tasks_go', methods=['POST'])
def add_task():
    task_service = TaskService()
    data = request.json
    if not data or not 'title' in data:
        return jsonify({"error": "Titulo é obrigatório"}), 400
    try:
        new_task = task_service.add_task(data['title'])
        return jsonify({'task': new_task}), 201
    except ValueError as e:
        return jsonify({"error": str(e)}), 400




