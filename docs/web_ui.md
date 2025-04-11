# Web UI\n\nThis project includes a simple web-based chat interface to interact with the Rasa bot.\n\n## Files\n\nLocated in the `webui/` directory:\n
*   `index.html`: The main HTML structure for the chat interface. Contains divs for the message display area and the input area (text box and send button).
*   `style.css`: Basic CSS for styling the chat window, messages (user vs. bot), input field, and button.
*   `script.js`: JavaScript code that handles:\n    *   Capturing user input from the text box (on button click or Enter key press).
    *   Displaying the user's message in the chat window.
    *   Sending the user's message to the Rasa server's REST webhook (`http://localhost:5005/webhooks/rest/webhook`) using the `fetch` API.
    *   Receiving the JSON response from Rasa.
    *   Parsing the response and displaying the bot's text messages in the chat window.
    *   Basic error handling for API connection issues.
    *   Automatic scrolling to the bottom of the chat window.

## How it Works\n\n1.  The `start_rasa_app.sh` script launches a simple Python HTTP server (`python3 -m http.server`) from the `webui/` directory.
2.  You access the UI by navigating to `http://localhost:<port>` (default port 8888) in your browser.
3.  The browser loads `index.html`, which in turn loads `style.css` and `script.js`.
4.  The JavaScript code handles the communication with the Rasa server running in Docker on `http://localhost:5005`.

## Limitations\n\n*   This is a very basic UI for testing and demonstration.
*   It only handles text messages from the bot.
*   It does not handle buttons, images, or other rich response types from Rasa.
*   There is no persistent chat history across browser sessions.
*   Error handling is minimal. 