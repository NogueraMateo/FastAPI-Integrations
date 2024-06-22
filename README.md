# FastAPI-Integrations
Welcome to FastAPI-Integrations. This project leverages the power of FastAPI, SQLAlchemy, and PostgreSQL to create a robust and scalable backend. It features user authentication and authorization using JWT, integrates Google OAuth 2.0 for seamless login experiences, and connects with the Zoom API to schedule virtual meetings effortlessly.

# Why this project?
In today's fast-paced digital world, companies need to provide quick and efficient ways for users to access their services. This project addresses that need by enabling virtual consultations, reducing the need for physical meetings, and providing a seamless experience for both users and service providers.

## TECHNOLOGIES
- Python
- FastAPI
- Fast-mail
- SQLAlchemy
- PostgreSQL
- Docker
- Git & Github

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
Follow the steps below to set up and run this project on your local machine. Ensure you have the necessary prerequisites.
Detailed instructions are provided to help you configure and run the application smoothly.

- Make sure you have **Docker** and **Docker Compose** installed in your PC. If you are using Windows OS, make sure you have **Docker Desktop** installed.
    - You can download Docker Desktop by clicking [here.](https://www.docker.com/products/docker-desktop/)

- Go to your terminal and make a git clone of this repository. 
```
git clone https://github.com/NogueraMateo/FastAPI-Integrations.git
```

## Setting up the Google Cloud Console project

To ensure that Google OAuth works as expected, you'll need to configure a project in [Google Cloud Console](https://console.cloud.google.com/welcome/new?_ga=2.117443785.-1160546546.1718048896). 

1. Create a new project
    ![Step 1](/assets/Zoom-Tuto/Step1.png)
    ![Step 2](/assets/Zoom-Tuto/Step2.png)
    ![Step 3](/assets/Zoom-Tuto/Step3.png)
    ![Step 4](/assets/Zoom-Tuto/Step4.png)

 2. Set up the OAuth consent screen
    ![Step 5](/assets/Zoom-Tuto/Step5.png)
    ![Step 6](/assets/Zoom-Tuto/Step6.png)
    ![Step 7](/assets/Zoom-Tuto/Step7.png)
    ![Step 8](/assets/Zoom-Tuto/Step8.png)
    ![Step 9](/assets/Zoom-Tuto/Step9.png)
    ![Step 10](/assets/Zoom-Tuto/Step10.png)
In this step, keep in mind that **`only the Gmail accounts you add here are the ones that are going to be able to log in when you're testing the API.`**
    ![Step 11](/assets/Zoom-Tuto/Step11.png)

4. Get the credentials
    ![Step 12](/assets/Zoom-Tuto/Step12.png)
    ![Step 13](/assets/Zoom-Tuto/Step13.png)
    ![Step 14](/assets/Zoom-Tuto/Step14.png) 

    ![Step 15](/assets/Zoom-Tuto/Step15.png)
    **`The Authorized redirect URIs must be the same url that the one in this part of the code. `**
    ![Emphasis](/assets/Zoom-Tuto/Emphasis.png)
Remember these credentials because you're going to need them later.
    ![Step 16](/assets/Zoom-Tuto/Step16.png)

## Setting up the Zoom account application

You'll also need to create a zoom application, specifically a Server-to-Server OAuth. This step is neccessary to get the Zoom
credentials to ensure the meeting scheduling works as expected. 

You can easily get the credentials by following the [Zoom Documentation](https://developers.zoom.us/docs/internal-apps/)
After you have created the app, you can go to your [apps](https://marketplace.zoom.us/user/build) and click on the project you
just created. 

There you shall see a screen like this
    ![Zoom app Dashboard](/assets/ZoomApp.png)

Keep these credentials at hand because you'll need them later.

## Setting up the gmail account from which the e-mails will be sent

To set this up, you must have access to the Gmail account set up to send emails, such as a noreply@gmail.com or whatever the account is.
Then follow these steps to generate a Password Application.

![Step 1](/assets/Google-App-Tuto/GStep1.png)
![Step 2](/assets/Google-App-Tuto/GStep2.png)
![Step 3](/assets/Google-App-Tuto/GStep3.png)
![Step 4](/assets/Google-App-Tuto/GStep4.png)

Make sure you copy this password because you'll never see it again.

## Setting up the `.env` file

The next step is to configure the **.env** file. As you can see in the repository, there is a **`.env.example`** file, and you must replace 
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

You can keep everything as it is, except for the **POSTGRES_PASSWORD**. Choose a secure password and replace it both in the variable and in the URL.

```ini
# Secret Keys
ACCESS_TOKEN_SECRET_KEY=your_access_token_secret_key
EMAIL_CONFIRMATION_SECRET_KEY=your_email_confirmation_secret_key
PASSWORD_RESET_SECRET_KEY=your_password_reset_secret_key
GOOGLE_OAUTH_SECRET_KEY=your_google_oauth_secret_key
```

Your secret keys can be any string, but for better security of the API, it is recommended to generate long, secure strings. You can generate them using the following command in the terminal:

```bash
openssl rand -hex 32
```
This will generate a long string like **`210b48bdfe0d703e820b93361e3178add9f18af8d0fadfecdd508446a780cc29`**.
It is suggested to generate a different string for each secret key and replace the placeholder values accordingly.

```ini
# Zoom API Configuration
ZOOM_CLIENT_ID=your_zoom_client_id
ZOOM_CLIENT_SECRET=your_zoom_client_secret
ZOOM_ACCOUNT_ID=your_zoom_account_id
```

Replace these default values with the ones you obtained when creating the Zoom Server-to-Server Application. Use the Account ID, Client ID, and Client Secret provided by Zoom.

```ini
# Mail Configuration
MAIL_USERNAME=your_mail_username
MAIL_PASSWORD=your_mail_password
MAIL_FROM=your_mail_from_address
```

- **MAIL_USERNAME** and **MAIL_FROM**: Use the Gmail address you set up to create the application password for sending emails.
- **MAIL_PASSWORD** Use the password provided by Google when you created the application password.


```ini
# Google OAuth Configuration
GOOGLE_OAUTH_SECRET_CLIENT=your_google_oauth_secret_client
GOOGLE_OAUTH_CLIENT_ID=your_google_oauth_client_id
```

- In the **GOOGLE_OAUTH_SECRET_CLIENT** fill it with the Client Secret given when creating the project with Google Cloud Console.
- In the **GOOGLE_OAUTH_CLIENT_ID** fill it with the Clien ID given when creating the project with Google Cloud Console.

```ini
ADMIN_EMAIL=your_admin_email@example.com      
ADMIN_PASSWORD_HASH=$2b$12$tOOtHr32DkiCAlnZa9F6UOASUvHo0vZlmMyYlvLxlttuqt7TvLyri
ADVISOR_EMAIL=your_advisor_email@example.com
ADVISOR_NAME=Your Advisor Name
```

- **ADMIN_EMAIL:** This is the email address that will be used for the default admin account created when the application starts. This account has administrative privileges and can manage other users and settings within the application.
- **ADMIN_PASSWORD_HASH:** This is the hashed password for the default admin account. To ensure security, use a strong hashing algorithm such as bcrypt to hash the password before setting this variable. Do not use plain text passwords. You're free to use the one provided in the **`.env.example`**,
the plain password is **admin123**
- **ADVISOR_EMAIL:** This is the email address for the default advisor that will be available in the system. Advisors are users who can be assigned to meetings and provide services or consultations.
- **ADVISOR_NAME:** This is the full name of the default advisor. It will be used to identify the advisor in the system and in communications with users.

### Generating a Secure Password Hash
To generate a secure password hash for the **`ADMIN_PASSWORD_HASH`** variable, you can use a tool like bcrypt. Here is an example of how to generate a bcrypt hash:

```python
from passlib.context import CryptContext

# Create a hashing context
pwd_context = CryptContext(schemes=["bcrypt"], deprecated="auto")

# Generate password hash
password = "anotherpassword"
password_hash = pwd_context.hash(password)

print(password_hash)
# Output: $2b$12$mw2oUt87EO.fxHVMT7Nzj.He1ld2Bw2rs7huwp099wiUta6OuyrVK
```

Replace `your_secure_password` with your desired password and use the resulting hash for the `ADMIN_PASSWORD_HASH` variable.

## Running the Project with Docker

Once you have configured the `.env` file, you can easily run the project using Docker. Follow these steps:

1. **Build and Run the Docker Containers:**

    Navigate to the project directory where the `docker-compose.yml` file is located and run the following command to build and start the containers:

    ```bash
    docker-compose up --build
    ```
    This command will build the Docker images and start the containers for the FastAPI application, PostgreSQL database, and any other services defined in the docker-compose.yml file.

2. **Access the Application:**
    Once the containers are up and running, you can access the FastAPI application in your web browser at:
    ```bash
    http://localhost:8000
    ```

    You can also access the interactive API documentation (Swagger UI) at:

    ```bash
    http://localhost:8000/docs
    ```

3. Stop the Docker Containers:

    To stop the running Docker containers, press Ctrl + C in the terminal where the docker-compose up command is running. Alternatively, you can run the following command in the project directory:
    ```bash
    docker-compose down
    ```

    This command will stop and remove the containers defined in the docker-compose.yml file.

## Cleaning Up the Database
If you need to clean up the database and start fresh, you can remove the Docker volumes used by the PostgreSQL container. This will delete all data in the database. Run the following command:

```bash
docker-compose down -v
```

This command stops the containers and removes the volumes, allowing you to start with a clean database when you run docker-compose up again.

# Examples of Front-End Integration
To demonstrate how to connect the front-end with the back-end for account confirmation and password reset, I have provided two example HTML files.
## Account Confirmation Example
### Overview
This section demonstrates how to implement a simple account confirmation flow using a front-end HTML page and the back-end FastAPI endpoints. When a user registers, they receive a confirmation email with a link. By clicking the link, they confirm their account through an HTML page that interacts with the back-end API. You can see the HTML [here](/demos/confirm-account.html)

### Back-End Endpoint
[Here](/api/routers/auth.py) is the corresponding FastAPI endpoint for confirming the user account

The workflow is:
1. `Register a new user:` When a user registers, an email with a confirmation link is sent to them. The link includes a token parameter.
2. `Click the confirmation link:` The user clicks the link in the email, which opens the [confirm-account.html](/demos/confirm-account.html) file in their browser.
3. `Confirm the account:` The user clicks the "Confirm your account" button, which sends a request to the FastAPI endpoint to confirm their account.

## Password Reset Example
This HTML file demonstrates how to reset a user's password by filling in a form and sending the new password to the back-end.
You can see the HTML provided [here](/demos/reset-password.html)

### Back-End Endpoint
[Here](/api/routers/password_reset.py) is the corresponding FastAPI endpoint for confirming the user account.

The workflow is:

1. **Request Password Reset:** The user requests to reset their password by entering their email address in a form on the front-end. This triggers an email with a password reset link to be sent to the user's email address. The link includes a token parameter.
2. **Click the Reset Link:** The user clicks the link in the email, which opens the [reset-password.html](/demos/reset-password.html) file in their browser.
3. **Enter New Password:** The user fills in the form with their new password and confirms it by re-entering the password.
4. **Submit the Form:** The user submits the form, which sends a request to the FastAPI endpoint to reset the password. If the token is valid and the passwords match, the user's password is updated in the database.


## License

This project is licensed under the MIT License - see the [LICENSE](LICENSE) file for details.
