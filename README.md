# Mutual Fund Brokerage Backend API

A FastAPI-based backend application for a mutual fund brokerage platform with RapidAPI integration for real-time NAV data.

## Features

- 🔐 **User Authentication**: JWT-based authentication with registration and login
- 💰 **Fund Management**: Integration with RapidAPI to fetch mutual fund data
- 📊 **Portfolio Tracking**: Real-time portfolio valuation with hourly updates
- 🏦 **Fund Families**: Support for multiple fund families and open-ended schemes
- 🔄 **Auto Updates**: Background task for automatic portfolio value updates
- 🧪 **Testing**: Comprehensive E2E test suite
- 📚 **Documentation**: Auto-generated API documentation with Swagger UI


## Setup Instructions

### Prerequisites

- Python 3.12+
- pip (Python package manager)
- Git

### 1. Clone the Repository

```bash
git clone https://github.com/Hemanth63052/mutual-fund-backend
cd mutual-fund-backend
```

### 2. Create Virtual Environment

```bash
# Create virtual environment
python -m venv venv

# Activate virtual environment
# On Windows:
venv\Scripts\activate
# On macOS/Linux:
source venv/bin/activate
```

### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

### 4. Environment Configuration

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env file with your configuration
```

**Required environment variables:**

```env
SECRET_KEY=your-super-secret-jwt-key-change-in-production
RAPIDAPI_KEY=your-rapidapi-key-here
DATABASE_URL=sqlite:///./mutual_fund_app.db
```

### 5. Get RapidAPI Key

1. Sign up at [RapidAPI](https://rapidapi.com/)
2. Subscribe to the [Latest Mutual Fund NAV API](https://rapidapi.com/suneetk92/api/latest-mutual-fund-nav)
3. Copy your API key to the `.env` file

### 6. Initialize Database

```bash
python init_db.py
```

### 7. Run the Application

```bash
# Development server
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# Production server
uvicorn main:app --host 0.0.0.0 --port 8000
```

### 8. Access the Application

- **API Documentation**: http://localhost:8000/docs
- **Alternative Docs**: http://localhost:8000/redoc
- **Health Check**: http://localhost:8000/api/health

## API Endpoints

### Authentication

- `POST /api/auth/register` - Register new user
- `POST /api/auth/login` - User login
- `GET /api/me` - Get current user info (protected)

### Fund Management

- `GET /api/fund-families` - Get available fund families
- `GET /api/fund-families/{family_name}/schemes` - Get open-ended schemes for family

### Portfolio Management

- `GET /api/portfolio` - Get user portfolio (protected)
- `POST /api/investments` - Create new investment (protected)
- `PUT /api/portfolio/refresh` - Manually refresh portfolio values (protected)

### System

- `GET /api/health` - Health check endpoint

## Testing

### Run Tests

```bash
# Install test dependencies (if not already installed)
pip install pytest pytest-asyncio

# Run all tests
pytest test_main.py -v

# Run specific test class
pytest test_main.py::TestAuthentication -v

# Run with coverage
pip install pytest-cov
pytest test_main.py --cov=main --cov-report=html
```

## Background Tasks

The application includes an automatic portfolio update system that:

- Runs every hour
- Fetches current NAV for all investments
- Updates portfolio values in real-time
- Handles API failures gracefully with retry logic

## Security Features

- **Password Hashing**: Bcrypt for secure password storage
- **JWT Authentication**: Stateless authentication with configurable expiration
- **CORS Support**: Configurable cross-origin resource sharing
- **Input Validation**: Pydantic models for request validation
- **Error Handling**: Comprehensive error responses

## Production Deployment

### Environment Variables for Production

```env
SECRET_KEY=generate-a-strong-secret-key-for-jwt
RAPIDAPI_KEY=your-production-rapidapi-key
DATABASE_URL=postgresql://username:password@localhost:5432/mutual_fund_db
```

### Database Migration

For production, use PostgreSQL:

```bash
# Install PostgreSQL driver
pip install psycopg2-binary

# Set DATABASE_URL to PostgreSQL
export SQL_URL=postgresql://username:password@localhost:5432/mutual_fund_db

# Initialize database
python init_db.py
```

### Docker Deployment (Optional)

Create `Dockerfile`:

```dockerfile
FROM python:3.12

WORKDIR /app

COPY requirements.txt .
RUN pip install -r requirements.txt

COPY . .

EXPOSE 8000

CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
```

Build and run:

```bash
docker build -t mutual-fund-api .
docker run -p 8000:8000 --env-file .env mutual-fund-api
```

## API Usage Examples

### Register User

```bash
curl -X POST "http://localhost:8000/api/auth/register" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Login

```bash
curl -X POST "http://localhost:8000/api/auth/login" \
  -H "Content-Type: application/json" \
  -d '{
    "email": "user@example.com",
    "password": "securepass123"
  }'
```

### Get Portfolio

```bash
curl -X GET "http://localhost:8000/api/portfolio" \
  -H "Authorization: Bearer YOUR_JWT_TOKEN"
```

## Troubleshooting

### Common Issues

1. **"RapidAPI key not configured"**
   - Ensure `RAPIDAPI_KEY` is set in your `.env` file
   - Verify you have an active subscription to the API

2. **Database connection errors**
   - Check `SQL_URL` in `.env` file
   - For SQLite, ensure the directory is writable
   - For PostgreSQL, verify connection parameters

3. **Import errors**
   - Ensure virtual environment is activated
   - Install all requirements: `pip install -r requirements.txt`

4. **JWT token errors**
   - Ensure `SECRET_KEY` is set in `.env` file
   - Use a strong, unique secret key for production

### Development Tips

- Use the Swagger UI at `/docs` for interactive API testing
- Monitor logs for background task status
- Test with different fund families available in the API
- Use the `/api/health` endpoint to verify system status

## Contributing

1. Fork the repository
2. Create a feature branch: `git checkout -b feature-name`
3. Make your changes and add tests
4. Run tests: `pytest test_main.py -v`
5. Commit your changes: `git commit -am 'Add feature'`
6. Push to the branch: `git push origin feature-name`
7. Submit a pull request

## Support

For issues and questions:
- Check the API documentation at `/docs`
- Review the troubleshooting section above
- Create an issue in the repository
