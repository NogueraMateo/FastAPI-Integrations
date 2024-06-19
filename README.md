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
`In this step, keep in mind that **only the gmail accounts you add here are the ones that are going to be able to log in when you're testing the API**.` 
    ![Step 11](/assets/Step11.png)

3. Getting the credentials
    ![Step 12](/assets/Step12.png)
    ![Step 13](/assets/Step13.png)
    ![Step 14](/assets/Step14.png) <br>
`**The Authorized redirect URIs must be the same url that the one in this part of the code **`
    ![Emphasis](/assets/Emphasis.png)
    ![Step 15](/assets/Step15.png)
Remember these credentials because you're going to need them later
    ![Step 16](/assets/Step16.png)
