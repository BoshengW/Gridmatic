# Gridmatic
NOAA + NYISO Data Pipeline

## Setting Up Procedure:
- Python Env - Python 3.8
- Create and activate virtual env in your local 
- Install all dependency by **pip3 install -r requirements.txt**
- Add **.flaskenv** inside fetch folder with below detail
```
# .flaskenv use for saving some
DEBUG=True
FLASK_ENV="development"
LOG_LEVEL="debug"
SECRET_KEY="not-so-secret"

## for FLASK_APP env need to use absolute module name inside package
FLASK_APP="restapi.app:create_app()"
``` 
- Then ready to go enjoy
