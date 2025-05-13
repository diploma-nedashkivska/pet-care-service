1. Clone the repository:
```
git clone https://github.com/diploma-nedashkivska/pet-care-service.git
cd pet-care-service
```

2. Create a virtual environment:
```
python -m venv venv
venv\Scripts\activate
```
3. Upgrade pip (optional but recommended):
```
python -m pip install --upgrade pip 
```

4. Install dependencies:
```
pip install -r requirements.txt
```

5. Start database services:
```
cd docker
docker compose up
```

6. Run migrations:
```
python manage.py migrate
```

7. Start the Django server:
```
python manage.py runserver
```