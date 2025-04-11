from flask import Flask, request, jsonify

app = Flask(__name__)

@app.route('/')
def home():
    return "Test Rasa API Server is running!"

@app.route('/webhooks/rest/webhook', methods=['POST'])
def webhook():
    data = request.json
    print(f"Received message: {data}")
    
    # Simple bot responses based on intent
    message = data.get('message', '').lower()
    sender = data.get('sender', 'user')
    
    if 'hello' in message or 'hi' in message:
        return jsonify([
            {"recipient_id": sender, "text": "Hello from the test server!"},
            {"recipient_id": sender, "text": "How can I help you today?"}
        ])
    elif 'bye' in message or 'goodbye' in message:
        return jsonify([
            {"recipient_id": sender, "text": "Goodbye! Have a nice day!"}
        ])
    else:
        return jsonify([
            {"recipient_id": sender, "text": f"You said: {message}. I'm a simple test server."}
        ])

if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5006, debug=False) 