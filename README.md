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

## FEATURES

### User Authentication and Authorization
- 🔒 **JWT Authentication:** Secure login and token-based authentication for users.
- 🔑 **Google OAuth 2.0:** Allows users to log in and register using their Google accounts.

### User Management
- 📝 **User Registration:** Create new user accounts with email verifications.
- 🔐 **User Login:** Secure user login with JWT tokens.
- 🔄 **Password Reset:** Users can reset their passwords via email links, in case they have forgotten their passwords.
- 📧 **Email Confirmation:** Users must confirm their email address to activate their accounts.

### Role-Based Access Control (RBAC)
- 🛠️ **Admin Roles:** Admin users have elevated privileges and can manage other users.
- 👥 **User Roles:** Regular users have limited access compared to admin users.

### Meeting Scheduling
- 📅 **Zoom Integration:** Schedule virtual meetings using the Zoom API.
- 📧 **Email Invitations:** Automatic email invitations sent to users and advisors with meeting details.
- 🗂️ **Meeting Management:** Users can view and manage their scheduled meetings.

### Rate Limiting 
- 🚫 **Login Attempts Limiting:** Protects against brute-force attacks by limiting login attempts using redis.
- 🚦 **Password Reset Attempts Limiting:** Protects against spam and server overloading by several requests.

### API Documentation
- 📖 **Swagger UI:** Interactive API documentation available at 'http://localhost:8000/docs'

### Deployment and Scalability
- 🐳 **Dockerized Setup:** Easily deploy the application using Docker and Docker Compose.
- 🔧 **Environment Configuration:** Use environment variables to configure the application securely.

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
    ![Step 1](/assets/Zoom-Tuto/Step1.png)
    ![Step 2](/assets/Zoom-Tuto/Step2.png)
    ![Step 3](/assets/Zoom-Tuto/Step3.png)
    ![Step 4](/assets/Zoom-Tuto/Step4.png)

 2. Setting up Oauth consent screen
    ![Step 5](/assets/Zoom-Tuto/Step5.png)
    ![Step 6](/assets/Zoom-Tuto/Step6.png)
    ![Step 7](/assets/Zoom-Tuto/Step7.png)
    ![Step 8](/assets/Zoom-Tuto/Step8.png)
    ![Step 9](/assets/Zoom-Tuto/Step9.png)
    ![Step 10](/assets/Zoom-Tuto/Step10.png)
In this step, keep in mind that `**only the gmail accounts you add here are the ones that are going to be able to log in when you're testing the API**.`
    ![Step 11](/assets/Zoom-Tuto/Step11.png)

4. Getting the credentials
    ![Step 12](/assets/Zoom-Tuto/Step12.png)
    ![Step 13](/assets/Zoom-Tuto/Step13.png)
    ![Step 14](/assets/Zoom-Tuto/Step14.png) 

    ![Step 15](/assets/Zoom-Tuto/Step15.png)
    `**The Authorized redirect URIs must be the same url that the one in this part of the code **`
    ![Emphasis](/assets/Zoom-Tuto/Emphasis.png)
Remember these credentials because you're going to need them later
    ![Step 16](/assets/Zoom-Tuto/Step16.png)

## Setting up the Zoom account application

You'll also need to create a zoom application, specifically a Server-to-Server OAuth. This step is neccessary to get the zoom
credentials to make sure the meeting scheduling works as expected. 

You can easily get the credentials by following the [Zoom Documentation](https://developers.zoom.us/docs/internal-apps/)
After you have created the app, you can go to your [apps](https://marketplace.zoom.us/user/build) and click on the project you
just created. 

There you shall see a screen like this
    ![Zoom app Dashboard](/assets/ZoomApp.png)

Keep these credentials at hand because you'll need them later.

## Setting up the gmail account from which the e-mails will be sent

To set this up, you must have access to the gmail account set up to send emails, such as a noreply@gmail.com or whatever the account is.
Then you follow the following steps in order to generate a Password Application.

![Step 1](/assets/Google-App-Tuto/GStep1.png)
![Step 2](/assets/Google-App-Tuto/GStep2.png)
![Step 3](/assets/Google-App-Tuto/GStep3.png)
![Step 4](/assets/Google-App-Tuto/GStep4.png)

Make sure you copy this password because you'll never see it again.

## Setting up the `.env` file

Now the next step is to configure the **.env** file. As you can see in the repository, there is a .env.example file, and you must replace 
some of the credentials and passwords we generated before.

Create a new `.env` file and fill it with the following information:

```ini
# PostgreSQL Database Configuration
POSTGRES_USER=postgres                      # Don't change it
POSTGRES_PASSWORD=your_postgres_password    # Choose a password
POSTGRES_DB=RESTAPI-DB                      # Don't change it 
POSTGRES_DB_HOST=db                         # Don't change it
POSTGRES_DB_PORT=5432                       # Don't change it

# Replace the values above here in the url
SQLALCHEMY_DATABASE_URL=postgresql://postgres:your_postgres_password@db:5432/RESTAPI-DB
```

Here you can leave everything as it is, except for the **POSTGRES_PASSWORD** just choose a password and replace it both in the 
variable and in the URL

```ini
# Secret Keys
ACCESS_TOKEN_SECRET_KEY=your_access_token_secret_key
EMAIL_CONFIRMATION_SECRET_KEY=your_email_confirmation_secret_key
PASSWORD_RESET_SECRET_KEY=your_password_reset_secret_key
GOOGLE_OAUTH_SECRET_KEY=your_google_oauth_secret_key
```

Your secret keys could be any string, but it is better for the security of the API to generate a long and more secure string.
You can generate it using this command in the terminal

```bash
openssl rand -hex 32
```
As a result, it'll generate a long string like this `**210b48bdfe0d703e820b93361e3178add9f18af8d0fadfecdd508446a780cc29**`.
I suggest, to generate a different string for each Secret Key and replace it up there.

```ini
# Zoom API Configuration
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_ACCOUNT_ID=your_zoom_account_id
```

Here you will have to replace those default values for the ones you got from creating the Zoom Server-to-Server Application.
Account ID, Client ID and Client Secret.

```ini
# Mail Configuration
MAIL_USERNAME=your_mail_username
MAIL_PASSWORD=your_mail_password
MAIL_FROM=your_mail_from_address
```

In the **MAIL_USERNAME** and **MAIL_FROM** fill it with the gmail direction you used to create the password application to send the emails
In the **MAIL_PASSWORD** fill it with the password Google gave you when you created the password application. 


```ini
# Google OAuth Configuration
GOOGLE_OAUTH_SECRET_CLIENT=your_google_oauth_secret_client
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
```

In the **GOOGLE_OAUTH_SECRET_CLIENT** fill it with the Client Secret given when creating the project with Google Cloud Console.
In the **GOOGLE_OAUTH_CLIENT_ID** fill it with the Clien ID given when creating the project with Google Cloud Console.