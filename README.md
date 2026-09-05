FincapGuard

An AI-powered financial risk management and portfolio optimization system built with Python and Streamlit.

                         ┌──────────┐
                         │   USER   │
                         └────┬─────┘
                              │
                              ▼
                 ┌──────────────────────┐
                 │  STREAMLIT FRONTEND  │
                 │                      │
                 │ Dashboard            │
                 │ Portfolio Analysis   │
                 │ Risk Analysis        │
                 │ Analytics            │
                 └──────────┬───────────┘
                            │
             ┌──────────────┴──────────────┐
             │                             │
             ▼                             ▼
    ┌─────────────────┐          ┌──────────────────┐
    │ Firebase Auth   │          │ Python Backend   │
    │                 │          │                  │
    │ Login / Signup  │          │ FincapGuard      │
    └─────────────────┘          │ System           │
                                 └────────┬─────────┘
                                          │
                         ┌────────────────┼────────────────┐
                         │                │                │
                         ▼                ▼                ▼
                  ┌────────────┐  ┌──────────────┐  ┌─────────────┐
                  │Optimization│  │Crisis        │  │Feature      │
                  │Engine      │  │Prediction    │  │Engineering  │
                  └────────────┘  └──────┬───────┘  └──────┬──────┘
                                         │                 │
                                         ▼                 ▼
                                  ┌────────────┐     ┌─────────────┐
                                  │ ML Models  │     │ Market Data │
                                  └────────────┘     └─────────────┘
                                  

🚀 Getting Started

Follow the steps below to run FincapGuard on your local machine.

1. Prerequisites

Make sure the following are installed on your computer:

Python 3.10 or higher
Git
A modern web browser such as Chrome, Edge, or Firefox

You can check whether Python is installed by opening PowerShell / Command Prompt and running:

python --version

You should see something similar to:

Python 3.x.x
2. Clone the Repository

Open PowerShell or Command Prompt and clone the repository:

git clone <YOUR_GITHUB_REPOSITORY_URL>

Then move into the project directory:

cd Hackathon
3. Create a Virtual Environment

It is recommended to create a virtual environment so that the project's dependencies remain separate from your other Python projects.

Run:

python -m venv venv

Activate the virtual environment.

Windows
venv\Scripts\activate
macOS / Linux
source venv/bin/activate

After activation, you should see (venv) in your terminal.

4. Install Required Python Packages

Install all required dependencies using:

python -m pip install -r requirements.txt

If a requirements.txt file is not available, install the main dependencies manually:

python -m pip install streamlit pandas plotly scipy scikit-learn joblib python-dotenv firebase-admin
5. Configure Environment Variables

Some parts of the application may require API keys or configuration values.

Create a .env file in the project root:

Hackathon/
│
├── backend/
├── frontend/
├── .env
├── requirements.txt
└── README.md

Add the required environment variables to .env.

Example:

API_KEY=your_api_key_here

Important: Never upload your .env file or private API keys to GitHub.

Make sure .env is included in .gitignore.

6. Firebase Authentication Setup

FincapGuard uses Firebase for authentication.

Step 1 — Create a Firebase Project

Go to the Firebase Console and create a new project.

Enable:

Firebase Authentication
Email/Password authentication
Any other authentication provider required by the project
Step 2 — Configure Firebase Credentials

Create/download the Firebase service account credentials required by the Python backend.

Place the credentials in the location expected by the project.

For example:

Hackathon/
│
├── backend/
├── frontend/
├── firebase-service-account.json
├── .env
└── README.md

Security Warning: Never commit firebase-service-account.json to GitHub.

Add it to .gitignore:

.env
firebase-service-account.json
venv/
__pycache__/
▶️ Running the Application
7. Start the Streamlit Application

Make sure you are inside the project root or the appropriate frontend directory.

For the current project structure:

cd frontend

Then start Streamlit:

python -m streamlit run app.py
8. Open the Application in Your Browser

After running the command, Streamlit will display something similar to:

Local URL: http://localhost:8501

Open your browser and visit:

http://localhost:8501

The FincapGuard application should now be running.

🖥️ Using the Application

Once the application opens:

1. Authentication

Log in using the authentication method provided by the application.

2. Dashboard

After successful authentication, you can access the main dashboard.

3. Portfolio Analysis

Enter or select the required portfolio information to analyze the portfolio.

4. Risk Analysis

The system evaluates different risk factors using the implemented risk and machine-learning engines.

5. Optimization

The optimization engine generates portfolio allocation recommendations based on the configured constraints and risk parameters.

6. Analytics

Use the available charts and visualizations to understand:

Portfolio allocation
Asset classes
Risk levels
Market conditions
Optimization results
📁 Project Structure
Hackathon/
│
├── backend/
│   ├── main.py
│   ├── config.py
│   │
│   ├── engines/
│   │   └── optimization_engine.py
│   │
│   ├── ml/
│   │   ├── crisis_predictor.py
│   │   └── feature_engineering.py
│   │
│   └── services/
│       └── auth_service.py
│
├── frontend/
│   ├── app.py
│   │
│   ├── components/
│   │   └── charts.py
│   │
│   └── pages/
│       └── dashboard.py
│
├── .env
├── requirements.txt
├── .gitignore
└── README.md
🛠️ Technology Stack
Frontend
Python
Streamlit
Plotly
Backend
Python
SciPy
Pandas
Scikit-learn
Joblib
Machine Learning
Scikit-learn
Feature engineering
ML-based risk/crisis prediction
Authentication
Firebase Authentication
Firebase Admin SDK
❗ Troubleshooting
streamlit is not recognized

Instead of:

streamlit run app.py

use:

python -m streamlit run app.py
ModuleNotFoundError

For example:

ModuleNotFoundError: No module named 'pandas'

Install the missing package:

python -m pip install pandas

Or reinstall all project dependencies:

python -m pip install -r requirements.txt
Port Already in Use

If port 8501 is already being used, run Streamlit on another port:

python -m streamlit run app.py --server.port 8502

Then open:

http://localhost:8502
🛑 Stopping the Application

To stop the Streamlit application, press:

Ctrl + C

in the terminal where Streamlit is running.

🔐 Security

Do not commit sensitive files or credentials to GitHub.

Make sure the following are included in .gitignore:

.env
firebase-service-account.json
venv/
__pycache__/
*.pyc

Never publicly share:

API keys
Firebase service account credentials
Passwords
Secret tokens
Private configuration files
👥 Contributors

Developed as part of a hackathon project.

⭐ Support

If you find this project useful, consider giving the repository a ⭐ on GitHub.
