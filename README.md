# Asset Management API

A Flask-based REST API to manage **assets** with service and expiration timing, automatic notifications, and violations logging.

---

## 📆 Features

* Create, update, fetch, delete assets
* Track `service_time`, `expiration_time`, `last_serviced`
* Send notifications 15 minutes before service or expiration time
* Log violations if service or expiration is missed
* Swagger UI documentation at `/apidocs`
* SQLite as the database backend
* ⏱️ All timestamps must be provided in **UTC format only**

---

### 🛠️ Installation & Setup

#### 1. Clone the Repository

```bash
git clone https://github.com/Preet-Singhvi/Aroras-Clinic.git
```

#### 2. Create & Activate Virtual Environment

```bash
python -m venv venv
```

* **Windows:**

```bash
venv\Scripts\activate
```

* **Linux/macOS:**

```bash
source venv/bin/activate
```

#### 3. Install Dependencies

```bash
pip install -r requirements.txt
```

#### 4. Set Environment Variables

Create a `.env` file:

```env
FLASK_ENV=development
DATABASE_URL=sqlite:///assets.db
```

> Add `.env` to `.gitignore` and never commit it.

#### 5. Initialize Database

Ensure the `migrations/` folder exists.

```bash
flask db init
```

Then apply the migrations:

```bash
flask db migrate -m "initial"
flask db upgrade
```

#### 6. Run the App

```bash
python run.py
```

Visit: [http://localhost:5000/apidocs](http://localhost:5000/apidocs)

---

## 📃 API Endpoints

| Method | Endpoint         | Description                  |
| ------ | ---------------- | ---------------------------- |
| GET    | `/assets`        | List all assets              |
| POST   | `/assets`        | Create a new asset           |
| GET    | `/assets/<id>`   | Get asset details            |
| PUT    | `/assets/<id>`   | Update an asset              |
| DELETE | `/assets/<id>`   | Delete an asset              |
| POST   | `/run-checks`    | Trigger periodic asset check |
| GET    | `/notifications` | List all notifications       |
| GET    | `/violations`    | List all violations          |

---

## 🧰 Sample Asset Payload

```json
{
  "name": "Air Conditioner",
  "service_time": "2025-06-26T14:00:00",
  "expiration_time": "2025-06-30T14:00:00",
  "last_serviced": "2025-06-20T14:00:00"
}
```

> ⏱️ All times must be in **UTC format** (ISO 8601).

---

## 🌐 Trigger Checks Manually

Use the following endpoint to simulate periodic background checks:

```bash
curl -X POST http://localhost:5000/run-checks
```

This will:

* Create notifications for assets within 15 mins of service/expiration
* Log violations for overdue assets

---

## ✅ Response Format

All API responses follow a consistent structure:

```json
{
  "status": "success",
  "code": 200,
  "message": "Asset created",
  "data": { ... }
}
```

---

## 📁 Project Structure

```
.
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── routes.py
│   ├── schemas.py
│   ├── utils.py
│   ├── response_model.py
│   └── config.py
├── migrations/         <-- Make sure this folder exists
├── run.py
├── requirements.txt
├── .env.example
└── README.md
```

---

## 🚪 Best Practices

* `.env` should never be committed
* Use `response_model.py` for consistent API output
* Error handling included for DB and validation
* Swagger doc covers every endpoint with example schemas

---

