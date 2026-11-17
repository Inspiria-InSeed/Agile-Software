from flask import Blueprint, request, jsonify
from sqlalchemy.exc import SQLAlchemyError

from auth import token_required
from database import get_db_session
from models import User, Project, Issue, Comment

api_bp = Blueprint('api', __name__)

@api_bp.route('/users', methods=['GET'])
@token_required
def get_users():
    """Retrieves all registered users."""
    try:
        session = get_db_session()
        users = session.query(User).all()
        result = [{'id': u.id, 'username': u.username, 'email': u.email} for u in users]
        return jsonify(result), 200
    except SQLAlchemyError:
        return jsonify({'message': 'Internal database error'}), 500

@api_bp.route('/projects', methods=['GET', 'POST'])
@token_required
def handle_projects():
    """Handles creating a new project or listing existing ones."""
    session = get_db_session()
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('name') or not data.get('key'):
            return jsonify({'message': 'Name and key are required'}), 400
        
        new_project = Project(name=data['name'], key=data['key'], description=data.get('description', ''))
        try:
            session.add(new_project)
            session.commit()
            return jsonify({'id': new_project.id, 'name': new_project.name, 'key': new_project.key}), 201
        except SQLAlchemyError:
            session.rollback()
            return jsonify({'message': 'Could not create project, perhaps key exists'}), 400
            
    projects = session.query(Project).all()
    result = [{'id': p.id, 'name': p.name, 'key': p.key} for p in projects]
    return jsonify(result), 200

@api_bp.route('/issues', methods=['POST'])
@token_required
def create_issue():
    """Creates a new issue."""
    data = request.get_json()
    if not data or not data.get('title') or not data.get('project_id'):
        return jsonify({'message': 'Title and project_id are required'}), 400
        
    session = get_db_session()
    new_issue = Issue(
        title=data['title'],
        description=data.get('description', ''),
        status=data.get('status', 'Backlog'),
        project_id=data['project_id'],
        reporter_id=request.current_user.id,
        assignee_id=data.get('assignee_id')
    )
    
    try:
        session.add(new_issue)
        session.commit()
        return jsonify({'id': new_issue.id, 'title': new_issue.title, 'status': new_issue.status}), 201
    except SQLAlchemyError:
        session.rollback()
        return jsonify({'message': 'Could not create issue'}), 400

@api_bp.route('/issues/<int:issue_id>', methods=['GET', 'PUT', 'DELETE'])
@token_required
def handle_single_issue(issue_id: int):
    """Handles fetching, updating, or deleting a specific issue."""
    session = get_db_session()
    issue = session.query(Issue).get(issue_id)
    if not issue:
        return jsonify({'message': 'Issue not found'}), 404
        
    if request.method == 'GET':
        return jsonify({
            'id': issue.id,
            'title': issue.title,
            'description': issue.description,
            'status': issue.status,
            'project_id': issue.project_id
        }), 200
        
    elif request.method == 'PUT':
        data = request.get_json()
        if not data:
            return jsonify({'message': 'Request body needed'}), 400
        
        issue.title = data.get('title', issue.title)
        issue.description = data.get('description', issue.description)
        issue.status = data.get('status', issue.status)
        issue.assignee_id = data.get('assignee_id', issue.assignee_id)
        
        try:
            session.commit()
            return jsonify({'message': 'Issue updated'}), 200
        except SQLAlchemyError:
            session.rollback()
            return jsonify({'message': 'Update failed'}), 400
            
    elif request.method == 'DELETE':
        try:
            session.delete(issue)
            session.commit()
            return jsonify({'message': 'Issue deleted'}), 200
        except SQLAlchemyError:
            session.rollback()
            return jsonify({'message': 'Deletion failed'}), 500

@api_bp.route('/issues/<int:issue_id>/comments', methods=['GET', 'POST'])
@token_required
def handle_comments(issue_id: int):
    """Handles listing or adding comments to an issue."""
    session = get_db_session()
    if request.method == 'POST':
        data = request.get_json()
        if not data or not data.get('content'):
            return jsonify({'message': 'Content is required'}), 400
            
        new_comment = Comment(
            content=data['content'],
            issue_id=issue_id,
            author_id=request.current_user.id
        )
        try:
            session.add(new_comment)
            session.commit()
            return jsonify({'id': new_comment.id, 'content': new_comment.content}), 201
        except SQLAlchemyError:
            session.rollback()
            return jsonify({'message': 'Could not create comment'}), 400

    comments = session.query(Comment).filter_by(issue_id=issue_id).all()
    result = [{'id': c.id, 'content': c.content, 'author_id': c.author_id} for c in comments]
    return jsonify(result), 200