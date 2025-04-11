# Architecture Overview

This Rasa application follows a standard microservices architecture facilitated by Docker Compose.

## Components

1.  **Rasa Server (`rasa` service):**
    *   Handles Natural Language Understanding (NLU) and Dialogue Management.
    *   Exposes the main HTTP API (`localhost:5005`) for user interactions (including the Web UI and other potential channels).
    *   Processes user messages, predicts intents and entities, manages dialogue state, and triggers actions.
    *   Communicates with the Action Server for custom logic.
    *   Configured via `config.yml`, `domain.yml`, `data/`, `credentials.yml`.
    *   Loads the trained model from the `models/` directory.

2.  **Action Server (`action_server` service):**
    *   Runs custom Python code defined in `actions/actions.py`.
    *   Handles custom actions triggered by the Rasa server (e.g., saving/retrieving reminders from the database).
    *   Exposes an endpoint (`localhost:5055`) that the Rasa server calls.
    *   Communicates directly with the PostgreSQL database.
    *   Configured via `endpoints.yml`.

3.  **PostgreSQL Database (`db` service):**
    *   Provides persistent storage for reminders and potentially other data.
    *   Accessed by the Action Server using credentials defined (currently as defaults or via `.env`).
    *   Data is stored in a Docker volume (`postgres_data`) to persist across container restarts.
    *   Accessible from the host machine on `localhost:5434` (or as configured).

4.  **Web UI (Served by `start_rasa_app.sh`):**
    *   A simple static frontend (HTML, CSS, JavaScript) served by a Python HTTP server running on the host machine (`localhost:8888` or as configured).
    *   Allows users to interact with the chatbot through a web browser.
    *   Communicates directly with the Rasa Server's REST webhook (`http://localhost:5005/webhooks/rest/webhook`).

## Communication Flow (Web UI Example)

1.  User types a message in the Web UI (`localhost:8888`) and clicks Send.
2.  JavaScript sends a POST request with the message to the Rasa Server API (`localhost:5005/webhooks/rest/webhook`).
3.  Rasa Server processes the message (NLU, Dialogue Management).
4.  If a custom action is needed (e.g., `action_set_reminder`), Rasa Server calls the Action Server (`localhost:5055`).
5.  Action Server executes the custom Python code.
6.  If database interaction is required, Action Server connects to the PostgreSQL database (`db:5432` internally).
7.  Action Server completes its logic and responds to the Rasa Server.
8.  Rasa Server determines the final bot response(s).
9.  Rasa Server sends the response(s) back to the Web UI's JavaScript.
10. JavaScript updates the chat display in the browser.

## Deployment Considerations

*   This setup uses Docker Compose, suitable for development and testing.
*   For production, consider using orchestration tools like Kubernetes.
*   Ensure robust configuration management (e.g., using environment variables securely).
*   Scale services independently based on load (e.g., more Rasa server instances).
*   Implement proper monitoring and logging. 