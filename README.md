# Savannah Assessment

> Main Repository for Backend Web App and API for savannah assessment

1. [Requirements](#requirements)
2. [Setup](#setup)
3. [Usage](#usage)
4. [Development](#development)

## Requirements

1. Python 3.9+ installed
2. Text editor such as [vs code](https://code.visualstudio.com/) or sublime text
3. Git - preferrably use terminal like [gitbash](https://gitforwindows.org/)

## Setup

1. Clone this repository.

```
git clone https://github.com/robinmuhia/savannahAssessment.git

```

2.  Change directory to the location of this repository.
3.  Create a `.env` file using the included `.env.example` as an example.
4.  Generate two secret keys for your app and paste into the JWT_SECRET_KEY and SESSION_SECRET_KEY section of .env file,
    you can generate the key from [here](https://djecrety.ir/)
5.  You will need to create a google app and retreive the google client id and google secret key. To get more information about setup,
    read this [article](https://www.balbooa.com/gridbox-documentation/how-to-get-google-client-id-and-client-secret). Note that in your authorized javascript origins, fill in https:127.0.0.1 and in the authorized redirect uris, fill in https://127.0.0.1:8000/token
6.  Install mkcert as we need an ssl certificate to run this locally. Find more about mkcert installation [here]
    (https://github.com/FiloSottile/mkcert)
7.  Set up a database in pg-admin locally
8.  Create and start your preferred Python virtual environment. For
    more information on how to set up a virtual environment, check the instructions on [this link](https://tutorial.djangogirls.org/en/django_installation/). Install the required libraries by running the commands below

            pip install -r requirements.txt

9.  After installation, run the following commands:

            alembic upgrade head
            mkcert -install  127.0.0.1

10. A local migration will be made creating a database and two .pem files will be created in your folder.
11. For details of how to get started with fastapi, check out [this link](https://fastapi.tiangolo.com/)
12. In order to work with a virtual environment, check out [this link](https://tutorial.djangogirls.org/en/installation/#pythonanywhere)

## Usage

To run locally:

     uvicorn app.main:app --host 127.0.0.1 --port 8000 --ssl-keyfile ./127.0.0.1-key.pem --ssl-certfile ./127.0.0.1.pem --reload

## Development

Pull the latest main version:

    git pull origin main

Create local development branch and switch to it:

    git branch {feature_branch_name}
    git checkout {feature_branch_name}

Make desired changes then commit the branch.

    git add .
    git commit -m "changes to{feature_branch_name}"
    git push origin {feature_branch_name}
