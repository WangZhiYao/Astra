# Astra API

Astra is a robust FastAPI-based backend application designed to manage various aspects of digital appearances,
platforms, user transactions, and watchlists. It provides a comprehensive set of APIs for authentication, managing
appearance data, tracking user purchases and sales, and enabling users to create and manage watchlists for items of
interest.

> [!NOTE]
> This application is currently under active development, and some features may not be fully
> implemented.

## Features

* **User Authentication**: Secure user registration, login, and token refresh using JWT.
* **Appearance Management**: APIs for creating and managing digital appearances, appearance types, and aliases.
* **Platform Management**: APIs for managing different platforms.
* **User Transaction Tracking**: Record and manage user purchase and sale transactions for appearances.
* **Watchlist Functionality**: Users can create watchlists and add/remove specific appearance items to track.
* **User Portfolio Management**: Users can view their portfolio of appearances, including quantity, average cost, total investment, current market value, and profit/loss.
* **User Portfolio Statistics**: Users can view their portfolio statistics, including total investment, current market value, and estimated and realized profit/loss.
* **Admin Privileges**: Role-based access control for administrative operations.
* **Redis Integration**: Used for caching and managing login attempt limits.
* **PostgreSQL Database**: Persistent storage for all application data.

## Technologies Used

* **Backend**: Python 3.13, FastAPI
* **Database**: PostgreSQL
* **ORM**: SQLAlchemy
* **Caching/Messaging**: Redis
* **Authentication**: JWT (JSON Web Tokens)
* **Password Hashing**: Passlib (Bcrypt)
* **ASGI Server**: Uvicorn
* **Dependency Management**: `pip` (via `requirements.txt`)

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for development and testing
purposes.

### Prerequisites

* [Docker](https://www.docker.com/get-started) (recommended for database and Redis setup)
* [Python 3.13](https://www.python.org/downloads/)
* `pip` (Python package installer)

### 1. Clone the Repository

```bash
git clone https://github.com/WangZhiYao/Astra.git
cd Astra
```

### 2. Environment Variables

Create a `.env` file in the root directory of the project by copying `.env.example` and filling in the necessary
details.

```bash
cp .env.example .env
```

Edit the `.env` file:

```ini
# PostgreSQL
POSTGRES_URL = "postgresql://user:password@localhost:5432/astra"

# Redis
REDIS_HOST = localhost
REDIS_PORT = 6379

# JWT
JWT_SECRET_KEY = your_super_secret_key_replace_this_with_a_strong_random_string
JWT_ALGORITHM = HS256
ACCESS_TOKEN_EXPIRE_MINUTES = 30
REFRESH_TOKEN_EXPIRE_DAYS = 7

# Login Attempts
MAX_LOGIN_ATTEMPTS = 3
LOGIN_ATTEMPT_WINDOW_MINUTES = 30
```

> [!NOTE]
> Replace `your_super_secret_key_replace_this_with_a_strong_random_string` with a strong, randomly generated key for
> production environments.

### 3. Install Python Dependencies

```bash
pip install -r requirements.txt
```

### 4. Initialize the Database Schema

The database schema is defined in `sql/schema.sql`. You'll need to apply this to your PostgreSQL database. You can use
`psql` or any PostgreSQL client.

Example using `psql` (make sure PostgreSQL is running via Docker Compose):

```bash
# Connect to your PostgreSQL database
psql -h localhost -p 5432 -U user -d astra

# Once connected, run the schema file
\i sql/schema.sql

# Exit psql
\q
```

> [!NOTE]
> Replace `localhost`, `5432`, `user`, `astra` with your actual database connection details if they differ from `.env`.

### 5. Run the Application

```bash
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

The `--reload` flag is useful for development as it automatically reloads the server on code changes. For production,
you would typically omit this.

The API will be accessible at `http://localhost:8000`. You can access the interactive API documentation (Swagger UI) at
`http://localhost:8000/docs`.

## API Endpoints

The main API endpoints are organized as follows:

* `/auth`: User registration, login, and token refresh.
* `/me/stats`: Get user statistics.
* `/me/portfolio`: Get user portfolio.
* `/appearances`: Manage appearances.
* `/appearance-types`: Manage appearance types.
* `/appearance-aliases`: Manage appearance aliases.
* `/platforms`: Manage platforms.
* `/platform-price-histories`: Manage platform price histories.
* `/user-purchase-transactions`: Record user purchase transactions.
* `/user-sale-transactions`: Record user sale transactions.
* `/watchlists`: Manage user watchlists.
* `/watchlists/{watchlist_id}/items`: Manage items within watchlists.

Refer to the interactive API documentation at `/docs` for detailed endpoint information, request/response schemas, and
try-it-out functionality.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

## License

```text
Copyright 2025 WangZhiYao

Licensed under the Apache License, Version 2.0 (the "License");
you may not use this file except in compliance with the License.
You may obtain a copy of the License at

    http://www.apache.org/licenses/LICENSE-2.0

Unless required by applicable law or agreed to in writing, software
distributed under the License is distributed on an "AS IS" BASIS,
WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
See the License for the specific language governing permissions and
limitations under the License.
```