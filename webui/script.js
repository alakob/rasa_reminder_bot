document.addEventListener('DOMContentLoaded', () => {
    const chatWindow = document.getElementById('chat-window');
    const userInput = document.getElementById('user-input');
    const sendButton = document.getElementById('send-button');

    const RASA_API_URL = 'http://localhost:5005/webhooks/rest/webhook';
    const SENDER_ID = 'user'; // Use a consistent sender ID

    // Function to add a message to the chat window
    function addMessage(text, sender) {
        const messageElement = document.createElement('div');
        messageElement.classList.add('message');
        messageElement.classList.add(sender === 'user' ? 'user-message' : 'bot-message');
        messageElement.textContent = text;
        chatWindow.appendChild(messageElement);
        // Scroll to the bottom
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Function to add an error message
    function addErrorMessage(text) {
        const errorElement = document.createElement('div');
        errorElement.classList.add('message', 'error-message');
        errorElement.textContent = text;
        chatWindow.appendChild(errorElement);
        chatWindow.scrollTop = chatWindow.scrollHeight;
    }

    // Function to send message to Rasa
    async function sendMessageToRasa(message) {
        try {
            const response = await fetch(RASA_API_URL, {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ sender: SENDER_ID, message: message })
            });

            if (!response.ok) {
                console.error('Rasa API Error:', response.status, response.statusText);
                addErrorMessage(`Error: Could not reach Rasa server (Status: ${response.status})`);
                return;
            }

            const botResponses = await response.json();

            if (botResponses && botResponses.length > 0) {
                botResponses.forEach(resp => {
                    if (resp.text) {
                        addMessage(resp.text, 'bot');
                    }
                    // Handle other response types like images if needed
                    // if (resp.image) { ... }
                });
            } else {
                // Handle case where Rasa returns empty response
                addErrorMessage('Bot did not provide a response.');
            }

        } catch (error) {
            console.error('Error sending message to Rasa:', error);
            addErrorMessage('Error: Could not connect to Rasa server.');
        }
    }

    // Event listener for the send button
    sendButton.addEventListener('click', () => {
        const messageText = userInput.value.trim();
        if (messageText) {
            addMessage(messageText, 'user'); // Display user message immediately
            userInput.value = ''; // Clear input
            sendMessageToRasa(messageText);
        }
    });

    // Event listener for pressing Enter in the input field
    userInput.addEventListener('keypress', (event) => {
        if (event.key === 'Enter') {
            sendButton.click(); // Trigger button click
        }
    });

    // Optional: Add an initial greeting from the bot
    // addMessage('Hello! How can I help you today?', 'bot');
}); 