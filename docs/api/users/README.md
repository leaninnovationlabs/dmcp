# Users API

This document describes the user management endpoints for Data MCP, including authentication, user creation, and password management.

## Default Admin Account

When Data MCP is first installed, a default admin account is automatically created:

- **Username**: `admin`
- **Password**: `dochangethispassword`
- **User ID**: `1`

⚠️ **Security Warning**: Change this default password immediately after your first login!

## Authentication

### User Login

**POST** `/dmcp/users/login`

Authenticate a user with username and password.

#### Request Body

```json
{
  "username": "admin",
  "password": "dochangethispassword"
}
```

#### Response

```json
{
  "data": {
    "id": 1,
    "username": "admin",
    "first_name": "Admin",
    "last_name": "Admin",
    "roles": ["admin"],
    "created_at": "2024-01-01T00:00:00Z",
    "updated_at": "2024-01-01T00:00:00Z"
  },
  "success": true,
  "errors": [],
  "warnings": []
}
```

#### Example Usage

```bash
curl -X POST "http://localhost:8000/dmcp/users/login" \
  -H "Content-Type: application/json" \
  -d '{
    "username": "admin",
    "password": "dochangethispassword"
  }'
```

## User Management

### Create User

**POST** `/dmcp/users/`

Create a new user account.

#### Request Body

```json
{
  "username": "newuser",
  "password": "securepassword123",
  "first_name": "New",
  "last_name": "User",
  "roles": ["user"]
}
```

### Get All Users

**GET** `/dmcp/users/`

Retrieve a list of all users.

### Get User by ID

**GET** `/dmcp/users/{user_id}`

Retrieve a specific user by their ID.

### Update User

**PUT** `/dmcp/users/{user_id}`

Update user information.

### Delete User

**DELETE** `/dmcp/users/{user_id}`

Delete a user account.

## Password Management

### Change Password

**POST** `/dmcp/users/{user_id}/change-password`

Change a user's password.

#### Request Body

```json
{
  "current_password": "dochangethispassword",
  "new_password": "newsecurepassword456"
}
```

#### Example Usage

```bash
curl -X POST "http://localhost:8000/dmcp/users/1/change-password" \
  -H "Content-Type: application/json" \
  -d '{
    "current_password": "dochangethispassword",
    "new_password": "newsecurepassword456"
  }'
```

## Password Reset Procedures

### For Default Admin Account Recovery

If you've forgotten the admin password:

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

## Error Responses

### Invalid Credentials

```json
{
  "data": null,
  "success": false,
  "errors": ["Invalid username or password"],
  "warnings": []
}
```

### User Not Found

```json
{
  "data": null,
  "success": false,
  "errors": ["User not found"],
  "warnings": []
}
```

### Password Change Failed

```json
{
  "data": null,
  "success": false,
  "errors": ["Current password is incorrect"],
  "warnings": []
}
```

## Security Notes

1. **Default Password**: Always change the default admin password immediately
2. **Strong Passwords**: Use strong passwords with mixed characters
3. **Password Storage**: Passwords are encrypted using Fernet encryption
4. **Session Management**: Consider implementing session timeouts
5. **Access Control**: Use roles to control user permissions

## Testing

You can test the endpoints using the provided Bruno API files:

- `login.bru`: Test user authentication
- `create.bru`: Test user creation
- `change password.bru`: Test password changes
- `list.bru`: Test user listing
- `get.bru`: Test user retrieval
- `update.bru`: Test user updates
- `delete.bru`: Test user deletion

Or use the Python test scripts:

```bash
# Test user creation
uv run scripts/test_user_creation.py

# Test user authentication
uv run scripts/test_users_me.py
```
