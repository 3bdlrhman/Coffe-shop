# Coffee Shop

Cafe for visitors to order drinks, show graphics representing the ratios of ingredients in each drink.
This application simply do CRUD operations.

also, These are a Role Based operations which means:
- Manager role: read, add, update or delete drinks
- Barista role: read the drinks and its recipe
- visitors role: these are available for public info( the available drinks ).

i  managed to do so using the JWT concept of Auth0 service
after singing in the user then get a token from Auth0 this token contains which permission is allowed for this user

Using this application you could:

1) Display graphics representing the ratios of ingredients in each drink.
2) Allow public users to view drink names and graphics.
3) Allow the shop baristas to see the recipe information.
4) Allow the shop managers to create new drinks and edit existing drinks.

## About the Stack

### Backend

The `./backend` directory contains a completed Flask server with SQLAlchemy module to interact with the data.

[View the README.md within ./backend for more details.](./backend/README.md)

### Frontend

The `./frontend` directory contains a complete Ionic frontend to consume the data from the Flask server. 

[View the README.md within ./frontend for more details.](./frontend/README.md)
