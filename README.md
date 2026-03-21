# AquaConnect 🐟

**AI-powered aquaculture management platform** for small and medium fish farmers.

## Features
- 🔐 **Authentication** – JWT-based login & registration
- 🏠 **Farm Dashboard** – Farm profiles, water quality overview, quick actions
- 🌊 **AI Water Quality Analysis** – pH, temperature, dissolved oxygen analysis with health scoring
- 📊 **Financial Planner** – Income/expense tracking, profitability reporting
- 💬 **Community Forum** – Knowledge sharing, expert Q&A
- 📡 **REST API** – JSON API for IoT sensor integration

## Tech Stack
- **Backend**: Flask (Python), SQLAlchemy ORM, Flask-JWT-Extended
- **Database**: SQLite (dev) / PostgreSQL (production)
- **Frontend**: Jinja2 templates + Vanilla CSS (responsive)
- **Deployment**: Docker + Docker Compose

---

## Quick Start (Local Development)

### 1. Create & activate virtual environment
```bash
python -m venv venv
# Windows:
venv\Scripts\activate
# Linux/macOS:
source venv/bin/activate
```

### 2. Install dependencies
```bash
pip install -r requirements.txt
```

### 3. Set up environment
```bash
copy .env.example .env   # Windows
cp .env.example .env     # Linux/macOS
# Edit .env with your settings
```

### 4. Run the app
```bash
python run.py
```

Open **http://localhost:5000**

---

## Docker Deployment (with PostgreSQL)

```bash
# Edit docker-compose.yml to set secure SECRET_KEY & JWT_SECRET_KEY
docker-compose up --build
```

Open **http://localhost:5000**

---

## API Endpoints

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/register` | Register new user |
| POST | `/api/auth/login` | Login, returns JWT token |
| GET | `/api/farms` | Get user's farms |
| POST | `/api/water-quality` | Analyze water quality |
| GET | `/api/water-quality/<farm_id>` | Get water history |
| GET | `/api/financial/summary/<farm_id>` | Financial summary |
| GET | `/api/forum/posts` | List forum posts |

---

## Project Structure
```
aquatech main/
├── app/
│   ├── __init__.py          # App factory + context processor
│   ├── models.py            # SQLAlchemy ORM models
│   ├── services.py          # AI analysis & financial services
│   ├── auth/                # Login, register, logout
│   ├── dashboard/           # Farm dashboard
│   ├── water_quality/       # Water quality analysis
│   ├── financial/           # Financial planner
│   ├── forum/               # Community forum
│   ├── api/                 # REST API (JSON)
│   ├── static/css/style.css # Global design system
│   └── templates/           # Jinja2 HTML templates
├── run.py                   # Entry point
├── requirements.txt
├── Dockerfile
└── docker-compose.yml
```
