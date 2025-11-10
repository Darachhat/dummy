# CDC OSP Dummy Bank API
## Prerequisites

- Python 3.12 or higher
- [uv](https://docs.astral.sh/uv/) - Fast Python package installer and resolver (recommended)
- Or pip (traditional Python package manager)

## Installation

### Option 1: Using uv (Recommended)

1. Install uv if you haven't already:
```bash
curl -LsSf https://astral.sh/uv/install.sh | sh
```

2. Clone the repository:
```bash
git clone http://10.255.1.208/cdcosp/api/cdcosp_dummy_bank_api.git
cd cdcosp_dummy_bank_api
```

3. Install dependencies:
```bash
uv pip install -e .
```

### Option 2: Using pip

1. Clone the repository:
```bash
git clone http://10.255.1.208/cdcosp/api/cdcosp_dummy_bank_api.git
cd cdcosp_dummy_bank_api
```

2. Create a virtual environment:
```bash
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate
```

3. Install dependencies:
```bash
pip install -r requirements.txt
```

## Configuration

1. Copy the example environment file:
```bash
cp .env.example .env
```

2. Edit `.env` file with your configuration:
```bash
# Backend
DATABASE_URL=sqlite:///./dummybank.db
SECRET_KEY=your_secret_key_here
ACCESS_TOKEN_EXPIRE_MINUTES=1440
CORS_ORIGINS="http://localhost:3000"

# Debugging
DEBUG=True
USE_MOCK_OSP=false

# Real OSP (CDC) API - Configure these for production
OSP_BASE_URL=https://your-osp-api-url
OSP_AUTH=your_auth_token
OSP_PARTNER=your_partner_id
OSP_TIMEOUT=30

# Payment Settings
FEE_AMOUNT=10.00
USD_TO_KHR_RATE=4000
```

### Environment Variables Explained

- `DATABASE_URL` - SQLite database file path
- `SECRET_KEY` - Secret key for JWT token generation (change in production!)
- `ACCESS_TOKEN_EXPIRE_MINUTES` - JWT token expiration time (1440 = 24 hours)
- `CORS_ORIGINS` - Allowed CORS origins (comma-separated for multiple)
- `DEBUG` - Enable debug mode (set to `False` in production)
- `USE_MOCK_OSP` - Use mock OSP API for testing (`true`) or real API (`false`)
- `OSP_BASE_URL` - CDC OSP API base URL
- `OSP_AUTH` - CDC OSP authentication token
- `OSP_PARTNER` - CDC OSP partner identifier
- `OSP_TIMEOUT` - API request timeout in seconds
- `FEE_AMOUNT` - Transaction fee amount in USD
- `USD_TO_KHR_RATE` - Exchange rate from USD to KHR

## Running the Application

### Development Mode

Using uvicorn directly:
```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

Or using FastAPI CLI:
```bash
fastapi dev main.py
```

The API will be available at:
- API: http://localhost:8000
- Interactive API docs (Swagger): http://localhost:8000/docs
- Alternative API docs (ReDoc): http://localhost:8000/redoc

### Production Mode

```bash
fastapi run main.py --port 8000 --proxy-headers
```

Or with uvicorn workers:
```bash
uvicorn main:app --host 0.0.0.0 --port 8000 --workers 4
```

### Using Docker

Build the Docker image:
```bash
docker build -t cdcosp-dummy-bank-api .
```

Run the container:
```bash
docker run -d -p 8000:8000 \
  -e DATABASE_URL=sqlite:///./dummybank.db \
  -e SECRET_KEY=your_secret_key \
  -v $(pwd)/dummybank.db:/workspace/dummybank.db \
  cdcosp-dummy-bank-api
```