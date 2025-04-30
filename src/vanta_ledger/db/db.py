from databases import Database
# Update the import path if models.py is not in the same package
# For example, if models.py is in the parent directory:
# from ..models import DATABASE_URL

from models import DATABASE_URL  # Use this if models.py is in the same directory as db.py

database = Database(DATABASE_URL)
