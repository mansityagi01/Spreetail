import sys
import os

# Add the backend folder to the Python path so imports work properly
sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'backend'))

# Import the FastAPI app
from app.main import app
