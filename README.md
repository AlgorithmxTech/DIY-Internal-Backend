# DIY-Internal-Backend
Backend Repository for DIY Internal Project

This project implements a authentication system designed to handle user registration, authentication, and security using modern best practices.

---

## **Current Features**

### **1. User Registration**
- Custom user model that uses **email** instead of a username for login.
- Includes **password validation** and **confirmation** during registration.
- Generates an **email verification token** to confirm user identity.
- Tracks user creation timestamps for auditing purposes.

### **2. JWT Authentication**
- Implements **JSON Web Token (JWT)** for secure authentication.
- Upon login:
  - Generates an **access token** (valid for 30 minutes).
  - Generates a **refresh token** (valid for 24 hours).
- **Token rotation** is enforced for enhanced security.

---

## **Authentication Flow**

1. **User Registration:**
   - Users register with their email and password.
   - A verification token is sent to their email to confirm the account.

2. **Login:**
   - Users authenticate with their email and password.
   - On success, access and refresh tokens are issued.

3. **Token Handling:**
   - Access tokens are used for making API requests.
   - Refresh tokens are used to obtain new access tokens when the old one expires.

4. **Token Expiry:**
   - Access tokens expire after 2 Hours.
   - Refresh tokens are valid for 24 hours.

---


## **Setup and Installation**
## For Dev Branch only

1. **Generate SSH Keys from VM**:
   ```bash
   ssh-keygen -t ed25519 -C "rolando.tactay@algorithmx.com"
   ```

2. **Add the SSH Key to Your GitHub Account**:
   - Copy the public key (`~/.ssh/id_ed25519.pub`) and add it to your GitHub user account under **Settings > SSH and GPG keys**.

3. **Clone the Repository**:
   ```bash
   git clone --branch develop --single-branch git@github.com:AlgorithmxTech/DIY-Internal-Backend.git
   cd DIY-Internal-Backend
   ```

4. **Create a `.env` File**:
   - Inside the project folder, create a `.env` file and configure the required environment variables. Example:
     ```
     DEBUG=True
     SECRET_KEY=your-secret-key
     DATABASE_URL=your-database-url
     ```

5. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   ```

6. **Activate the Virtual Environment**:
   - **Linux/MacOS**:
     ```bash
     source venv/bin/activate
     ```
   - **Windows (Command Prompt)**:
     ```cmd
     venv\Scripts\activate
     ```
   - **Windows (PowerShell)**:
     ```powershell
     .\venv\Scripts\Activate.ps1
     ```

7. **Install Required Packages**:
   ```bash
   pip install -r requirements.txt
   ```

8. **Run the Server (Debug Mode is Enabled)**:
   ```bash
   python3 manage.py runserver 0.0.0.0:8000
   ```
---

## **Technologies Used**

- **Django**: Backend framework
- **Django REST Framework (DRF)**: API development
- **JWT**: Secure user authentication

# Authentication API Documentation

## Base URL
```
http://192.168.100.214:8000/api
```

## Authentication
Most endpoints require JWT authentication. Include the token in the Authorization header:
```
Authorization: Bearer <your_access_token>
```

## Endpoints and Usage

### 1. Register New User
**Endpoint:** `POST /register/`

**Payload:**
```json
{
    "email": "user@example.com",
    "username": "user",
    "password": "password123",
    "password_confirm": "password123"
}
```

**Response:**
```json
{
    "message": "Registration successful. Please check your email to verify your account.",
    "email_status": "sent"
}
```

### 2. Login
**Endpoint:** `POST /login/`

**Payload:**
```json
{
    "email": "user@example.com",
    "password": "password123"
}
```

**Success Response:**
```json
{
    "access": "your.access.token",
    "refresh": "your.refresh.token",
    "user": {
        "id": 1,
        "email": "user@example.com",
        "username": "user",
        "is_email_verified": true,
        "created_at": "2024-12-06T10:00:00Z"
    }
}
```

**Error Response (After multiple failed attempts):**
```json
{
    "detail": "Too many failed attempts. Please try again later."
}
```

### 3. Refresh Token
**Endpoint:** `POST /token/refresh/`

**Payload:**
```json
{
    "refresh": "your.refresh.token"
}
```

**Response:**
```json
{
    "access": "new.access.token"
}
```

### 4. Email Verification
**Endpoint:** `GET /verify-email/confirm/?token=<verification_token>`

This endpoint is accessed via email link, not direct API call. Redirects to frontend after verification.

### 5. Forgot Password
**Endpoint:** `POST /forgot-password/`

**Payload:**
```json
{
    "email": "user@example.com"
}
```

**Response:**
```json
{
    "message": "Password reset link has been sent to your email."
}
```

### 6. Reset Password
**Endpoint:** `POST /reset-password/`

**Payload:**
```json
{
    "token": "reset-token-from-email",
    "new_password": "newpassword123",
    "confirm_password": "newpassword123"
}
```

**Response:**
```json
{
    "message": "Password has been reset successfully."
}
```

### 7. Get User Profile
**Endpoint:** `GET /profile/`

**Headers Required:**
- Authorization: Bearer <access_token>

**Response:**
```json
{
    "id": 1,
    "email": "user@example.com",
    "username": "user",
    "is_email_verified": true,
    "created_at": "2024-12-06T10:00:00Z"
}
```

## Error Responses

### Validation Error
```json
{
    "detail": {
        "field_name": [
            "Error message"
        ]
    }
}
```

### Authentication Error
```json
{
    "detail": "Invalid credentials"
}
```

### Token Error
```json
{
    "detail": "Token is invalid or expired"
}
```

## Status Codes
- 200: Success
- 201: Created
- 400: Bad Request
- 401: Unauthorized
- 403: Forbidden
- 404: Not Found
- 429: Too Many Requests

## Rate Limiting
- Login attempts are limited to 5 failed attempts per email/IP combination within 24 hours
- After exceeding this limit, temporary lockout is enforced

## Security Features
1. JWT Token Authentication
2. Email verification required
3. Failed login attempt tracking
4. Password complexity requirements
5. Secure password reset process
6. HTTP-only cookies for token storage

## Development Notes
- Debug mode shows additional information in responses
- Email verification links are included in API responses during development
- Frontend URL configurations are required for redirects
