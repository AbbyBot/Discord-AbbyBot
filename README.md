# <p align="center">Discord AbbyBot</p>

<p style="text-align: center;"><strong>Entertainment, Administration, Multilingual, Storytelling, A charismatic survivor girl.</strong></p>

<div align="center">
powered by

![image]( https://img.shields.io/badge/Discord.py-7289DA?style=for-the-badge&logo=discord&logoColor=white)
![image]( https://img.shields.io/badge/Python-3.10.12-3776AB?style=for-the-badge&logo=python&logoColor=white)
![image]( https://img.shields.io/badge/MySQL-brown?style=for-the-badge&logo=mysql&logoColor=white)
![image]( https://img.shields.io/badge/Flask-000000?style=for-the-badge&logo=flask&logoColor=white)
![image]( https://img.shields.io/badge/dotenv-darkgreen?style=for-the-badge&logo=dotenv&logoColor=EEF37B)
</div>


AbbyBot is a multi-purpose discord application, mainly dedicated to the entertainment and administrative sector.


<p align="center">AbbyBot plays Abigail "Abby" Monroe  as a character, a character designed by 'AstronautMarkus', every action she takes will try to imitate the personality of this fictional character.</p>



## Overview

AbbyBot is an application for Discord (BOT) designed by <a href="https://reyesandfriends.cl/">reyesandfriends.cl</a>, a project that seeks to create a self-sufficient application for the management and entertainment of servers, through the use of `slash_commands`, it also has a multilingual system to switch languages ​​from `English` to `Spanish` and vice versa.


## Bot Features

- **Slash commands:** AbbyBot owns all its commands using `slash_commands` to make it easier for the user to use.
- **Events system:** AbbyBot has an event system where it will respond to the user in different ways if they do a specific thing, such as mentioning it or deleting messages. This system can be disabled by the administrator.
- **Administration system:** `(W.I.P)` is currently still considered a work in development, but will be implemented very soon in its initial phase.
- **Random dialogues:** AbbyBot speaks different words in different languages, has different dialogues in order to attract the user's attention. 
- **Music player:** This command is acclaimed by many for sure, but at the same time it is a risk factor, a command to play .mp3 files in the bot.
- **'Abigail':** One of AbbyBot's objectives is to present "her" character, each dialogue she has has some story to tell.

## Installation (Development)

AbbyBot is built with the use of global variables (dotenv), so you need to create an `.env` file before starting.
- **Create a .env file:** Using a code or text editor you can create a `.env` file. It must contain the following content:

| **Variable**       | **Description**                                                                 |
|--------------------|---------------------------------------------------------------------------------|
| `BOT_TOKEN`        | The token provided by Discord for your bot (keep this secret).                  |
| `DB_HOST`          | The database host (e.g., `localhost`, without port).                            |
| `DB_USER`          | Username for your database connection.                                          |
| `DB_PASSWORD`      | Password for your database connection.                                          |
| `DB_NAME`          | The name of the schema to be used by AbbyBot.                                   |
| `EMOJIS`           | A list of Discord emojis used randomly by AbbyBot. Example: `<:emoji_name:id>`. |
| `API_URL`| API URL to do a POST when AbbyBot is online or offline Example: `https://api.com/bot-info`.|




- **Save the file:** You must save the .env file in `Python_Discord-AbbyBot` directory, between `Abby-bot.py`



```plaintext
Repository Root
│
├── Python_Discord-AbbyBot/
│   ├── Abby-bot.py
│   └── .env
│
└── README.md
```

- **Create the database:** Using the same credentials as the .env except for the discord token, you must connect to a `MySQL database manager`, such as <a href="https://www.mysql.com/products/workbench/">MySQL Workbench</a>, <a href="https://www.phpmyadmin.net/">phpMyAdmin</a>, <a href="https://dbeaver.io/">DBeaver</a>, etc.

You must look for a couple of files found in the `SQL_Files` directory, inside this you will find two more directories:

```plaintext
Repository Root
│
├── Python_Discord-AbbyBot/
│   └─ SQL_Files/
│      ├─ insert_data/
│      └─ tables_creation/
│
└── README.md
```

- **Use Creation data SQL file:** Inside the `tables_creation` directory, there is a .SQL file which has the script to create the tables necessary to store AbbyBot data.

```plaintext
Repository Root
│
├── Python_Discord-AbbyBot/
│   └─ SQL_Files/
│      └─ tables_creation/
│         └─ abbybot.sql
│
└── README.md
```

Now we simply run the SQL script and the tables will be created.

- **Insert Data:** To insert the necessary data into the database you created, we must return to the other directory, the one called `insert_data`. 

Inside this, you will find different .SQL files:

```plaintext
Repository Root
│
├── Python_Discord-AbbyBot/
│   └─ SQL_Files/
│      └─ insert_data/
│         ├─ abbybot_event_messages.sql
│         ├─ abbybot_help.sql
│         └─ abbybot_tell_story.sql
│
└── README.md
```
Here, in short, the same thing is repeated, you must open any .SQL script (regardless of the order) and execute it so that the data is inserted, try to do it only once since the tables are auto-incrementing and duplicate data could be generated.

The important thing is that ALL the .SQL files are execute

### Install FFmpeg

AbbyBot requires **FFmpeg** to process and play audio files. Follow the instructions below based on your operating system.

#### Installing FFmpeg

- **On Windows:**
  
  1. Download FFmpeg from the official site: [FFmpeg - Windows builds](https://ffmpeg.org/download.html).
  2. Extract the downloaded zip file to a folder (e.g., `C:\ffmpeg\`).
  3. Add FFmpeg to your system's PATH:
     - Open **Settings** > **System** > **About** > **Advanced system settings**.
     - Click **Environment Variables**.
     - Under **System Variables**, find **Path**.
     - Click **Edit** and then **New**. Add the path to the `bin` folder of FFmpeg (e.g., `C:\ffmpeg\bin`).
     - Save the changes and close the settings window.
  4. To verify the installation, open a command prompt and run:
     ```bash
     ffmpeg -version
     ```

- **On Linux:**
  
  FFmpeg can be installed directly from the package manager on most Linux distributions:

  - **Debian/Ubuntu-based distributions:**
    ```bash
    sudo apt update
    sudo apt install ffmpeg
    ```

  - **Fedora/RHEL-based distributions:**
    ```bash
    sudo dnf install ffmpeg
    ```

  - **Arch Linux:**
    ```bash
    sudo pacman -S ffmpeg
    ```

  After installing FFmpeg, you can verify the installation by running:
  ```bash
  ffmpeg -version
  ```

- **On macOS:**
  
  You can install FFmpeg using **Homebrew**:

  ```bash
  brew install ffmpeg
  ```

  After installation, check the version:

  ```bash
  ffmpeg -version
  ```



-Finally, the database will be ready.

<p align="center">To run AbbyBot there are two ways, depending on the operating system or the Distro that you use:</p>



### Windows method:

- **Open "1. Create Windows environment.bat"** - will create a Python virtual environment in the path and then install AbbyBot dependencies.
- **Open "2. Activate Windows environment.bat"** : it will activate the environment
- **From "2. Activate Windows environment.bat" manually drag the file "3. Start Windows environment.bat" and run it**: This will start AbbyBot from the console with its environment.


### GNU/Linux (most Distros) method:

- **Check Python version:** First you have to verify the version of Python, which is at least 3.10, first we will open a terminal using alt ctrl + alt + t or simply searching for it in the applications menu.

Execute 
```plaintext
python3 --version
```
the system will display the installed Python version. 

- **Create virtual environment:** Using the same terminal

Execute 
```plaintext
python3 -m venv venv
```
the system will display the installed Python version. 

- **Start environment:** After creating the environment, run the following command to activate it:

Execute 
```plaintext
source venv/bin/activate
```

If everything works, in your terminal you should see (venv) before the username:

Execute 
```plaintext
(venv) user@mycomputer:
```
Now all that remains is to install the requirements.

- **Install the requirements:** To execute all the code you must install all the requirements that AbbyBot needs, in the `requirements.txt` file located at the root of the repository you will find:

```plaintext
Repository Root
│
├── requirements.txt
│
└── README.md
```

Go to it with the terminal and the environment activated and then install the requirements using pip install:

```plaintext
pip install -r requirements.txt
```

With the `requirements already installed`, the `environment activated`, the `database created and data inserted` and the `.env with its variables ready`, all that remains is to start the main `.py` file:

- **Run AbbyBot:** To run AbbyBot, we must have `all the previous steps completed`, have our `virtual environment ready and activated`, we must go to the `Python_Discord-AbbyBot` directory, within this you will find `Abby-bot.py`, which we must execute:

```plaintext
python AbbyBot.py 
```
And if you performed all the steps correctly, everything will be ready!

