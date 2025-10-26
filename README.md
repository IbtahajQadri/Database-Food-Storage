# Database Food Storage

## Introduction
This Project was created as part of an assignment in the "Software Engineering" Course in the Engineering and Management Masters Degree at Technische Hochschule Ingolstadt. The aim of this group project was to work together as a team with each member having a different role in the software development process such as "Tester", "CICD Responsible", "Software Architect" and "Group Manager". My contribution to this project was as a CICD reponsible where i implemented the CICD pipeline in GItlab along with major functionalities of the software. 

## Description
A browser-based web application for managing household food inventory. It allows users to categorize food items, track quantities and expiration dates, search and remove consumed items, and identify shortages by comparing actual stock with ideal quantities to support efficient grocery planning. The main features of this web application include:
1. Creating a New Food Category, modifying an existing category in the database and deleting the category.
2. Creating food items to add to a category, modifying its characteristics and deleting a specific food item.
3. A search function which lets you search for food items based on categories or Expiry date.
4. Shopping list function which lets you see which items are nearing their expiry date and what needs to be purchased.

---

## 🛠️ Local Setup Instructions: Running via DJango server

### Step 1: Clone the Repository

1. Clone Repo with the following git command.
> git clone git@github.com:IbtahajQadri/Database-Food-Storage.git

2. Move into the project repository.
> cd team-25-03

### Step 2: Create and Activate Virtual Environment

1. Create a virtual environment (only once)
> python3 -m venv venv

2. Activate the environment

- For Linux/macOS:
> source venv/bin/activate

- For Windows:
> venv\Scripts\activate

### Step 3: Install Dependencies

> pip install -r requirements.txt

### Step 4: Running the server
> python manage.py runserver

the web application will be accessible at: http://localhost:8000/

---

## 🚀 Client Setup Instructions: Running via Docker Image

The original implementation of this project, including the **GitLab CI/CD pipeline** and **Docker image**, was developed on a private GitLab repository as part of the course assignment.

Due to university access restrictions, the GitLab repository is **not publicly accessible**.  
However, the `.gitlab-ci.yml` file and the Docker file is included in this repository for reference.

🐳 Run with Docker

You can run the Food Storage Django web application easily using Docker.

1️⃣ Build the Docker image

Make sure you’re in the folder containing the Dockerfile:

docker build -t food-storage .


This will build a Docker image named food-storage using your Dockerfile.

2️⃣ Run the container
docker run -d -p 8000:8000 food-storage


Open your browser and visit:
http://localhost:8000

3️⃣ Stop the container (optional)
docker ps               # List running containers
docker stop <container_id>

4️⃣ Rebuild after code changes
docker build --no-cache -t food-storage .

--- 

👥 Contributors

Team 25-03 (THI Software Engineering Course)
Hafiz Ali
Patience Dikio
Hashim Hasnain Hadi
Ibtahaj Athar Qadri
