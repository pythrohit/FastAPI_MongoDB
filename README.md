# FastAPI & MongoDB API

This is a small API application built with **FastAPI** and **MongoDB**, providing user authentication and blog management.

## Features

### User Authentication
- Register new users
- Login with JWT authentication
- Secure routes with authentication

### Blog Management
- Create, update, delete blog posts
- Fetch user-specific blogs
- Public access to view blogs

## Technologies Used
- **Backend**: FastAPI
- **Database**: MongoDB (via Motor)
- **Authentication**: JWT (JSON Web Token)
- **Environment Management**: dotenv

## Installation & Setup

### Prerequisites
- Python 3.8+
- MongoDB instance (local or cloud)

### Steps to Run

1. **Clone the Repository**
   ```bash
   git clone https://github.com/pythrohit/FastAPI_MongoDB.git
   cd fastapi-mongodb-api
   ```

2. **Create a Virtual Environment**
   ```bash
   python -m venv venv
   source venv/bin/activate  # On Windows use `venv\Scripts\activate`
   ```

3. **Install Dependencies**
   ```bash
   pip install -r requirements.txt
   ```

4. **Set Environment Variables**
   Create a `.env` file and add:
   ```ini
   MONGO_URI=mongodb://localhost:27017/your_db_name
   SECRET_KEY=your_secret_key
   ```

5. **Run the Server**
   ```bash
   uvicorn main:app --reload
   ```


