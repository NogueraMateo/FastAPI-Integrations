confirmation_message = lambda token: f'''
        <!DOCTYPE html>
        <html lang="en">
        <head>
            <meta charset="UTF-8">
            <meta name="viewport" content="width=device-width, initial-scale=1.0">
            <style>
                body {{
                    font-family: Arial, sans-serif;
                    margin: 0;
                    padding: 0;
                    background-color: #f4f4f4;
                }}
                .container {{
                    width: 100%;
                    padding: 20px;
                    background-color: #ffffff;
                    box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                    margin: 20px auto;
                    max-width: 600px;
                }}
                .header {{
                    background-color: #4CAF50;
                    color: white;
                    padding: 10px 0;
                    text-align: center;
                }}
                .content {{
                    padding: 20px;
                }}
                .footer {{
                    background-color: #f1f1f1;
                    text-align: center;
                    padding: 10px 0;
                    color: #777;
                }}
                a.button {{
                    display: inline-block;
                    padding: 10px 20px;
                    font-size: 18px;
                    color: #ffffff;
                    background-color: #4CAF50;
                    text-decoration: none;
                    border-radius: 5px;
                    margin-top: 20px;
                }}
                a.button:hover {{
                    background-color: #45a049;
                }}
            </style>
        </head>
        <body>
            <div class="container">
                <div class="header">
                    <h1>Confirmation of your account</h1>
                </div>
                <div class="content">
                    <p>Hola,</p>
                    <p>Please follow the following link to confirm your account:</p>
                    <a href="http://127.0.0.1:5500/confirm-account.html?token={token}" class="button">Confirm Account</a>
                </div>
                <div class="footer">
                    <p>If you received this message by mistake, please ignore this email.</p>
                </div>
            </div>
        </body>
        </html>
        '''

reset_message = lambda token: f'''
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <style>
            body {{
                font-family: Arial, sans-serif;
                margin: 0;
                padding: 0;
                background-color: #f4f4f4;
            }}
            .container {{
                width: 100%;
                padding: 20px;
                background-color: #ffffff;
                box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
                margin: 20px auto;
                max-width: 600px;
            }}
            .header {{
                background-color: #ff4c4c;
                color: white;
                padding: 10px 0;
                text-align: center;
            }}
            .content {{
                padding: 20px;
            }}
            .footer {{
                background-color: #f1f1f1;
                text-align: center;
                padding: 10px 0;
                color: #777;
            }}
            a.button {{
                display: inline-block;
                padding: 10px 20px;
                font-size: 18px;
                color: #ffffff;
                background-color: #ff4c4c;
                text-decoration: none;
                border-radius: 5px;
                margin-top: 20px;
            }}
            a.button:hover {{
                background-color: #e04343;
            }}
        </style>
    </head>
    <body>
        <div class="container">
            <div class="header">
                <h1>Password Recovery</h1>
            </div>
            <div class="content">
                <p>Hola,</p>
                <p>Please follow the following link to reset your password:</p>
                <a href="http://127.0.0.1:5500/recover.html?token={token}" class="button">Reset Password</a>
            </div>
            <div class="footer">
                <p>If you have not requested to reset your password, please ignore this email.</p>
            </div>
        </div>
    </body>
    </html>
    '''

user_invitation_message = lambda formatted_time, join_url: f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .container {{
            width: 100%;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
        }}
        .header {{
            background-color: #007bff;
            color: white;
            padding: 10px 0;
            text-align: center;
        }}
        .content {{
            padding: 20px;
        }}
        .footer {{
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            color: #777;
        }}
        a.button {{
            display: inline-block;
            padding: 10px 20px;
            font-size: 18px;
            color: #ffffff;
            background-color: #007bff;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }}
        a.button:hover {{
            background-color: #0056b3;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Invitación a Reunión de Zoom</h1>
        </div>
        <div class="content">
            <p>¡Hola!, agendaste una reunión de Zoom para asesoría.</p>
            <h4>Fecha y hora: {formatted_time}</h4>
            <p>Únete a la reunión Zoom haciendo clic en el siguiente enlace:</p>
            <a href="{join_url}" class="button">Unirse a la Reunión</a>
        </div>
        <div class="footer">
            <p>Si recibiste este mensaje por error, por favor ignora este correo electrónico.</p>
        </div>
    </div>
</body>
</html>
'''

advisor_invitation_message = lambda formatted_time, join_url, current_user_first_name, current_user_lastname, topic: f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .container {{
            width: 100%;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
        }}
        .header {{
            background-color: #28a745;
            color: white;
            padding: 10px 0;
            text-align: center;
        }}
        .content {{
            padding: 20px;
        }}
        .footer {{
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            color: #777;
        }}
        a.button {{
            display: inline-block;
            padding: 10px 20px;
            font-size: 18px;
            color: #ffffff;
            background-color: #28a745;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }}
        a.button:hover {{
            background-color: #218838;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Nueva reunión de Zoom agendadada</h1>
        </div>
        <div class="content">
            <p>¡Hola!, el usuario {current_user_first_name} {current_user_lastname} ha agendado una reunión de zoom contigo.</p>
            <h4>Fecha y hora: {formatted_time}</h4>
            <h4>Motivo: {topic}</h4>
            <p>Únete a la reunión Zoom haciendo clic en el siguiente enlace:</p>
            <a href="{join_url}" class="button">Unirse a la Reunión</a>
        </div>
        <div class="footer">
            <p>Si recibiste este mensaje por error, por favor ignora este correo electrónico.</p>
        </div>
    </div>
</body>
</html>
'''


user_reschedule_message = lambda formatted_time, join_url: f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .container {{
            width: 100%;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
        }}
        .header {{
            background-color: #ff9800;
            color: white;
            padding: 10px 0;
            text-align: center;
        }}
        .content {{
            padding: 20px;
        }}
        .footer {{
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            color: #777;
        }}
        a.button {{
            display: inline-block;
            padding: 10px 20px;
            font-size: 18px;
            color: #ffffff;
            background-color: #ff9800;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }}
        a.button:hover {{
            background-color: #e68900;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Zoom Meeting Rescheduled</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>Your scheduled Zoom meeting has been rescheduled.</p>
            <h4>New Date and Time: {formatted_time}</h4>
            <p>Join the Zoom meeting by clicking the following link:</p>
            <a href="{join_url}" class="button">Join Meeting</a>
        </div>
        <div class="footer">
            <p>If you received this message by mistake, please ignore this email.</p>
        </div>
    </div>
</body>
</html>
'''

advisor_reschedule_message = lambda formatted_time, join_url, topic, user_first_name, user_last_name: f'''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <style>
        body {{
            font-family: Arial, sans-serif;
            margin: 0;
            padding: 0;
            background-color: #f4f4f4;
        }}
        .container {{
            width: 100%;
            padding: 20px;
            background-color: #ffffff;
            box-shadow: 0 0 10px rgba(0, 0, 0, 0.1);
            margin: 20px auto;
            max-width: 600px;
        }}
        .header {{
            background-color: #17a2b8;
            color: white;
            padding: 10px 0;
            text-align: center;
        }}
        .content {{
            padding: 20px;
        }}
        .footer {{
            background-color: #f1f1f1;
            text-align: center;
            padding: 10px 0;
            color: #777;
        }}
        a.button {{
            display: inline-block;
            padding: 10px 20px;
            font-size: 18px;
            color: #ffffff;
            background-color: #17a2b8;
            text-decoration: none;
            border-radius: 5px;
            margin-top: 20px;
        }}
        a.button:hover {{
            background-color: #138496;
        }}
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>Zoom Meeting Rescheduled</h1>
        </div>
        <div class="content">
            <p>Hello,</p>
            <p>The Zoom meeting scheduled by {user_first_name} {user_last_name} has been rescheduled.</p>
            <h4>New Date and Time: {formatted_time}</h4>
            <h4>Topic: {topic}</h4>
            <p>Join the Zoom meeting by clicking the following link:</p>
            <a href="{join_url}" class="button">Join Meeting</a>
        </div>
        <div class="footer">
            <p>If you received this message by mistake, please ignore this email.</p>
        </div>
    </div>
</body>
</html>
'''