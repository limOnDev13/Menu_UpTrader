# UpTrader test task
A test assignment from the UpTrader company.

---

## Setup and launch
To demonstrate how the application works, it is enough to assemble docker containers with 
the ```docker compose up --build``` command. To access the admin area, you will need to go into 
the container shell with the django application and create a superuser. 
To fill the database, you can upload a fixture /uptrader/menu_item_fixture.json or 
use ```python manage.py create_menu_items --count 10``` command.

If the application is running locally via docker (with nginx), 
then the application will work by url. http://127.0.0.1:8080/menu/<some kind of word>
___

## Technologies
- Django
- Postgres
- Docker
- Nginx
- unittest
