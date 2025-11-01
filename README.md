# 🛒 Order Management API

A FastAPI-based backend system for managing orders with JWT authentication and background job processing.

## 📋 Features

- ✅ User registration and JWT authentication
- ✅ Create, list, and cancel orders
- ✅ Background job processing (every 2 minutes)
- ✅ PostgreSQL database with proper indexing
- ✅ Comprehensive error handling and logging
- ✅ Token expiration (15 minutes)
- ✅ Password hashing with bcrypt

## 🛠️ Tech Stack

- **Framework**: FastAPI
- **Database**: PostgreSQL
- **Authentication**: JWT (python-jose)
- **Password Hashing**: bcrypt (passlib)
- **Background Jobs**: APScheduler
- **ORM**: SQLAlchemy
- **Python Version**: 3.13.9

## 📁 Project Structure

```
order-management-api/
├── main.py                 # Application entry point
├── routes.py               # API endpoints
├── models.py               # Database models
├── database.py             # Database configuration
├── auth.py                 # Authentication utilities
├── schemas.py              # Pydantic schemas
├── background_jobs.py      # Background job scheduler
├── requirements.txt        # Python dependencies
├── .env.example            # Environment variables template
└── README.md              # Documentation
```

## 🚀 Setup Instructions

### 1. Prerequisites

- Python 3.13.9
- PostgreSQL installed and running
- pip package manager

### 2. Install Dependencies

```bash
# Create virtual environment (recommended)
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

### 3. Database Setup

Create a PostgreSQL database:

```sql
CREATE DATABASE order_management;
```

### 4. Environment Configuration

Copy `.env.example` to `.env` and configure:

```bash
cp .env.example .env
```

Edit `.env` with your database credentials:

```env
DATABASE_URL=postgresql://your_username:your_password@localhost:5432/order_management
SECRET_KEY=your-super-secret-key-change-this
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=15
APP_HOST=0.0.0.0
APP_PORT=8000
```

### 5. Run the Application

```bash
python main.py
```

Or using uvicorn directly:

```bash
uvicorn main:app --reload
```

The API will be available at: `http://localhost:8000`

## 📚 API Documentation

Once running, visit:
- **Swagger UI**: http://localhost:8000/docs
- **ReDoc**: http://localhost:8000/redoc

## 🔌 API Endpoints

### Authentication

#### Register User
```bash
POST /auth/register
Content-Type: application/json

{
  "name": "John Doe",
  "email": "john@example.com",
  "password": "securepass123"
}
```

#### Login
```bash
POST /auth/login
Content-Type: application/json

{
  "email": "john@example.com",
  "password": "securepass123"
}

Response:
{
  "access_token": "eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9...",
  "token_type": "bearer",
  "expires_in": 15
}
```

### Orders (Requires Authentication)

#### Create Order
```bash
POST /orders
Authorization: Bearer <your_token>
Content-Type: application/json

{
  "product_name": "Laptop",
  "amount": 999.99
}
```

#### Get All Orders
```bash
GET /orders
Authorization: Bearer <your_token>
```

#### Cancel Order
```bash
PATCH /orders/{order_id}/cancel
Authorization: Bearer <your_token>
```

## 📝 cURL Examples

### Register
```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"John Doe","email":"john@example.com","password":"securepass123"}'
```

### Login
```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"john@example.com","password":"securepass123"}'
```

### Create Order
```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE" \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Laptop","amount":999.99}'
```

### Get Orders
```bash
curl -X GET http://localhost:8000/orders \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

### Cancel Order
```bash
curl -X PATCH http://localhost:8000/orders/1/cancel \
  -H "Authorization: Bearer YOUR_TOKEN_HERE"
```

## 🗄️ Database Schema

### Users Table
```sql
CREATE TABLE users (
    id SERIAL PRIMARY KEY,
    name VARCHAR(100) NOT NULL,
    email VARCHAR(100) UNIQUE NOT NULL,
    password_hash VARCHAR(255) NOT NULL,
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);
```

### Orders Table
```sql
CREATE TABLE orders (
    id SERIAL PRIMARY KEY,
    user_id INTEGER NOT NULL REFERENCES users(id),
    product_name VARCHAR(200) NOT NULL,
    amount FLOAT NOT NULL,
    status VARCHAR(20) NOT NULL DEFAULT 'pending',
    created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Indexes
CREATE INDEX idx_orders_user_id ON orders(user_id);
CREATE INDEX idx_orders_status ON orders(status);
CREATE INDEX idx_orders_created_at ON orders(created_at);
```

## ⚙️ Background Job Processing

The background job runs every **2 minutes** and:
1. Finds all orders with `pending` status
2. Updates them to `processing`
3. Updates them to `completed`
4. Logs all processing activities

To change the interval, edit `background_jobs.py`:
```python
# For 3 minutes
scheduler.add_job(process_pending_orders, 'interval', seconds=180)
```

## 🔒 Security Features

- ✅ Password hashing with bcrypt
- ✅ JWT token-based authentication
- ✅ Token expiration (15 minutes)
- ✅ Protected endpoints with bearer token
- ✅ User can only access their own orders

## ⚠️ Error Handling

The API returns appropriate HTTP status codes:

- `200 OK` - Successful request
- `201 Created` - Resource created successfully
- `400 Bad Request` - Validation error
- `401 Unauthorized` - Invalid or missing token
- `403 Forbidden` - Insufficient permissions
- `404 Not Found` - Resource not found
- `500 Internal Server Error` - Server error

## 📊 Design Decisions

### Why FastAPI?
- Modern, fast framework with automatic API documentation
- Built-in data validation with Pydantic
- Excellent performance and async support

### Why SQLAlchemy?
- Robust ORM with excellent PostgreSQL support
- Type safety and migration support
- Clean abstraction over database operations

### Why APScheduler?
- Simple background job scheduling
- No external dependencies (Redis/RabbitMQ)
- Perfect for small to medium-scale applications

### Why JWT?
- Stateless authentication
- Scalable across multiple servers
- Industry-standard security

## 🧪 Testing

Test the API using:
1. **Swagger UI**: http://localhost:8000/docs (interactive testing)
2. **Postman**: Import the cURL commands
3. **Python requests**: Write integration tests

## 📦 Deployment Considerations

For production:
1. Change `SECRET_KEY` to a strong random value
2. Set `reload=False` in uvicorn
3. Use a production WSGI server (gunicorn + uvicorn workers)
4. Enable HTTPS
5. Set up proper logging and monitoring
6. Use environment-specific configuration
7. Set up database migrations with Alembic

## 🐛 Troubleshooting

### Database Connection Error
- Verify PostgreSQL is running
- Check DATABASE_URL in `.env`
- Ensure database exists

### Token Expired Error
- Tokens expire in 15 minutes
- Login again to get a new token

### Import Errors
- Ensure all dependencies are installed: `pip install -r requirements.txt`
- Activate virtual environment

## 📄 License

This project is for technical assessment purposes.

## 👨‍💻 Author

Created as part of Backend Developer Technical Test

---

**Note**: This is a development setup. For production, implement additional security measures, error handling, and monitoring.