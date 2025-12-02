# Taskflow API - Deployment & Demonstration Guide

## 🚀 Quick Start

### Prerequisites
- Python 3.8+ 
- pip

### Installation Steps

1. **Clone/Navigate to project directory**
   ```bash
   cd taskflow
   ```

2. **Create virtual environment**
   ```bash
   python3 -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   pip install email-validator  # Required for email validation
   ```

4. **Initialize database**
   ```bash
   alembic upgrade head
   ```

5. **Start the API server**
   ```bash
   uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
   ```

## 🧪 API Testing with Default Users

### 1. Project Manager Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "project_manager", "password": "pm123"}'
```

### 2. Backend Developer Login
```bash
curl -X POST "http://localhost:8000/auth/login" \
     -H "Content-Type: application/json" \
     -d '{"username": "backend_dev", "password": "dev123"}'
```

### 3. Create Task (Project Manager Only)
```bash
# Replace YOUR_PM_TOKEN with the token from step 1
curl -X POST "http://localhost:8000/tasks/" \
     -H "Authorization: Bearer YOUR_PM_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "title": "Implement User Authentication API",
       "description": "Build JWT-based authentication system with role validation",
       "priority": 3,
       "assigned_to_id": 2
     }'
```

### 4. Backend Developer Views Their Tasks
```bash
# Replace YOUR_DEV_TOKEN with the token from step 2
curl -X GET "http://localhost:8000/tasks/" \
     -H "Authorization: Bearer YOUR_DEV_TOKEN"
```

### 5. Backend Developer Updates Task Status
```bash
# Replace TASK_ID with the actual task ID and YOUR_DEV_TOKEN
curl -X PUT "http://localhost:8000/tasks/TASK_ID/status" \
     -H "Authorization: Bearer YOUR_DEV_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{"status": "in_progress"}'
```

### 6. Project Manager Updates Task Details
```bash
# Replace TASK_ID with the actual task ID and YOUR_PM_TOKEN
curl -X PUT "http://localhost:8000/tasks/TASK_ID" \
     -H "Authorization: Bearer YOUR_PM_TOKEN" \
     -H "Content-Type: application/json" \
     -d '{
       "status": "completed",
       "feedback": "Excellent work! Clean implementation.",
       "score": 9
     }'
```

## 🔍 Complete API Testing Script

Use the provided `test_api.py` script for comprehensive testing:

```bash
python test_api.py
```

This script will:
1. Test authentication for both user types
2. Demonstrate role-based access control
3. Create, update, and manage tasks
4. Verify data isolation between roles
5. Show error handling for unauthorized access

## 🏗️ Architecture Highlights

### Role-Based Access Control (RBAC)
- **Backend Developers**: Can only access their own tasks
- **Project Managers**: Have full system access with team-wide oversight

### Authentication Flow
1. Users authenticate with username/password
2. Server returns JWT token containing user ID and role
3. Clients use token in subsequent requests: `Authorization: Bearer {token}`
4. Server validates token and enforces role-based access

### Database Schema
- **Users Table**: User accounts with role information
- **Tasks Table**: Task management with relationships and constraints
- **Enums**: Strictly defined roles and task statuses

### API Endpoints Summary

#### Authentication (`/auth`)
- `POST /auth/login` - User authentication
- `POST /auth/register` - User registration
- `GET /auth/me` - Get current user info
- `POST /auth/change-password` - Change password

#### Task Management (`/tasks`)
- **Backend Developer Endpoints:**
  - `GET /tasks/` - View own tasks
  - `PUT /tasks/{id}/status` - Update task status
  
- **Project Manager Endpoints:**
  - `GET /tasks/all` - View all tasks
  - `POST /tasks/` - Create new task
  - `PUT /tasks/{id}` - Update any task
  - `DELETE /tasks/{id}` - Delete task

## 🔒 Security Features

### Password Security
- bcrypt hashing with salt
- Secure password change with current password verification
- No plaintext password storage

### JWT Security
- HS256 algorithm with configurable secret key
- Token expiration (30 minutes by default)
- Role information embedded in token
- Proper token validation on every request

### Data Isolation
- Backend Developers cannot see other developers' tasks
- Backend Developers cannot modify task assignments
- Backend Developers cannot provide scores or feedback
- All access control enforced at API level

### Input Validation
- Pydantic models for all requests
- Email validation for user registration
- Status validation against allowed values
- Score validation (1-10 range)

## 🗄️ Database Migrations

### Creating New Migrations
```bash
# Create migration from model changes
alembic revision --autogenerate -m "Description of changes"

# Apply migrations
alembic upgrade head

# Rollback migration
alembic downgrade -1
```

### Migration Files
- Initial migration creates users and tasks tables
- Proper foreign key relationships
- Indexes for performance
- Enum constraints for data integrity

## 🚀 Production Deployment

### Environment Setup
```env
# .env file
DATABASE_URL=postgresql://user:password@localhost/taskflow
SECRET_KEY=your-secure-random-secret-key-change-in-production
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=30
API_VERSION=1.0.0
DEBUG=false
```

### Production Considerations
1. **Database**: Use PostgreSQL or MySQL instead of SQLite
2. **Security**: Use strong, random secret keys
3. **CORS**: Configure specific allowed origins
4. **HTTPS**: Use TLS in production
5. **Logging**: Implement proper logging and monitoring
6. **Rate Limiting**: Add API rate limiting
7. **Error Handling**: Implement comprehensive error tracking

### Docker Deployment (Optional)
```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .
EXPOSE 8000

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

## 📊 Performance Considerations

### Database
- Connection pooling for high traffic
- Proper indexing on frequently queried fields
- Query optimization for complex joins

### API
- Pagination for large datasets
- Async/await for I/O operations
- Efficient filtering and sorting

### Authentication
- Token caching on client side
- Minimal database queries for token validation
- Configurable token expiration

## 🧪 Testing Strategy

### Unit Tests
- Model validation
- Authentication logic
- Permission enforcement

### Integration Tests
- API endpoint testing
- Database operations
- Role-based access validation

### Test Coverage
- All authentication endpoints
- Task CRUD operations
- Access control enforcement
- Error handling scenarios

## 📝 API Documentation

Once the server is running:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc
- **OpenAPI JSON**: http://localhost:8000/openapi.json

## 🐛 Troubleshooting

### Common Issues

1. **Import Errors**: Ensure PYTHONPATH includes project root
2. **Database Errors**: Run `alembic upgrade head`
3. **Authentication Issues**: Verify default users are created
4. **Permission Errors**: Check user roles and token validity

### Logs and Debugging
- Application logs show startup and error details
- Database logs for query issues
- Authentication logs for login failures
- Access control logs for permission violations

## 📈 Scalability

### Horizontal Scaling
- Stateless API design allows load balancing
- Database read replicas for query performance
- Caching layer for frequently accessed data

### Vertical Scaling
- Optimized queries and database indexes
- Connection pooling for database efficiency
- Async operations for better throughput

---

**This comprehensive Taskflow API demonstrates advanced backend development skills with:**
- FastAPI framework expertise
- Database design and ORM usage
- Authentication and authorization
- Role-based access control
- RESTful API design
- Production-ready architecture
- Testing and documentation