from datetime import datetime
from typing import List, Optional
from werkzeug.security import generate_password_hash, check_password_hash

# Since database.py imports models, and models needs db from somewhere to define relationships and tables
# if following an SQLAlchemy approach, we normally initialize db globally elsewhere.
# Given the dependency order listed, database.py connects later.
# Standard practice is flask_sqlalchemy.

from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

class ProjectUser(db.Model):
    """Association table linking users to projects."""
    __tablename__ = 'project_users'
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), primary_key=True)
    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), primary_key=True)

class User(db.Model):
    """Data model for system users."""
    __tablename__ = 'users'

    id = db.Column(db.Integer, primary_key=True)
    username = db.Column(db.String(80), unique=True, nullable=False)
    email = db.Column(db.String(120), unique=True, nullable=False)
    password_hash = db.Column(db.String(128), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    assigned_issues = db.relationship('Issue', backref='assignee', lazy=True, foreign_keys='Issue.assignee_id')
    reported_issues = db.relationship('Issue', backref='reporter', lazy=True, foreign_keys='Issue.reporter_id')
    comments = db.relationship('Comment', backref='author', lazy=True)
    projects = db.relationship('Project', secondary='project_users', backref=db.backref('members', lazy='dynamic'))

    def set_password(self, password: str) -> None:
        """Hashes and sets the user's password."""
        self.password_hash = generate_password_hash(password)

    def check_password(self, password: str) -> bool:
        """Checks if the provided password matches the stored hash."""
        return check_password_hash(self.password_hash, password)

class Project(db.Model):
    """Data model for college projects."""
    __tablename__ = 'projects'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(10), unique=True, nullable=False)
    name = db.Column(db.String(100), nullable=False)
    description = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issues = db.relationship('Issue', backref='project', lazy=True, cascade="all, delete-orphan")

class Issue(db.Model):
    """Data model for tracking issues/tasks."""
    __tablename__ = 'issues'

    id = db.Column(db.Integer, primary_key=True)
    key = db.Column(db.String(20), unique=True, nullable=False) # e.g., PROJ-1
    title = db.Column(db.String(200), nullable=False)
    description = db.Column(db.Text, nullable=True)
    status = db.Column(db.String(50), nullable=False, default='To Do') # To Do, In Progress, Done
    priority = db.Column(db.String(50), nullable=False, default='Medium') # Low, Medium, High, Critical
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    project_id = db.Column(db.Integer, db.ForeignKey('projects.id'), nullable=False)
    reporter_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)
    assignee_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=True)

    comments = db.relationship('Comment', backref='issue', lazy=True, cascade="all, delete-orphan")

class Comment(db.Model):
    """Data model for issue comments."""
    __tablename__ = 'comments'

    id = db.Column(db.Integer, primary_key=True)
    content = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    issue_id = db.Column(db.Integer, db.ForeignKey('issues.id'), nullable=False)
    user_id = db.Column(db.Integer, db.ForeignKey('users.id'), nullable=False)

if __name__ == "__main__":
    # Create the db tables if this module is run independently
    # This implies standard Flask application context setup, omitted here per requirement
    pass