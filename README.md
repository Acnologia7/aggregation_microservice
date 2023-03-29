# Product aggregator microservice (showcase)
## !Project has been modified just for showcase purpose, it is not functional at this moment for keeping third parties out of context, which are required for functionality!

## Project structure

```
.
├── app/
│   ├── __init__.py
│   ├── models.py
│   ├── schemas.py
│   ├── tasks.py
│   ├── views.py
│   ├── APIs/
│   │   └── applifting/
│   │       ├── __init__.py
│   │       └── applifting_api.py
│   ├── constants/
│   │   ├── __init__.py
│   │   └── http_status_codes.py
│   ├── logs/
│   │   ├── warrnings.log
│   │   ├── errors.log
│   │   └── critical.log
│   └── utils/
│       ├── __init__.py
│       └── wraps.py
├── tests/
│   ├── __init__.py
│   ├── conftest.py
│   ├── test_applifting_api.py
│   ├── test_tasks.py
│   └── test_views.py
├── .env
├── .gitignore
├── docker-compose.yml
├── Dockerfile
├── make_db.py
├── README.md
├── requirements.txt
└── run.py
```
## Setup
### Build
For usage with docker, just navigate into a root folder of project (where docker-compose and Dockerfile is located) and then run command: 
- `docker-compose up --build`

### Deletition for rebuilding/clean up
To delete docker containers with their volumes run command: 
- `docker-compose down -v`

### Runnig in testing mode
For running pytest for this application you have two options to do so:
- changing env variable in .env file `TESTING_MODE=1` from default 0 (otherwise tests will stay "locked"), then make sure that in Dockerfile is commented `ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]`and use `ENTRYPOINT [ "tail", "-f", "/dev/null" ]` to run app container continuosly so we can enter it for runing tests with pytest.

- Find app conteiner with `docker ps` then enter it wiht `docker exec it <docker-image-id> bash`
- run `pytest` command (if not setting up `TESTING_MODE=1` from inside which you should probably) you can always check envs by command `env`

## !!! Caution !!!
- If you wish to run pytest then you should do it before you start app normally (due to one db), I found some issues with connection to my second testing db between dockers so for now it is only one db.

- maybe it will be needed to rerun app container if there is an db connection error (should not be case in run for testing)

### Running in classic mode
- Make sure that `TESTING_MODE=0` 
- Make sure that `ENTRYPOINT ["flask", "run", "--host=0.0.0.0"]` is uncommented and  `ENTRYPOINT [ "tail", "-f", "/dev/null" ]` commented
- Save Rerun/rebuild docker images
- Use any app for requests (was tested with Postman)
- if everything is running you should see flask app msg in terminal then app should run on localhost(127.0.0.1:5000) ip adress

### Manual way
- remove Dockerfile
- create venv in root directory of project and activate
- make sure you install all requirements
- comment application part in docker-compose and left only db container, run `docker-compose up --build`
- then run `flask run` or `flask run --host="0.0.0.0"`
- for changing `TESTING_MODE` for pytests or normal run update .env file


## Routes
(Postman guide only)

### /auth (POST)
- basic login for this api
- for obtaining login token choose basic auth, insert your username and password (PASSWORD123) -> you can check it in .env file by variable `PASSWORD_TO_API` you can change it to your liking
- in response you will optain token which copy and paste in postman bearer authorization with every next request, token is valid for 30 mins

#### Response:
- 200 - OK
- 401 - Could not verify - wrong password
- 400 - Bad request - token is missing
- 403 - Forbidden - token is not valid

### /products (GET)
- return all products from db

        Response:
        - 200 - OK
        [
            {
                id: string(UUID),
                name: string,
                description: string,
            }
        ]
        - 404 - Not found

### /product (POST)
- pre-create one specific product, checks if is valid to unique name and id, if so then registers it and get offers for it, then if everyting is successful save it in db. 

#### Body (application/json):
- name : string
- description : string

        Response:
        - 201 -
        {
            product_id: string(UUID),
            name: string
            description: string
        }
        - 500 - Internal server, if there was issue due to process of registration or getting offers
        - 400 - Bad request - if product already exists

### /product (GET)
#### Body (application/json):
- product_id: string(UUID)
        
        Response:
        - 200 - OK
        {
            product_id: string(UUID),
            name: string
            description: string
        }
        - 404 - Not found
        - 400 - Bad request


### /product (PUT)
#### Body (application/json):
- product_id: string(UUID)
- name: string (updated)
- description: string (updated)
- ! If left empty, it will update with empty !

        Response:
        - 200 - OK
        {
            product_id: string(UUID),
            name: string (updated)
            description: string (updated)
        }
        - 404 - Not found
        - 400 - Bad request

### /product (DELETE)
#### Body (application/json):
- product_id: string(UUID)

        Response:
        - 200 - OK
        - 404 - Not Found
        - 400 - Bad request

### /product/offers (GET)
#### Body (application/json):
- product_id: string(UUID)

        Response:
        - 200 - OK
        [
            {
                offer_id: string(UUID),
                items_in_stock: int
                price: int
            }
        ]
        - 404 - Not Found
        - 400 - Bad request

### /offer (GET)
#### Body (application/json):
- offer_id: string(UUID)

        Response:
        - 200 - OK
        {
            offer_id: string(UUID),
            items_in_stock: int,
            price: int,
            product.description: string,
            product.name: string
        }
        - 404 - Not found
        - 400 - Bad request


## Util docker app (PgAdmin-optional):
If you prefer to check database in web ui, you can uncomment pgadmin docker part with its volume and build it together with app and db container

- ip adress should be localhost:5050
- user: admin@email.com
- password: admin

- then in ui right click on server -> register -> name your server to your liking
- in conncetions write name of docker of database (postgres-dev in our case)
- username: admin
- password: admin
- save

- then if everything ok, you can click on server - > (your given name name) - > schemas -> tables

- then you right click on table -> query tool -> there you can write sql queries and see records

## Util script (make_db.py-optional)
- For creation db tables manualy if needed (run via python from inside docker or your terminal)

## Logs
- If needed there are log files that are generated at start of app in log directory (warnings, errors, critical)
