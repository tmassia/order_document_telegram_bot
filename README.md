This project is a telegram bot for processing requests and sending order with attachments as a documents (docx,pdf)  via Gmail smtp email.

It includes the following main features:

handling messages and commands from Telegram users in chat following set of commands)async ,
sending email include collected  information with attached files. 

Interacting with a database to store information about clients and their orders - async connection.
            * * *

1- Install dependencies: 
pip install -r requirements.txt

2- Create a .env file and fill in the necessary variables,
      including bot token, API keys, and SMTP settings.

3- Run the script:
python main.py

4-Usage
To start using the bot in Telegram, enter the command /start.
Follow the instructions to fill in the required information.
Choose the type of test and send the request.

   * * *
   
stack of tech

aiogram3, asyncio, postgesql+psycorpg2, smtp setup for gmail(create token for third-party services)

LNG - HE 
