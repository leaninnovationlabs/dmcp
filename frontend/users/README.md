# Users Section

This directory contains user-related UI components for the DMCP application.

## Default Admin Account

When DMCP is first installed, a default admin account is automatically created:

- **Username**: `admin`
- **Password**: `dochangethispassword`

⚠️ **Security Warning**: Change this default password immediately after your first login!

### Initial Login Process

1. Navigate to the DMCP web interface: http://localhost:8000/dmcp/ui
2. Use the default credentials:
   - Username: `admin`
   - Password: `dochangethispassword`
3. Once logged in, immediately change the password using the Change Password feature

## Files

- `change-password.html` - Password change form with modern UI
- `change-password.js` - JavaScript functionality for password management

## Features

### Password Change
- Secure password change functionality
- Real-time password strength validation
- Password visibility toggle
- Form validation and error handling
- Success/error message display
- Responsive design

## API Endpoints Used

- `GET /users/me` - Get current user information
- `POST /users/{user_id}/change-password` - Change user password

## Usage

1. Navigate to the Change Password page via:
   - Sidebar: User Profile → Change Password
   - Home page: User Profile section → Change Password button

2. Enter your current password
3. Enter a new password (with strength validation)
4. Confirm the new password
5. Submit the form

## Security Features

- Password strength validation
- Current password verification
- Secure API communication with JWT tokens
- Form validation and sanitization
