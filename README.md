# FULL-FEATURED-BACKEND-APPLICATION
Full Featured Backend Application, using FastAPI, SQLAlchemy and PostgreSQL. Performing user Authentication and Authorization using JWT along with Google Oauth 2.0 and integration with Zoom API for scheduling virtual meetings.

The idea of this project came out of the need of a company that offers different services (web development, mobile development, marketing support, accounting support, etc,) to give extra information to those users interested in acquiring their services. 

In order to avoid face-to-face attendance, I implemented a virtual meeting system using Zoom API to generate zoom meeting links. The meetings are supposed to be attended by virtual assitants on the day and time set by the user. 

## TECHNOLOGIES
- Python
- FastAPI
- Fast-mail
- SQLAlchemy
- PostgreSQL
- Git & Github
- Docker

## Features

### User Authentication and Authorization
- **JWT Authentication:** Secure login and token-based authentication for users.
- **Google OAuth 2.0:** Allows users to log in and register using their Google accounts.

### User Management
- **User Registration:** Create new user accounts with email verifications.
- **User Login:** Secure user login with JWT tokens.
- **Password Reset:** Users can reset their passwords via email links, in case they have forgotten their passwords.
- **Email Confirmation:** Users must confirm their email address to activate their accounts.

### Role-Based Access Control (RBAC)
- **Admin Roles:** Admin users have elevated privileges and can manage other users.
- **User Roles:** Regular users have limited access compared to admin users.

### Meeting Scheduling
- **Zoom Integration:** Schedule virtual meetings using the Zoom API.
- **Email Invitations:** Automatic email invitations sent to users and advisors with meeting details.
- **Meeting Management:** Users can view and manage their scheduled meetings.

### Rate Limiting 
- **Login Attempts Limiting:** Protects against brute-force attacks by limiting login attempts using redis.
- **Password Reset Attempts Limiting:** Protects against spam and server overloading by several requests.

### API Documentation
- **Swagger UI:** Interactive API documentation available at 'http://localhost:8000/docs'

### Deployment and Scalability
- **Dockerized Setup:** Easily deploy the application using Docker and Docker Compose.
- **Environment Configuration:** Use environment variables to configure the application securely.

# GETTING STARTED
Here are the steps to follow so that you can test this REST-API on your local machine.

- Make sure you have **Docker** and **Docker Compose** installed in your PC. If you are using Windows OS, make sure you have **Docker Desktop** installed.
    - You can download Docker Desktop by clicking [here.](https://www.docker.com/products/docker-desktop/)

- Go to your terminal and make a git clone of this repository. 
```
git clone https://github.com/NogueraMateo/FULL-FEATURED-BACKEND-APPLICATION.git
```

## Setting up the Google Cloud Console project

- In order to assure that Google Oauth works as expected, you'll need to configure a project in [Google Cloud Console](https://console.cloud.google.com/welcome/new?_ga=2.117443785.-1160546546.1718048896). 

1. Create a new project
    ![Step 1](/assets/Step1.png)
    ![Step 2](/assets/Step2.png)
    ![Step 3](/assets/Step3.png)
    ![Step 4](/assets/Step4.png)

 2. Setting up Oauth consent screen
    ![Step 5](/assets/Step5.png)
    ![Step 6](/assets/Step6.png)
    ![Step 7](/assets/Step7.png)
    ![Step 8](/assets/Step8.png)
    ![Step 9](/assets/Step9.png)
    ![Step 10](/assets/Step10.png)
In this step, keep in mind that `**only the gmail accounts you add here are the ones that are going to be able to log in when you're testing the API**.`
    ![Step 11](/assets/Step11.png)

4. Getting the credentials
    ![Step 12](/assets/Step12.png)
    ![Step 13](/assets/Step13.png)
    ![Step 14](/assets/Step14.png) 

    ![Step 15](/assets/Step15.png)
    `**The Authorized redirect URIs must be the same url that the one in this part of the code **`
    ![Emphasis](/assets/Emphasis.png)
Remember these credentials because you're going to need them later
    ![Step 16](/assets/Step16.png)

## Setting up the Zoom account application

You'll also need to create a zoom application, specifically a Server-to-Server OAuth. This step is neccessary to get the zoom
credentials to make sure the meeting scheduling works as expected. 

You can easily get the credentials by following the [Zoom Documentation](https://developers.zoom.us/docs/internal-apps/)
After you have created the app, you can go to your [apps](https://marketplace.zoom.us/user/build) and click on the project you
just created. 

There you shall see a screen like this
    ![Zoom app Dashboard](/assets/ZoomApp.png)

Keep these credentials at hand because you'll need them later.

## Setting up the `.env` file





