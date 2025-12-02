# Taskflow API

A comprehensive FastAPI backend for task management in software teams with role-based access control (RBAC). Built with FastAPI, SQLAlchemy, JWT authentication, and SQLite database.

## 🎯 Features

### Core Features
- **Role-Based Access Control (RBAC)**: Two distinct user roles with different permissions
- **JWT Authentication**: Secure token-based authentication with role information
- **Database ORM**: SQLAlchemy ORM with SQLite database for development
- **RESTful API**: Clean, documented API endpoints following REST principles
- **Data Validation**: Pydantic models for request/response validation
- **Database Migrations**: Alembic integration for database versioning

### User Roles
1. **Backend Developer**: Regular user with limited access
   - View only their own tasks
   - Update status of their assigned tasks
   - Access personal task list with filtering

2. **Project Manager**: Elevated role with full system access
   - Create tasks for any developer
   - View all tasks across the team
   - Update any task (status, assignee, feedback, scores)
   - Delete tasks
   - Apply query parameters for filtering

### Task Management
- **Status Management**: TODO, IN_PROGRESS, COMPLETED, BLOCKED
- **Priority Levels**: Low (1), Medium (2), High (3)
- **Feedback System**: Project managers can provide feedback on tasks
- **Scoring System**: 1-10 scoring system for completed tasks
- **Time Tracking**: Automatic timestamp tracking for creation, updates, and completion

## 🏗️ Architecture

```
taskflow/
├── app/
│   ├── __init__.py
│   ├── main.py                 # FastAPI application entry point
│   ├── database.py             # SQLAlchemy configuration
│   ├── config.py               # Application settings
│   ├── models/                 # Database models
│   │   └── __init__.py         # User and Task models
│   ├── schemas/                # Pydantic schemas
│   │   ├── auth.py             # Authentication schemas
│   │   ├── tasks.py            # Task management schemas
│   │   └── __init__.py
│   ├── routers/                # API endpoints
│   │   ├── auth.py             # Authentication endpoints
│   │   ├── tasks.py            # Task management endpoints
│   │   └── __init__.py
│   └── auth/                   # Security utilities
│       ├── security.py         # JWT and password handling
│       └── __init__.py
├── alembic/                    # Database migrations
│   ├── env.py                  # Alembic environment
│   ├── script.py.mako          # Migration template
│   ├── versions/               # Migration files
│   │   └── 001_initial.py      # Initial migration
│   └── alembic.ini             # Alembic configuration
├── requirements.txt            # Dependencies
├── requirements-dev.txt        # Development dependencies
├── .env                        # Environment variables
├── start.sh                    # Startup script
└── README.md                   # This file
```

## 🚀 Quick Start

### Prerequisites
- Python 3.8+
- pip

### Installation

1. **Clone and navigate to the project**
   ```bash
   cd taskflow
   ```

2. **Make startup script executable**
   ```bash
   chmod +x start.sh
   ```

3. **Run the startup script**
   ```bash
   ./start.sh
   ```

The API will start on `http://localhost:8000`

### Manual Setup (Alternative)

1. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Run migrations**
   ```bash
   alembic upgrade head
   ```

4. **Start the server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 📖 API Documentation

Once the server is running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🔐 Default Users

The application creates default users for testing:

### Project Manager
- **Username**: `project_manager`
- **Email**: `pm@taskflow.com`
- **Password**: `pm123`

### Backend Developer
- **Username**: `backend_dev`
- **Email**: `dev@taskflow.com`
- **Password**: `dev123`

## 🛣️ API Endpoints

### Authentication (`/auth`)

#### POST `/auth/login`
Authenticate user and receive JWT token.

**Request:**
```json
{
  "username": "project_manager",
  "password": "manager123"
}
```

**Response:**
```json
{
  "access_token": "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzI1NiJ9...",
  "token_type": "bearer",
  "expires_in": 1800
}
```

#### POST `/auth/register`
Register a new user.

#### GET `/auth/me`
Get current user information (requires authentication).

#### POST `/auth/change-password`
Change user password (requires authentication).

### Task Management (`/tasks`)

#### Backend Developer Endpoints

**GET `/tasks/`**
Get current user's tasks with optional filtering.

**Parameters:**
- `status` (optional): Filter by status (`todo`, `in_progress`, `completed`, `blocked`)
- `page` (optional): Page number (default: 1)
- `per_page` (optional): Items per page (default: 10, max: 100)

**PUT `/tasks/{task_id}/status`**
Update status of own task.

**Request:**
```json
{
  "status": "completed"
}
```

#### Project Manager Endpoints

**GET `/tasks/all`**
Get all tasks with filtering options.

**Parameters:**
- `status` (optional): Filter by task status
- `assignee` (optional): Filter by assignee ID
- `page`, `per_page`: Pagination parameters

**POST `/tasks/`**
Create new task for any developer.

**Request:**
```json
{
  "title": "Implement API endpoint",
  "description": "Create RESTful endpoint for user management",
  "priority": 2,
  "assigned_to_id": 1
}
```

**PUT `/tasks/{task_id}`**
Update any task details.

**DELETE `/tasks/{task_id}`**
Delete a task.

**GET `/tasks/{task_id}`**
Get specific task by ID.

## 🔒 Security Features

### Authentication Flow
1. User sends username/password to `/auth/login`
2. Server validates credentials and returns JWT token
3. User includes token in subsequent requests: `Authorization: Bearer {token}`

### Role-Based Access Control
- JWT tokens contain user role information
- Backend Developers: Can only access their own tasks
- Project Managers: Full access to all tasks

### Password Security
- Passwords are hashed using bcrypt
- Secure password change endpoint with current password verification

## 🗄️ Database Schema

### Users Table
- `id`: Primary key
- `username`: Unique username
- `email`: Unique email address
- `full_name`: User's full name
- `hashed_password`: bcrypt hashed password
- `role`: User role (`backend_developer` or `project_manager`)
- `is_active`: Account status
- `created_at`, `updated_at`: Timestamps

### Tasks Table
- `id`: Primary key
- `title`: Task title
- `description`: Task description
- `status`: Task status (`todo`, `in_progress`, `completed`, `blocked`)
- `priority`: Task priority (1-3)
- `created_by_id`: ID of creating user (Project Manager)
- `assigned_to_id`: ID of assigned user (Backend Developer)
- `feedback`: Manager feedback on task
- `score`: Task score (1-10)
- `created_at`, `updated_at`, `completed_at`: Timestamps

## 🧪 Testing

### Using curl

1. **Login as Project Manager**
   ```bash
   curl -X POST "http://localhost:8000/auth/login" \
        -H "Content-Type: application/json" \
        -d '{"username": "project_manager", "password": "manager123"}'
   ```

2. **Create a task** (Project Manager only)
   ```bash
   curl -X POST "http://localhost:8000/tasks/" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE" \
        -H "Content-Type: application/json" \
        -d '{
          "title": "Build authentication system",
          "description": "Implement JWT authentication",
          "priority": 3,
          "assigned_to_id": 2
        }'
   ```

3. **Get user's tasks** (Backend Developer view)
   ```bash
   curl -X GET "http://localhost:8000/tasks/" \
        -H "Authorization: Bearer YOUR_TOKEN_HERE"
   ```

## 🛠️ Development

### Database Migrations

**Create new migration:**
```bash
alembic revision --autogenerate -m "Your migration message"
```

**Apply migrations:**
```bash
alembic upgrade head
```

**Rollback migration:**
```bash
alembic downgrade -1
```

### Environment Variables

Create a `.env` file for configuration:

```env
DATABASE_URL=sqlite:///./taskflow.db
SECRET_KEY=your-super-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_VERSION=1.0.0
DEBUG=true
```

## 📊 Data Isolation

### Backend Developer Access
- Can only view tasks assigned to them
- Can update task status (todo → in_progress → completed)
- Cannot view other developers' tasks
- Cannot modify task assignments or scores

### Project Manager Access
- Can view all tasks across the team
- Can create tasks for any developer
- Can update any task attribute
- Can delete tasks
- Can apply filtering and sorting
- Can provide feedback and scores

## 🚦 Error Handling

The API returns appropriate HTTP status codes:

- `200 OK`: Successful request
- `201 Created`: Resource created successfully
- `400 Bad Request`: Invalid input data
- `401 Unauthorized`: Authentication required or failed
- `403 Forbidden`: Insufficient permissions
- `404 Not Found`: Resource not found
- `500 Internal Server Error`: Server error

## 🔄 Production Considerations

For production deployment:

1. **Environment Configuration**
   - Change `SECRET_KEY` to a secure random value
   - Use a production database (PostgreSQL, MySQL)
   - Disable `DEBUG` mode
   - Configure proper CORS origins

2. **Security Enhancements**
   - Implement rate limiting
   - Add input sanitization
   - Use HTTPS in production
   - Consider implementing refresh tokens

3. **Database**
   - Use connection pooling
   - Implement proper backup strategy
   - Consider read replicas for scaling

4. **Monitoring**
   - Add logging and monitoring
   - Implement health checks
   - Set up error tracking





---

**Author**: MiniMax Agent  
**Created**: 2025-12-02  
**Version**: 1.0.0
