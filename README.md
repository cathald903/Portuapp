# Introduction
### What is this?
This app is a flask app that allows someone to spin up an instance that will give them the ability to subscribe to certain words in the database and subsequently be quizzed on them.

### Why Portuguese?
I am currently trying to learn the language and decided the best way to do that was to build this instead.

# How to use
The app uses Docker, Flask and MYSQL to spin up a service that can be connected to via localhost.
### Start the containers
`docker compose up --build -d db && sleep 10  && docker compose up --build flask`
Note: the docker yaml 'depends on' variable was not used because it was running into an issue where it would not wait for the db process to be spun up fully before starting the flask app, causing a failure

### Navigate to the webpage
`http://127.0.0.1:8000/login`
Click on the link to register an account and login. This will bring you to a plain webpage (frontend was not the focus of this project).

![image](https://github.com/user-attachments/assets/795970a4-30fa-440b-a8f7-f3b36c07a6cf)


### Get Quizzin
Navigate to the `Quiz` page and fill out the form to begin your quiz 

![image](https://github.com/user-attachments/assets/d0530688-1a1e-4c53-89b8-18e4ce8fde83)

Context here refers how some words refer to specific things in Portuguese that we would only have one word for in English, eg To play has Tocar and Jogar

The 'Conjugation' option refers to whether you want to be tested on the correct conjugation of the verbs you are quizzed on.
