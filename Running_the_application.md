# Running the application

## Direct execution (best for local development)

**1. Make sure that the required MySQL instance is up and running!**

------------not using-------------
For example we might spawn a docker MySQL instance using:
`docker run --name my-mysql -e MYSQL_ROOT_PASSWORD=my-secret-pw -p 3306:3306`
------------not using--------------

**2. Clone the code and run the app**
pip install flask 

pipenv shell

pipenv install Pipfile


```bash
# Get the code
git clone https://github.com/hoyoul321/flask_website.git
cd intranet

# Virtualenv modules installation 
$ pipenv install

# Create and edit ./config/config.yaml, 
# use  ./config/config.yaml.example as reference
# Set DEBUG: True for development mode, DEBUG: False for deployment

# Upgrade the DB
$ pipenv run flask db upgrade

# Populate the DB with sample data
#$ pipenv run flask populate

# Start the application
$ pipenv run python ./app.py
# OR
$ pipenv run flask run --port=80

# Access the app in browser: http://127.0.0.1/
# Administrator account: admin@gmail.com, password: admin



