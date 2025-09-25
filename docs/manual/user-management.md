# User Management

This document describes the user management functionality in Data MCP, including user creation, authentication, role management, and API endpoints.

## Overview

The user management system provides a complete solution for managing users in the Data MCP application. It includes:

- User registration and authentication
- Role-based access control
- Secure password storage with encryption
- RESTful API endpoints for all user operations
- Comprehensive validation and error handling

## Default Admin Account

When you first install Data MCP, a default admin account is automatically created with the following credentials:

- **Username**: `admin`
- **Password**: `dochangethispassword`
- **Roles**: `admin`

⚠️ **Security Warning**: It's crucial to change this default password immediately after your first login for security purposes.

### Changing the Default Admin Password

You can change the admin password using several methods:

#### Method 1: Using the API
```bash
curl -X POST http://localhost:8000/dmcp/users/1/change-password \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -d '{
    "current_password": "dochangethispassword",
    "new_password": "your-new-secure-password"
  }'
```

#### Method 2: Using the Web UI
1. Navigate to http://localhost:8000/dmcp/ui
2. Login with the default credentials (admin/dochangethispassword)
3. Go to the Users section
4. Click on the admin user
5. Use the "Change Password" feature

#### Method 3: Using the Login API First
If you need to authenticate first:
```bash
# First, login to get a session
curl -X POST http://localhost:8000/dmcp/users/login \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "dochangethispassword"
  }'

# Then change the password using the user ID (1)
curl -X POST http://localhost:8000/dmcp/users/1/change-password \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "dochangethispassword",
    "new_password": "your-new-secure-password"
  }'
```

## User Model

Each user in the system has the following attributes:

| Field | Type | Description | Required |
|-------|------|-------------|----------|
| `id` | Integer | Unique identifier (auto-generated) | Yes |
| `username` | String(255) | Unique username for login | Yes |
| `password` | String(255) | Encrypted password | Yes |
| `first_name` | String(255) | User's first name | Yes |
| `last_name` | String(255) | User's last name | Yes |
| `roles` | String | Comma-separated list of user roles | No (default: "") |
| `created_at` | DateTime | Account creation timestamp | Auto |
| `updated_at` | DateTime | Last update timestamp | Auto |

## Security Features

### Password Encryption
- Passwords are encrypted using the Fernet symmetric encryption algorithm
- Each password is encrypted before storage and decrypted for verification
- Uses the same encryption system as datasource passwords for consistency

### Role-Based Access Control
- Users can have multiple roles
- Roles are stored as a comma-separated string in the database
- API responses return roles as an array for easy frontend consumption
- Common roles include: `admin`, `user`, `viewer`, etc.
- Roles can be dynamically added/removed

## API Endpoints

### User Management

#### Create User
```http
POST /dmcp/users/
```

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123",
  "first_name": "John",
  "last_name": "Doe",
  "roles": ["user", "admin"]
}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["user", "admin"],
    "created_at": "2025-08-30T20:54:34.973923",
    "updated_at": "2025-08-30T20:54:34.973923"
  },
  "success": true,
  "errors": [],
  "warnings": []
}
```

#### Get All Users
```http
GET /dmcp/users/
```

**Response:**
```json
{
  "data": [
    {
      "id": 1,
      "username": "johndoe",
      "first_name": "John",
      "last_name": "Doe",
      "roles": ["user", "admin"],
      "created_at": "2025-08-30T20:54:34.973923",
      "updated_at": "2025-08-30T20:54:34.973923"
    }
  ],
  "success": true,
  "errors": [],
  "warnings": []
}
```

#### Get User by ID
```http
GET /dmcp/users/{user_id}
```

#### Update User
```http
PUT /dmcp/users/{user_id}
```

**Request Body:**
```json
{
  "first_name": "Johnny",
  "roles": ["user", "admin", "viewer"]
}
```

#### Delete User
```http
DELETE /dmcp/users/{user_id}
```

### Authentication

#### User Login
```http
POST /dmcp/users/login
```

**Request Body:**
```json
{
  "username": "johndoe",
  "password": "securepassword123"
}
```

**Response:**
```json
{
  "data": {
    "id": 1,
    "username": "johndoe",
    "first_name": "John",
    "last_name": "Doe",
    "roles": ["user", "admin"],
    "created_at": "2025-08-30T20:54:34.973923",
    "updated_at": "2025-08-30T20:54:34.973923"
  },
  "success": true,
  "errors": [],
  "warnings": []
}
```

#### Change Password
```http
POST /dmcp/users/{user_id}/change-password
```

**Request Body:**
```json
{
  "current_password": "securepassword123",
  "new_password": "newsecurepassword456"
}
```

### Password Reset Procedures

#### For Admin Users
If you're an admin user and need to reset another user's password:

1. **Using the API** (if you have admin privileges):
```bash
curl -X PUT http://localhost:8000/dmcp/users/{user_id} \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer YOUR_ADMIN_TOKEN" \
  -d '{
    "password": "new-temporary-password"
  }'
```

2. **Using the Web UI**:
   - Navigate to the Users section
   - Find the user you want to reset
   - Use the "Reset Password" feature (if available)

#### For Default Admin Account Recovery
If you've forgotten the admin password and need to recover access:

1. **Database Reset** (if no other admin users exist):
```bash
# Stop the application
# Delete the database file
rm dmcp.db

# Reinitialize the database (this will recreate the default admin account)
uv run alembic upgrade head

# Restart the application
uv run main.py
```

⚠️ **Warning**: This will delete all existing data and users!

2. **Create a New Admin User** (if you have database access):
```bash
# Use the test script to create a new admin user
uv run scripts/test_user_creation.py
```

#### Password Security Best Practices
- Use strong passwords (minimum 8 characters, mix of letters, numbers, symbols)
- Change default passwords immediately
- Use unique passwords for different accounts
- Consider using a password manager
- Regularly update passwords
- Never share passwords or store them in plain text

### Role Management

#### Add Role to User
```http
POST /dmcp/users/{user_id}/roles/{role}
```

#### Remove Role from User
```http
DELETE /dmcp/users/{user_id}/roles/{role}
```

#### Get Users by Role
```http
GET /dmcp/users/by-role/{role}
```

## Database Schema

The users table is created using Alembic migrations. The current migration file is:
`alembic/versions/155f613d7a50_add_users_table.py`

To apply the migration:
```bash
alembic upgrade head
```

## Usage Examples

### Creating a New User

```python
from app.services.user_service import UserService
from app.models.schemas import UserCreate

# Create user service
user_service = UserService(db)

# Create user data
user_data = UserCreate(
    username="newuser",
    password="password123",
    first_name="New",
    last_name="User",
    roles=["user"]
)

# Create the user
user = await user_service.create_user(user_data)
```

### Authenticating a User

```python
from app.models.schemas import UserLogin

# Login data
login_data = UserLogin(
    username="newuser",
    password="password123"
)

# Authenticate user
user = await user_service.authenticate_user(login_data)
if user:
    print(f"Welcome, {user.first_name}!")
else:
    print("Invalid credentials")
```

### Managing User Roles

```python
# Add admin role
user = await user_service.add_role_to_user(user_id, "admin")

# Remove user role
user = await user_service.remove_role_from_user(user_id, "user")

# Get all admin users
admin_users = await user_service.get_users_by_role("admin")
```

## Error Handling

The API returns standardized error responses:

```json
{
  "data": null,
  "success": false,
  "errors": ["Username already exists"],
  "warnings": []
}
```

Common error scenarios:
- **400 Bad Request**: Invalid input data, duplicate username
- **401 Unauthorized**: Invalid login credentials
- **404 Not Found**: User not found
- **500 Internal Server Error**: Database or system errors

## Testing

Run the user management tests:
```bash
pytest tests/test_user.py -v
```

Test user creation manually:
```bash
python scripts/test_user_creation.py
```

## Security Considerations

1. **Password Storage**: Passwords are encrypted using Fernet encryption
2. **Input Validation**: All user inputs are validated using Pydantic schemas
3. **SQL Injection Protection**: Uses SQLAlchemy ORM with parameterized queries
4. **Role Validation**: Roles are stored as arrays and validated
5. **Audit Trail**: All user operations include timestamps

## Future Enhancements

Potential improvements for the user management system:

1. **Password Policies**: Enforce password complexity requirements
2. **Account Lockout**: Implement account lockout after failed attempts
3. **Session Management**: Add JWT-based session management
4. **Two-Factor Authentication**: Support for 2FA
5. **User Groups**: Organize users into groups for easier management
6. **Audit Logging**: Track all user actions for compliance
7. **Password Expiration**: Force password changes after time periods
