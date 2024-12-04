# DIY-Internal-Backend
Backend Repository for DIY Internal Project

This project implements a robust authentication system designed to handle user registration, authentication, and security using modern best practices.

---

## **Core Features**

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

## **API Endpoints**

| **Method** | **Endpoint**          | **Description**                          |
|------------|-----------------------|------------------------------------------|
| `POST`     | `/api/register/`      | Registers a new user.                    |
| `POST`     | `/api/login/`         | Authenticates user and provides tokens.  |
| `POST`     | `/api/token/refresh/` | Refreshes the access token.              |
| `GET`      | `/api/profile/`       | Retrieves the authenticated user's data. |

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
   - Access tokens expire after 30 minutes.
   - Refresh tokens are valid for 24 hours.

---

## **Setup and Installation**

1. Clone the repository:
   ```bash
   git clone <repository-url>
   cd <project-directory>
   ```

2. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

3. Run database migrations:
   ```bash
   python manage.py migrate
   ```

4. Start the development server:
   ```bash
   python manage.py runserver
   ```

---

## **How to Use**

1. Register a new user using the `/api/register/` endpoint.
2. Log in with your credentials at `/api/login/` to get the access and refresh tokens.
3. Use the access token for API requests (include it in the `Authorization` header as `Bearer <access-token>`).
4. Refresh the access token using `/api/token/refresh/` when it expires.

---

## **Technologies Used**

- **Django**: Backend framework
- **Django REST Framework (DRF)**: API development
- **JWT**: Secure user authentication
