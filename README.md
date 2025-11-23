# 📚 Bookly - Book Review API

A REST API for managing books and reviews, built with FastAPI and following Clean Architecture principles.

## 🚀 Features

- **CRUD Operations** for books
- **RESTful API** design
- **Clean Architecture** implementation
- **Async support** with SQLModel
- **API documentation** with Swagger UI

## 📋 Requirements

- Python 3.11+
- Poetry (dependency management)
- PostgreSQL (or any SQL database)

## ⚙️ Setup

1. **Install dependencies:**
   ```bash
   poetry install
   ```

2. **Configure environment:**
   Create a `.env` file in the root directory:
   ```env
   DATABASE_URL=postgresql+asyncpg://user:password@localhost/bookly
   ```

3. **Run the application:**
   ```bash
   cd src
   poetry run uvicorn bookly:app --reload
   ```
   
   Or from the project root:
   ```bash
   poetry run uvicorn bookly:app --reload --app-dir src
   ```

4. **Access the API:**
   - API: `http://localhost:8000`
   - Swagger docs: `http://localhost:8000/docs`
   - ReDoc: `http://localhost:8000/redoc`

## 🏗️ Project Structure

```
bookly/
├── src/bookly/
│   ├── __init__.py          # FastAPI app initialization
│   ├── config.py            # Configuration settings
│   ├── db/
│   │   └── main.py          # Database engine setup
│   └── book/
│       ├── controllers.py   # API endpoints (Presentation layer)
│       ├── service.py       # Business logic (Application layer)
│       ├── models.py        # Domain models
│       └── sample_data.py   # Sample data for development
└── tests/                   # Test files
```

## 📡 API Endpoints

### Books

- `GET /api/v1/books` - Get all books
- `POST /api/v1/books` - Create a new book
- `GET /api/v1/books/{book_id}` - Get a book by ID
- `PATCH /api/v1/books/{book_id}` - Update a book
- `DELETE /api/v1/books/{book_id}` - Delete a book

## 🔧 Development

This project follows **Clean Architecture** principles:

- **Controllers** (Presentation): Handle HTTP requests/responses
- **Services** (Application): Contain business logic
- **Models** (Domain): Define data structures
- **Database** (Infrastructure): Data persistence layer

## 📝 License

MIT License - See LICENSE file for details

## 👤 Author

Richard Ayala
- GitHub: [@RichardAyalaFunes](https://github.com/RichardAyalaFunes)
- Email: ayala.funes06@gmail.com

