import os
from pathlib import Path
from dotenv import load_dotenv

'''
This file can be imported to allow API Key and Location handling.
The class is a super class, so no initialization is required. 
'''

class ApiHandler:
    def __init__():
        pass

    # API KEY FILES 
    @staticmethod
    def generateKeyFile():
        file_name = 'KeyStorage'
        env_path = Path(f'../Storage/{file_name}.env')
        if not env_path.exists():
            env_path.write_text('')
            print(f"{file_name}.env file created")
        else:
            print(f'{file_name}.env already exists.')

    @staticmethod
    def check_for_file():
        env_path = Path('../Storage/KeyStorage.env')
        return env_path.exists()
        
    @staticmethod
    def save_api_key(key):
        KEY_NAME = 'MY_API_KEY'
        FILE_NAME = 'KeyStorage'
        env_path = Path(f'../Storage/{FILE_NAME}.env')
        env_path.write_text(f"{KEY_NAME}={key}")

    @staticmethod
    def load_api_key():
        load_dotenv(dotenv_path="../Storage/KeyStorage.env")
        return os.getenv("MY_API_KEY", "")
    
    # Added by Jkurth for validation
    @staticmethod
    def validate_key(key: str) -> bool:
        # Replace this with API validation logic
        import requests
        try:
            url = f"https://weather.visualcrossing.com/VisualCrossingWebServices/rest/services/timeline/Houghton?key={key}"
            response = requests.get(url)
            return (response.status_code == 200)    # returns TRUE if status code is valid
        except Exception:
            return False
        
    # Added by Jkurth for validation
    @staticmethod
    def validate_location(url_path: str) -> bool:
        # Replace this with API validation logic
        import requests
        try:
            url = url_path
            response = requests.get(url)
            return (response.status_code == 200)    # returns TRUE if status code is valid
        except Exception:
            print('false')
            return False

    # added by Jkurth
    @staticmethod
    def grab_api_key(path: str = "../Storage/KeyStorage.env") -> str:
        try:
            with open(path, "r", encoding="utf-8") as f:
                for line in f:
                    if line.startswith("MY_API_KEY="):
                        return line.split("=", 1)[1].strip().strip('"').strip("'")
        except FileNotFoundError:
            pass
        return ""
