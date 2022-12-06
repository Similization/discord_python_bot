# How to use this bot
## First steps
1. You will need to create your own configuration file in the 
**util** folder, it should be named as configuration.json and contains:
    ```
    {
    "bot": {
        "token": "<your discord token bot>"
    },

    "yandex": {
        "token": "<your yandex music account token>"
    },

    "youtube": {

        "YDL_OPTIONS": {
            "format": "bestaudio",
            "noplaylist": "False"
    },

        "FFMPEG_OPTIONS": {
            "before_options": "-reconnect 1 -reconnect_stream 1 -reconnect_delay_max 5",
            "options": "-vn"
        }
    },

    "database": {
        "host": "localhost",
        "login": "<your database login>",
        "password": "<your database password>"
        }
    }
    ```
2. If you want to collect information - you will have to run several scripts in sql folder to create database
3. After you have created the config file - you can safely run ***bot_example.py*** file
