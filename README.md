# FULL-FEATURED-BACKEND-APPLICATION
Full Featured Backend Application, using FastAPI, SQLAlchemy and PostgreSQL. Performing user Authentication and Authorization using JWT along with Google Oauth 2.0 and integration with Zoom API for scheduling virtual meetings.

The idea of this project came out of the need of a company that offers different services (web development, mobile development, marketing support, accounting support, etc,) to give extra information to those users interested in acquiring their services. 

In order to avoid face-to-face attendance, I implemented a virtual meeting system using Zoom API to generate zoom meeting links. The meetings are supposed to be attended by virtual assitants on the day and time set by the user. 

# GETTING STARTED
Here are the steps to follow so that you can test this REST-API on your local machine.

- Make sure you have **Docker** and **Docker Compose** installed in your PC if you are using Windows OS, make sure you have **Docker Desktop** installed.
    - You can download Docker Desktop by clicking [here.](https://www.docker.com/products/docker-desktop/)

- Go to your terminal and make a git clone of this repository. 
```
git clone https://github.com/NogueraMateo/FULL-FEATURED-BACKEND-APPLICATION.git
```

## Setting up the Google Cloud Console project

- In order to assure that Google Oauth works as expected, you'll need to configure a project in [Google Cloud Console](https://console.cloud.google.com/welcome/new?_ga=2.117443785.-1160546546.1718048896). 

1. Create a new project
    <img src="/assets/Step1.png" width="300" height="100">
    <img src="/assets/Step2.png" width="300" height="100">
    <img src="/assets/Step3.png" width="300" height="100">
    <img src="/assets/Step4.png" width="300" height="100">

 2. Setting up Oauth consent screen
    <img src="/assets/Step5.png" width="300" height="100">
    <img src="/assets/Step6.png" width="300" height="100">
    <img src="/assets/Step7.png" width="300" height="100">
    <img src="/assets/Step8.png" width="300" height="100">
    <img src="/assets/Step9.png" width="300" height="100">
    <img src="/assets/Step10.png" width="300" height="100">
In this step, keep in mind that **only the gmail accounts you add here are the ones that are going to be able to log in when you're testing the API**. 
    ![Step 11](/assets/Step11.png)

3. Getting the credentials
    <img src="/assets/Step12.png" width="300" height="100">
    <img src="/assets/Step13.png" width="300" height="100">
    <img src="/assets/Step14.png" width="300" height="100">
    <img src="/assets/Emphasis.png" width="300" height="100">
    <img src="/assets/Step15" width="300" height="100">
Remember these credentials because you're going to need them later
    <img src="/assets/Step16.png" width="300" height="100">
