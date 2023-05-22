import firebase_admin
from firebase_admin import credentials, storage
from pathlib import Path

# Initialize Firebase app with credentials
# if not firebase_admin._apps:
#     save_folder = "key"
#     save_path = Path(save_folder, "admin.json")
#     cred = credentials.Certificate(save_path)
#     firebase_admin.initialize_app(cred)


# # Get a reference to the Firebase Storage bucket
# bucket = storage.bucket(
#     name="long-plexus-376814.appspot.com",
# )
