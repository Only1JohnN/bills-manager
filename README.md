# Bills Manager

Bills Manager is a Django-based application designed to help users manage their bills efficiently. It provides features such as bill creation, recurring bill management, reminders, OTP-based authentication, and password reset functionality. The application also integrates with Celery for task scheduling and Redis for caching.

---

## Table of Contents

- [Features](#features)
- [Tech Stack](#tech-stack)
- [Setup and Installation](#setup-and-installation)
- [Environment Variables](#environment-variables)
- [API Endpoints](#api-endpoints)
- [Authentication](#authentication)
- [Recurring Bills](#recurring-bills)
- [Pagination](#pagination)
- [Email Notifications](#email-notifications)
- [Testing](#testing)
- [Deployment](#deployment)
- [Contributing](#contributing)
- [License](#license)

---

## Features

- **User Authentication**:
  - Register, login, and logout with JWT-based authentication.
  - OTP-based email verification for account activation.
  - Password reset functionality with secure token-based validation.

- **Bill Management**:
  - Create, update, delete, and view bills.
  - Support for recurring bills with customizable frequencies (daily, weekly, monthly, etc.).
  - Automatic reminders for upcoming bills.

- **Admin Dashboard**:
  - Manage users and bills via the Django admin interface.
  - View and filter bills by category, priority, and due date.

- **Email Notifications**:
  - OTP emails for account verification.
  - Password reset emails with secure links.
  - Welcome emails for new users.

- **Task Scheduling**:
  - Celery integration for handling recurring bills and reminders.
  - Redis as the message broker for Celery tasks.

- **Pagination**:
  - Paginated API responses for bill listings.

---

## Tech Stack

- **Backend**: Django, Django REST Framework
- **Database**: SQLite (default), PostgreSQL (for production)
- **Task Queue**: Celery with Redis
- **Authentication**: JWT (via `djangorestframework-simplejwt`)
- **Email**: SMTP (Mailtrap for development)
- **Testing**: Django Test Framework
- **Deployment**: Gunicorn, Docker (optional)

---

## Setup and Installation

### Prerequisites

- Python 3.10 or higher
- Redis (for Celery)
- PostgreSQL (optional for production)
- Virtual environment tool (e.g., `venv` or `virtualenv`)

### Installation Steps

1. **Clone the Repository**:
   ```bash
   git clone https://github.com/your-username/bills-manager.git
   cd bills-manager
   ```

2. **Create a Virtual Environment**:
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows: venv\Scripts\activate
   ```

3. **Install Dependencies**:
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Up Environment Variables**:
   Create a `.env` file in the project root and configure the following variables:
   ```env
   EMAIL_HOST=sandbox.smtp.mailtrap.io
   EMAIL_HOST_USER=your_mailtrap_user
   EMAIL_HOST_PASSWORD=your_mailtrap_password
   EMAIL_PORT=587
   EMAIL_USE_TLS=True
   EMAIL_USE_SSL=False
   ```

5. **Run Migrations**:
   ```bash
   python manage.py makemigrations
   python manage.py migrate
   ```

6. **Start the Development Server**:
   ```bash
   python manage.py runserver
   ```

7. **Start Redis and Celery**:
   - Start Redis:
     ```bash
     redis-server
     ```
   - Start Celery:
     ```bash
     celery -A bills-manager worker --loglevel=info
     ```

---

## Environment Variables

The following environment variables are required for the project:

| Variable               | Description                          | Example Value                  |
|------------------------|--------------------------------------|--------------------------------|
| `EMAIL_HOST`           | SMTP server host                    | `sandbox.smtp.mailtrap.io`     |
| `EMAIL_HOST_USER`      | SMTP username                       | `your_mailtrap_user`           |
| `EMAIL_HOST_PASSWORD`  | SMTP password                       | `your_mailtrap_password`       |
| `EMAIL_PORT`           | SMTP port                           | `587`                          |
| `EMAIL_USE_TLS`        | Use TLS for email                   | `True`                         |
| `EMAIL_USE_SSL`        | Use SSL for email                   | `False`                        |

---

## API Endpoints

### Authentication

| Method | Endpoint                  | Description                     |
|--------|---------------------------|---------------------------------|
| POST   | `/api/auth/register/`     | Register a new user             |
| POST   | `/api/auth/login/`        | Login and get JWT tokens        |
| POST   | `/api/auth/logout/`       | Logout and blacklist tokens     |
| POST   | `/api/auth/forgot-password/` | Request password reset OTP    |
| POST   | `/api/auth/verify-password-otp/` | Verify OTP for password reset |
| POST   | `/api/auth/reset-password/<uidb64>/<token>/` | Reset password |

### Bills

| Method | Endpoint                  | Description                     |
|--------|---------------------------|---------------------------------|
| GET    | `/api/bills/`             | List all bills (paginated)      |
| POST   | `/api/bills/`             | Create a new bill               |
| GET    | `/api/bills/<id>/`        | Retrieve a specific bill        |
| PUT    | `/api/bills/<id>/`        | Update a specific bill          |
| DELETE | `/api/bills/<id>/`        | Delete a specific bill          |
| POST   | `/api/bills/<bill_id>/pay/` | Mark a bill as paid            |

---

## Authentication

- **JWT Authentication**:
  - The application uses `djangorestframework-simplejwt` for token-based authentication.
  - Access and refresh tokens are issued upon login.

- **OTP Verification**:
  - OTPs are sent via email for account verification and password reset.

---

## Recurring Bills

- Recurring bills are automatically generated using Celery tasks.
- Supported frequencies:
  - Daily, Weekly, Bi-weekly, Monthly, Bi-monthly, Annually, Custom.

---

## Pagination

- API responses for bill listings are paginated using Django REST Framework's `PageNumberPagination`.
- Default page size: 10 items.
- Clients can customize the page size using the `page_size` query parameter.

---

## Email Notifications

- **Welcome Email**: Sent to users upon successful registration.
- **OTP Email**: Sent for account verification and password reset.
- **Password Reset Success Email**: Sent after a successful password reset.

---

## Deployment

### Using Gunicorn
1. Install Gunicorn:
   ```bash
   pip install gunicorn
   ```
2. Run the server:
   ```bash
   gunicorn bills-manager.wsgi:application --bind 0.0.0.0:8000
   ```

### Using Docker (Optional)
1. Build the Docker image:
   ```bash
   docker build -t bills-manager .
   ```
2. Run the container:
   ```bash
   docker run -p 8000:8000 bills-manager
   ```

---

## Contributing

Contributions are welcome! To contribute:

1. Fork the repository.
2. Create a new branch:
   ```bash
   git checkout -b feature-name
   ```
3. Commit your changes:
   ```bash
   git commit -m "Add feature-name"
   ```
4. Push to the branch:
   ```bash
   git push origin feature-name
   ```
5. Open a pull request.

---

## License

This project is licensed under the MIT License. See the `LICENSE` file for details.
