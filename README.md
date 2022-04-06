# flask-blog-site
A Simple Blog Website created using Flask.

## Steps to run the app

 - Create a virtual environment 

       python -m venv venv
 - Install the required python dependencies as mentioned in **requirements.txt**
         
       pip install -r requirements.txt
       

 - Add the following environment variables in **venv\Scripts\activate.bat**
   - EMAIL_FLASK_USER  
   - EMAIL_FLASK_PASS 
   - SECRET_KEY
   - SQLALCHEMY_DATABASE_URI
  
   Set the appropriate values of these variables and then, **you are good to go !**

 - Finally, activate your virtual environment...	 

	   venv\Scripts\activate.bat

 - Run your flask server by executing the file: **run.py**
 
       python run.py
