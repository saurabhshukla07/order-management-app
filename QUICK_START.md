# 🚀 Quick Start Guide

Get the Order Management API running in 5 minutes!

## ⚡ Quick Setup

### 1. Install PostgreSQL (if not installed)

**Windows:**
- Download from https://www.postgresql.org/download/windows/
- Run installer and remember your password

**macOS:**
```bash
brew install postgresql@14
brew services start postgresql@14
```

**Linux (Ubuntu/Debian):**
```bash
sudo apt update
sudo apt install postgresql postgresql-contrib
sudo systemctl start postgresql
```

### 2. Create Database

```bash
# Login to PostgreSQL
psql -U postgres

# Create database
CREATE DATABASE order_management;

# Exit
\q
```

### 3. Install Python Dependencies

```bash
# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install requirements
pip install -r requirements.txt
```

### 4. Configure Environment

```bash
# Copy example env file
cp .env.example .env

# Edit .env with your database credentials
# Change: postgresql://postgres:YOUR_PASSWORD@localhost:5432/order_management
```

### 5. Run the Application

```bash
python main.py
```

✅ API will be running at http://localhost:8000

## 📋 Test the API (Step by Step)

### Step 1: Register a User

```bash
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{
    "name": "John Doe",
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

### Step 2: Login

```bash
curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{
    "email": "john@example.com",
    "password": "securepass123"
  }'
```

**Save the access_token from response!**

### Step 3: Create an Order

Replace `YOUR_TOKEN` with the token from Step 2:

```bash
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer YOUR_TOKEN" \
  -H "Content-Type: application/json" \
  -d '{
    "product_name": "Laptop",
    "amount": 999.99
  }'
```

### Step 4: View Your Orders

```bash
curl -X GET http://localhost:8000/orders \
  -H "Authorization: Bearer YOUR_TOKEN"
```

### Step 5: Cancel an Order

Replace `1` with your order ID:

```bash
curl -X PATCH http://localhost:8000/orders/1/cancel \
  -H "Authorization: Bearer YOUR_TOKEN"
```

## 🌐 Use Swagger UI (Easier!)

1. Go to http://localhost:8000/docs
2. Click "Authorize" button
3. Enter: `Bearer YOUR_TOKEN`
4. Test all endpoints interactively!

## ⏰ Background Job Testing

1. Create several orders (they'll be `pending`)
2. Wait 2-3 minutes
3. Check orders again - they'll be `completed`
4. Watch the console logs for processing messages

## 🐛 Common Issues

### Database Connection Error
```
Error: connection to server failed
```
**Solution:** Ensure PostgreSQL is running and credentials in `.env` are correct

### Module Not Found Error
```
ModuleNotFoundError: No module named 'fastapi'
```
**Solution:** Activate virtual environment and install dependencies
```bash
source venv/bin/activate
pip install -r requirements.txt
```

### Token Expired Error
```
{"detail": "Invalid or expired token"}
```
**Solution:** Tokens expire in 15 minutes. Login again to get a new token.

### Port Already in Use
```
Error: [Errno 48] Address already in use
```
**Solution:** Change port in `.env` or kill process using port 8000
```bash
# Find process
lsof -i :8000
# Kill it
kill -9 <PID>
```

## 📊 Verify Everything Works

Run this complete test:

```bash
# 1. Health check
curl http://localhost:8000/

# 2. Register
curl -X POST http://localhost:8000/auth/register \
  -H "Content-Type: application/json" \
  -d '{"name":"Test User","email":"test@test.com","password":"test123456"}'

# 3. Login and save token
TOKEN=$(curl -X POST http://localhost:8000/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"test@test.com","password":"test123456"}' \
  | grep -o '"access_token":"[^"]*' | cut -d'"' -f4)

# 4. Create order
curl -X POST http://localhost:8000/orders \
  -H "Authorization: Bearer $TOKEN" \
  -H "Content-Type: application/json" \
  -d '{"product_name":"Test Product","amount":99.99}'

# 5. Get orders
curl -X GET http://localhost:8000/orders \
  -H "Authorization: Bearer $TOKEN"
```

If all commands succeed, you're good to go! 🎉

## 📝 Next Steps

1. Import `Postman_Collection.json` into Postman for easier testing
2. Check `README.md` for detailed documentation
3. View API docs at http://localhost:8000/docs
4. Review code comments to understand the implementation

## 💡 Tips

- Use Swagger UI for interactive testing
- Check console logs to see background job activity
- Create multiple orders to test background processing
- Try canceling orders in different states
- Test with invalid tokens to see error handling

---

Need help? Check the main README.md or review the code comments!