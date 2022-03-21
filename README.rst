Table of Contents
=================

1. `General`_

2. `Installation and deployment`_

3. `Configuration`_

4. `Assumptions and Improvements`_


General
========
This program is a home assignment of SafeBreach.
It demonstrates the ability to connect to a given email server, pole on a specific folder, fetch the email on arrival,
parse it and then act upon given set of rules.


Installation and deployment
===========================

1. Open a command line on your machine (verify git installation) and run the following:
    git clone git@github.com:zeevschneider/SafeBreach.git

2. Make sure that you have a machine with Python &gt;= 3.6 installed

3. Open a command line and cd to the /SafeBreach folder in the downloaded package

4. The best way is to install requirements into a virtual environment in order not to soil
    your python with unnecessary packages:
    a. Install virtualenv package - pip install virtualenv
    b. Create virtual environment:
        1. Make sure that you are in the /SafeBreach folder
        2. Run the following command – virtualenv {your_env_name}
        3. Activate your virtual environment – type {your_env_name}\Scripts\activate
        Your command line looks like the following:
        ({your_env_name}) {path}/SafeBreach
    c. Run the following command to install packages that are listed in the requirements.txt file:
       pip install -r requirements.txt
       You should receive a “Successfully installed…” message

Configuration
==============
 The project comes with a config file (config/email_server.yml), which enables configuration for an email server
 connection (tested for gmail only).
 We have set a Google 2-step verification account for this project.
 In order to get into account's UI use the "EMAIL" and "UI_PASSWORD" entries in the config file (you may be prompted for
 the confirmation key upon login attempt - please contact me)

 Please use the "From" entry in the config file to control the program's email filtering:
    e.g By default it is configured to filter email from Gmail


 Assumptions and Improvements:
 =============================
 1. The program filters email by the "From" section of the email (single address).
 2. The program sends response as a separate message to the receiver. It would be better to respond to the original message.
 3. When a relevant message (correct key word and attached file) is received, file run result is a attached as a file, because stdout
    and stderr data are not decoded to true stings.
 4. Keyword is filtered as exact match:
    i.e "banana", "Banana"  but not "bananas"

