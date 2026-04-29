# Sync-EventBackendAPI 

A robust, production-ready backend application built with **FastAPI** for managing event registrations, user authentication, and automated reporting. This API is designed with a focus on security, role-based access control, and seamless deployment.

## ✨ Key Features

* **Secure Authentication:** Complete User Signup and Login flows utilizing OAuth2 with JWT (JSON Web Tokens) and bcrypt password hashing.
* **Role-Based Access Control (RBAC):** Tiered authorization supporting distinct user roles (e.g., standard users and a Master Admin) to secure protected routes.
* **Automated Email & Reporting:** Dynamically generates CSV reports of event data and emails them to designated admin email securely using SMTP and Google App Passwords.
* **Event Management:** Endpoints to handle user statuses, including a dynamic "Toggle Check-in" system.
* **Interactive Documentation:** Auto-generated, interactive API documentation using Swagger UI.
* **Robust Testing:** Integrated unit testing suite built with `pytest` and `httpx` to ensure API reliability.
* **Cloud Deployment:** Fully configured for CI/CD deployment on Render.

## 🛠️ Tech Stack

* **Framework:** FastAPI (Python)
* **Database:** SQLite (Lightweight, file-based database)
* **Data Validation:** Pydantic V2
* **Authentication:** JWT (PyJWT / python-jose), Passlib (bcrypt)
* **Testing:** Pytest
* **Environment Management:** python-dotenv

## ⚙️ Local Setup & Installation

Follow these steps to run the project locally on your machine.

**1. Clone the repository:**
```bash
git clone [https://github.com/Mukesh2806/Sync-EventBackendAPI.git](https://github.com/Mukesh2806/Sync-EventBackendAPI.git)
cd Sync-EventBackendAPI
2. Create and activate a virtual environment:

Bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
3. Install dependencies:

Bash
pip install -r requirements.txt
4. Set up Environment Variables:
Create a .env file in the root directory of the project and add the following variables:

Code snippet
SECRET_KEY=your_super_secret_key_here
ALGORITHM=HS256
ACCESS_TOKEN_EXPIRE_MINUTES=1440
SENDER_EMAIL=your_email@gmail.com
SENDER_PASSWORD=your_16_char_google_app_password
RECEIVER_EMAIL=recipient_email@example.com
MASTER_ADMIN_EMAIL=master@example.com
5. Run the server:

Bash
uvicorn app.main:app --reload
📖 API Documentation
FastAPI automatically generates interactive documentation. Once the server is running, you can test all endpoints directly from your browser:

Swagger UI: http://127.0.0.1:8000/docs

ReDoc: http://127.0.0.1:8000/redoc

Render live site: https://sync-eventbackendapi.onrender.com/

(Note: If viewing the live deployed version, append /docs to the Render URL).

🧪 Running Tests
This project includes a suite of unit tests to verify authentication and endpoint health. To run the tests, simply execute:

Bash
pytest
Acknowledgments & AI Leverage
Building software today is about combining problem-solving with the right tools. While the core architecture, database modeling, API design, and system logic were driven by my own understanding of backend engineering, I proudly utilized AI assistants (like ChatGPT/Gemini) to accelerate development and overcome roadblocks in the following specific areas:

Frontend Prototyping: Writing the foundational HTML syntax and specific JavaScript logic, particularly the fetch functions for API integration and the UI logic for the check-in toggle.

Backend Automation Scripts: Synthesizing the specific Python logic for the toggle_check_in route in main.py, as well as formatting the csv module integration and SMTP automated email dispatch logic.

Advanced Debugging: Acting as a pairing partner to help diagnose and resolve stubborn configuration errors that I could not immediately resolve on my own, such as environment variable loading issues, JWT algorithm fallbacks, and deployment merge conflicts.