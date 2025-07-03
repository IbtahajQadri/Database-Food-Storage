# Team 25-03

## Database Food Storage

## Description
A browser-based web application for managing household food inventory. It allows users to categorize food items, track quantities and expiration dates, search and remove consumed items, and identify shortages by comparing actual stock with ideal quantities to support efficient grocery planning.

---

## 🚀 Client Setup Instructions: Running via Docker Image

This guide explains how to download the pre-built Docker image from our GitLab Container Registry and run the application on your local system.

> **Note:** It is assumed that Docker is already installed on your system.

### Step 1: Generate a GitLab Access Token

To access the GitLab Container Registry, you need to authenticate using a **Personal Access Token**:

1. Log in to your GitLab account.
2. Click your avatar (top left corner) and select **Edit Profile**.
3. Navigate to **Access Tokens**.
4. Create a new token named e.g., `"Container registry token"`.
5. Select the scopes:
   - `read_registry`
   - `write_registry` (optional if you don’t plan to push images)
6. Click **Create personal access token** and **save the token securely** — you won’t be able to see it again.

---

### Step 2: Log in to GitLab Container Registry from your Terminal

1. Go to your project’s **Container Registry** page on GitLab.
2. Click **CLI Commands** to expand the login command.
3. Copy the login command, which looks like:
   ```bash
   docker login registry.gitlab.com -u <your-username> -p <your-access-token>
   ```
4. Paste and run this command in your terminal to authenticate Docker with GitLab.

---

### Step 3: Pull and Run the Docker Image

1. In the Container Registry, find the image you want to run.
2. Copy the full image path (e.g., `registry.gitlab.com/thi-wi/sweng/m-egm/team-25-03:latest`).
3. Run the Docker container with:

    ```bash
    docker run -it --pull=always -p 8000:8000 registry.gitlab.com/thi-wi/sweng/m-egm/team-25-03:latest
    ```

- The flag `--pull=always` ensures Docker always pulls the latest version of the image before running.

---

### Step 4: Access the Application

Once the container is running, the web application will be accessible at:
http://localhost:8000/

Open this URL in your web browser to start using the Food Storage App.

---

## Notes

- Ensure Docker is installed on your system before following these steps.
- If you encounter any issues logging in or pulling the image, verify your access token and permissions.
- Contact the development team for further support 😊