# Logistics Microservice

A simplified Inventory & Order Management Service built with Python (FastAPI), PostgreSQL, and SQLAlchemy. This service manages products, orders, and stock levels.

## Prerequisites

* **Docker & Docker Compose**: For containerization and running the database/application.
* **uv**: For Python dependency management and running local tests.
* **Python 3.12+**: Required for running tests locally.

## Running the Application

1.  **Clone the repository:**
    ```bash
    git clone https://github.com/thilina98/inventory-management-system.git
    cd inventory-management-system
    ```

2.  **Start the services:**
    Run the following command to build the image and start the API and Database containers:
    ```bash
    docker-compose up --build -d
    ```

3.  **Apply Database Migrations:**
    run the migrations
    ```bash
    uv run alembic upgrade head
    ```

4.  **Access the Service:**
    * **API Root:** `http://localhost:8000`
    * **Health Check:** `http://localhost:8000/health`
    * **Interactive API Docs:** `http://localhost:8000/docs`

## Running Tests

The test suite is configured to connect to the test database container exposed on port `5433`.

1.  **Ensure Docker containers are running:**
    (The `db_test` service in `compose.yml` must be active).
    ```bash
    docker-compose up -d db_test
    ```

2.  **Run tests using `uv`:**
    ```bash
    uv run pytest
    ```

## Design Decisions & Trade-offs

### 1. Concurrency Handling & Data Integrity
* **Decision:** Implemented pessimistic locking (`SELECT ... FOR UPDATE`) within the order creation transaction.
* **Reasoning:** This prevents "double-spending" race conditions where concurrent requests could purchase the same stock item. It ensures `stock_quantity` never drops below zero, which is critical for inventory accuracy.

### 2. Layered Architecture
* **Decision:** The application is strictly divided into **API** (Routes), **Services** (Business Logic), and **Repositories** (Data Access).
* **Reasoning:** This separation of concerns ensures that business rules (like stock checks) are decoupled from the HTTP framework, making the code more maintainable and easier to test in isolation.

### 3. Trade-offs (Time Constraints)
* **Authentication:** Full OAuth2/JWT authentication was omitted to prioritize the robustness of the core transactional logic and database schema within the 4-6 hour timeframe.
* **Pagination:** Endpoints use basic offset-based pagination. For a high-scale production system, cursor-based pagination would be preferred to avoid performance degradation on large offsets.
* **Test Environment:** Tests currently run locally against a containerized DB. In a CI/CD pipeline, this would be wrapped in a dedicated test runner stage in Docker.
* **Logging:** Logging was omitted for the most part of this. But in a good api, there should be a good login service.



# next to be implemented
* implement errors
* logging
* rate limiting
* authentication