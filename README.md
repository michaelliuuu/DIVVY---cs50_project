# DIVVY

A web application that allows users to easily split expenses with others. Groups are created with friends and family to allow bills or payments to be one place. Ranging from vacation trips to a cup of coffee, DIVVY can track it all.

You can watch a demonstration video **<a href="https://youtu.be/4_yymIpAqs0">here</a>**.

<img width="1440" alt="index" src="https://github.com/michaelliuuu/cs50_project/assets/102439915/27eb73dd-0396-40c2-a58d-60ac5b2497ea">
<img width="1440" alt="activity" src="https://github.com/michaelliuuu/cs50_project/assets/102439915/8097bfb3-2c39-416b-be23-e2c5f4331c76">


## Overview
### 1. Home Page
The home page displays all the groups that have been created, as well as its added members and their current accumulated expenses.

### 2. Group Page 
Users need to first create groups to eventually be populated. Add as many members of your friends or family to these groups.

### 3. Split Page
Conveniently split expenses amongst group members by initially choosing a group, picking the members that need the expense to be split, the expense itself, and its description.

### 4. Pay Page
Quickly pay off individual expenses by choosing the group, then inputting the amount the person wants to pay off.

### 5. Activity Page
Provides a detailed view of all transactions made from splitting and paying off expenses.


## Technologies
The site was developed using **Flask**, a Python web framework, which serves as its backend. **SQLite3** was utilized to store and manage the database. For the site's frontend, **HTML/CSS** was employed for its simplicity.


## Installation
Anyone is welcome to install this program. The following are the steps to run it:
### Step 1: Cloning the repository
Here are the instructions to properly **<a href="https://docs.github.com/en/repositories/creating-and-managing-repositories/cloning-a-repository">clone</a>** this repo.

## Step 2: Create a virtual environment
Within the terminal of this program, type in 'pip install virtualenv' to install the virtual environment, then 'virtualenv venv' to create the environment.

### Step 3: Installing the dependencies
Within the terminal of this program, type in 'pip install -r requirements.txt' to install all the dependencies within the requirement.txt file. 

### Step 4: Run the application
Now run the app.py file to start the program.


## Contributions
This application was solely done by myself for the final project for **Harvard University's CS50x**. 
The template from "pset9 finance" was used, alongside my own flair.


## Future Updates
- Allow users to change/reset their passwords
- Allow users to delete groups and members within the group
- Improved layouts for easier accessibility
- Notification system to alert users about new group activities, payments, and balances
 