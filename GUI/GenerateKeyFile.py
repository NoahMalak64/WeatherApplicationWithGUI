from pathlib import Path

#Create the .env file to persitently store the API key after program shutdown
file_name = 'KeyStorage'
env_path = Path(f'../Storage/{file_name}.env')
if not env_path.exists():
    env_path.write_text('')
    print(f"{file_name}.env file created")
else:
    print(f'{file_name}.env already exists.')