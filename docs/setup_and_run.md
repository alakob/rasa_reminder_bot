# Setup and Running the Application

This document provides detailed steps for setting up the development environment and running the Rasa Reminder Chatbot application.

## Prerequisites

Ensure you have the following software installed on your host machine:

*   **Docker Engine:** To build and run the containerized services. ([Installation Guide](https://docs.docker.com/engine/install/))
*   **Docker Compose:** To manage the multi-container application defined in `docker-compose.yml`. ([Installation Guide](https://docs.docker.com/compose/install/))
*   **Git:** For cloning the repository.
*   **Python 3:** Required by the `start_rasa_app.sh` script to serve the static Web UI files. ([Download Python](https://www.python.org/downloads/))

## Setup Steps

1.  **Clone the Repository:**
    Open your terminal and navigate to the directory where you want to store the project. Then, clone the repository:
    ```bash
    git clone <your-repository-url>
    cd rasa_project # Or your project's root directory name
    ```

2.  **Environment Configuration (Optional):**
    The application can be configured using environment variables. The `docker-compose.yml` file defines default values (e.g., for the database connection). For production or specific setups, you might want to create a `.env` file in the project root to override these defaults.

    *Example `.env` file content:*
    ```dotenv
    # Database Credentials
    POSTGRES_DB=rasa_prod
    POSTGRES_USER=prod_user
    POSTGRES_PASSWORD=supersecretpassword

    # Rasa Model (Optional - otherwise uses default in docker-compose)
    # RASA_MODEL_NAME=your_specific_model.tar.gz

    # External Service Keys (if using channels like Twilio/Slack)
    # TWILIO_ACCOUNT_SID=ACxxxxxxxxxxxx
    # TWILIO_AUTH_TOKEN=your_auth_token
    # TWILIO_PHONE_NUMBER=+15551234567
    # SLACK_BOT_TOKEN=xoxb-your-token
    ```
    **Note:** Do not commit your `.env` file containing sensitive credentials to version control. Ensure it is listed in your `.gitignore` file.

3.  **Set Script Permissions:**
    Make the startup script executable:
    ```bash
    chmod +x start_rasa_app.sh
    ```

## Running the Application

Execute the startup script from the project root directory:

```bash
./start_rasa_app.sh
```

**What the script does:**

1.  **Checks Dependencies:** Verifies that `docker-compose.yml` and the `webui/` directory exist.
2.  **Starts Docker Services:** Runs `docker-compose up -d`. This command:
    *   Pulls necessary base images (like `postgres:13`).
    *   Builds the custom Rasa image defined in `Dockerfile` if it doesn't exist or if files have changed (respecting the `platform: linux/amd64` setting).
    *   Creates the necessary Docker network.
    *   Starts the `db`, `rasa`, and `action_server` containers in detached mode (background).
3.  **Starts Web UI Server:** Launches a simple Python HTTP server (`python3 -m http.server`) in the background, serving files from the `webui/` directory on the configured port (default `8888`). It stores the server's Process ID (PID) in `webui/.serverpid`.
4.  **Displays Access Points:** Prints the URLs for accessing the Web UI and Rasa API.
5.  **Waits for Interruption:** Keeps running until you press `Ctrl+C`.

**First Run:** The first time you run the script, Docker may need to download base images and build the Rasa image, which can take several minutes depending on your internet connection and machine specs.

## Accessing Services

*   **Web UI:** `http://localhost:8888`
*   **Rasa API:** `http://localhost:5005`
*   **Action Server:** `http://localhost:5055`
*   **Database:** `localhost:5434` (using a tool like `psql` or a GUI like DBeaver/pgAdmin)

## Stopping the Application

*   **Recommended:** Press `Ctrl+C` in the terminal where `./start_rasa_app.sh` is running. The script's `trap` command will intercept the signal and execute the `cleanup` function, which runs `docker-compose down` (stopping and removing containers) and kills the Python web server process.
*   **Manual Docker Stop:** If the script was terminated abruptly, you can manually stop the Docker services by running `docker-compose down` in the project root.

## Troubleshooting

*   **Port Conflicts (`Address already in use`):** If `start_rasa_app.sh` fails because a port is in use (e.g., 5005, 5055, 5434, 8888), identify the conflicting process using `sudo lsof -i tcp:<port_number>` and either stop that process or change the corresponding port mapping in `docker-compose.yml` or `start_rasa_app.sh`.
*   **Web UI Connection Error (`Could not connect to Rasa server`):**
    *   Ensure all Docker containers started correctly (`docker ps`).
    *   Check the logs of the `rasa` and `action_server` containers (`docker logs <container_name>`) for errors.
    *   Verify the Rasa server loaded the model correctly (check `rasa` logs after removing `--log-file`).
    *   Check the browser's developer console for network or CORS errors when using the Web UI.
*   **Docker Build Errors:** Refer to the build logs for specific dependency or installation issues. Common issues involve platform compatibility (ARM vs x86) or missing packages. We added `platform: linux/amd64` to `docker-compose.yml` to address `tensorflow-addons` issues on Apple Silicon. 