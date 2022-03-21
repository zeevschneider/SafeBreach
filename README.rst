Table of Contents
=================

1. `General`_

2. `Specifications`_

3. `Installation and deployment`_

4. `Configuration`_

4. `Usage`_

5. `Assumptions and Improvements`_


General
========
This program is a home assignment of SafeBreach.
It demonstrates the ability to connect to a given email server, pole on a specific folder, fetch the email on arrival,
parse it and then act upon given set of rules.


Specifications:
===============
Should be able to receive emails from a specific domain

These emails will contain inside the body a certain {keyword} and an attached python file
Your application should be able to download the file, run it with python and send the output back
to the recipient inside the email body
If keyword == {keyword}, your application should send the output of the python attachment
If keyword != {keyword}, your application should send an email with the following body: “Invalid
keyword”
If the attachment is missing, your application should send an email with the following body:
“Attachment missing”
If the python file you try to run throws an exception, your application should send an email with
the backtrace of the exception


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


Usage:
======
Run the program:
    CD to safe_breach/bin and run "safebreach.cmd" or CD to safe_breach and run "python main.py".

Send email from your chosen domain (Domain:  From: key in configuration file) to your email address (Connectivity:  EMAIL: key).
See 'Specifications section'

Stop the program:
    Hit CTRL+C



Assumptions and Improvements:
=============================
 1. The program filters email by the "From" section of the email (single address).
 2. The program sends response as a separate message to the receiver. It would be better to respond to the original message.
 3. When a relevant message (correct key word and attached file) is received, file run result is a attached as a file, because stdout
    and stderr data are not decoded to true stings.
 4. Keyword is filtered as exact match:
    i.e "banana", "Banana"  but not "bananas"
 5. TODO: Writing Tests
 6. TODO: Verify Python installed - present friendly message is not
 7. TODO: Check flaky stop condition - not always stops on CTRL+C