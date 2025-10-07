import http.server
import socketserver
import json
import webbrowser
import threading
import time

# All airline data built into the file
AIRLINE_KNOWLEDGE = {
    "faqs": [
        {
            "question": "What is PacificBlue's baggage allowance?",
            "answer": "Economy class: 1 carry-on (7kg) + 1 personal item. Business class: 2 carry-ons (14kg total) + 1 personal item. Checked baggage starts at 23kg for economy.",
            "category": "baggage",
            "keywords": ["baggage", "luggage", "carry on", "suitcase", "weight", "bag", "packing"]
        },
        {
            "question": "How can I change my flight?",
            "answer": "You can change flights online up to 24 hours before departure through our website or mobile app. Fees may apply depending on fare type.",
            "category": "booking", 
            "keywords": ["change", "flight", "modify", "reservation", "ticket", "booking"]
        },
        {
            "question": "What is your check-in policy?",
            "answer": "Online check-in opens 24 hours before flight and closes 2 hours before departure. Airport check-in closes 45 minutes before departure.",
            "category": "checkin",
            "keywords": ["check in", "check-in", "boarding", "airport", "documents"]
        },
        {
            "question": "Do you offer refunds for cancelled flights?",
            "answer": "Full refunds for cancellations by PacificBlue. For passenger cancellations, refunds depend on fare type. Flexible fares are fully refundable.",
            "category": "refunds",
            "keywords": ["refund", "cancel", "cancellation", "money back"]
        },
        {
            "question": "What amenities are included?",
            "answer": "All flights include complimentary snacks and non-alcoholic drinks. International flights include meals, entertainment, and blanket kits.",
            "category": "amenities",
            "keywords": ["food", "meal", "entertainment", "wifi", "drink", "snack", "amenities"]
        },
        {
            "question": "Can I select my seat in advance?",
            "answer": "Seat selection is available during booking or after purchase through our website. Some seats may have additional fees.",
            "category": "booking",
            "keywords": ["seat", "select", "choose", "assignment", "preference"]
        },
        {
            "question": "What documents do I need for international travel?",
            "answer": "Valid passport, visa if required. Please check specific country requirements before travel.",
            "category": "checkin",
            "keywords": ["documents", "passport", "visa", "international", "travel"]
        },
        {
            "question": "Is WiFi available on your flights?",
            "answer": "Complimentary WiFi is available on all domestic flights. International flights offer premium WiFi packages for purchase.",
            "category": "amenities", 
            "keywords": ["wifi", "internet", "connectivity", "online", "wireless"]
        },
        {
            "question": "What is your pet travel policy?",
            "answer": "Small pets in carriers are allowed in cabin for $125 each. Larger pets must travel in climate-controlled cargo hold with advance booking.",
            "category": "baggage",
            "keywords": ["pet", "dog", "cat", "animal", "travel with"]
        },
        {
            "question": "How do I join your frequent flyer program?",
            "answer": "You can join PacificBlue Rewards for free on our website. Earn miles on every flight and redeem for awards, upgrades, and partner benefits.",
            "category": "booking",
            "keywords": ["frequent flyer", "rewards", "miles", "loyalty", "program"]
        }
    ]
}

def find_best_answer(user_question):
    """Simple keyword matching - pure Python, no dependencies"""
    question_lower = user_question.lower()
    best_match = None
    best_score = 0
    
    for faq in AIRLINE_KNOWLEDGE["faqs"]:
        score = 0
        
        # Check keywords
        for keyword in faq["keywords"]:
            if keyword in question_lower:
                score += 3  # High score for keyword matches
        
        # Check question words
        question_words = question_lower.split()
        for word in question_words:
            if len(word) > 3:  # Only meaningful words
                if word in faq["question"].lower():
                    score += 2
                if word in faq["answer"].lower():
                    score += 1
        
        # Update best match if this FAQ scored higher
        if score > best_score:
            best_score = score
            best_match = faq
    
    return best_match

# Beautiful web interface HTML
WEB_PAGE = '''
<!DOCTYPE html>
<html>
<head>
    <title>PacificBlue Airlines Assistant</title>
    <style>
        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
        }
        body {
            font-family: 'Arial', sans-serif;
            background: linear-gradient(135deg, #007bff, #0056b3);
            min-height: 100vh;
            padding: 20px;
        }
        .container {
            max-width: 800px;
            margin: 0 auto;
            background: white;
            border-radius: 15px;
            box-shadow: 0 10px 30px rgba(0,0,0,0.2);
            overflow: hidden;
        }
        .header {
            background: #007bff;
            color: white;
            padding: 30px;
            text-align: center;
        }
        .header h1 {
            font-size: 2.5em;
            margin-bottom: 10px;
        }
        .header p {
            font-size: 1.1em;
            opacity: 0.9;
        }
        .chat-container {
            height: 400px;
            overflow-y: auto;
            padding: 20px;
            background: #f8f9fa;
        }
        .message {
            margin: 15px 0;
            display: flex;
        }
        .user-message {
            justify-content: flex-end;
        }
        .bot-message {
            justify-content: flex-start;
        }
        .message-bubble {
            max-width: 70%;
            padding: 12px 18px;
            border-radius: 18px;
            word-wrap: break-word;
        }
        .user-bubble {
            background: #007bff;
            color: white;
            border-bottom-right-radius: 5px;
        }
        .bot-bubble {
            background: white;
            color: #333;
            border: 1px solid #ddd;
            border-bottom-left-radius: 5px;
        }
        .input-area {
            padding: 20px;
            border-top: 1px solid #eee;
            background: white;
        }
        .input-group {
            display: flex;
            gap: 10px;
        }
        input[type="text"] {
            flex: 1;
            padding: 12px 16px;
            border: 2px solid #007bff;
            border-radius: 25px;
            font-size: 16px;
            outline: none;
        }
        input[type="text"]:focus {
            border-color: #0056b3;
        }
        button {
            padding: 12px 24px;
            background: #007bff;
            color: white;
            border: none;
            border-radius: 25px;
            cursor: pointer;
            font-size: 16px;
            transition: background 0.3s;
        }
        button:hover {
            background: #0056b3;
        }
        .typing {
            font-style: italic;
            color: #666;
        }
        .welcome-message {
            text-align: center;
            color: #666;
            margin: 10px 0;
        }
    </style>
</head>
<body>
    <div class="container">
        <div class="header">
            <h1>🛫 PacificBlue Airlines</h1>
            <p>Your AI Travel Assistant</p>
        </div>
        
        <div class="chat-container" id="chat">
            <div class="message bot-message">
                <div class="message-bubble bot-bubble">
                    <strong>Hello! I'm your PacificBlue Airlines assistant! ✈️</strong><br><br>
                    I can help you with:<br>
                    • Baggage policies and allowances<br>
                    • Flight changes and bookings<br>
                    • Check-in procedures<br>
                    • Amenities and services<br>
                    • Frequent flyer program<br>
                    • And much more!<br><br>
                    What would you like to know about your travel?
                </div>
            </div>
        </div>
        
        <div class="input-area">
            <div class="input-group">
                <input type="text" id="userInput" placeholder="Ask about baggage, flights, check-in..." onkeypress="handleKeyPress(event)">
                <button onclick="sendMessage()">Send</button>
            </div>
        </div>
    </div>

    <script>
        function sendMessage() {
            const input = document.getElementById('userInput');
            const message = input.value.trim();
            if (message === '') return;
            
            const chat = document.getElementById('chat');
            
            // Add user message
            const userDiv = document.createElement('div');
            userDiv.className = 'message user-message';
            userDiv.innerHTML = '<div class="message-bubble user-bubble">' + message + '</div>';
            chat.appendChild(userDiv);
            
            // Clear input
            input.value = '';
            
            // Show typing indicator
            const typingDiv = document.createElement('div');
            typingDiv.className = 'message bot-message';
            typingDiv.innerHTML = '<div class="message-bubble bot-bubble typing">Searching airline policies...</div>';
            chat.appendChild(typingDiv);
            chat.scrollTop = chat.scrollHeight;
            
            // Send to server
            fetch('/chat', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ message: message })
            })
            .then(response => response.json())
            .then(data => {
                // Remove typing indicator
                chat.removeChild(typingDiv);
                
                // Add bot response
                const botDiv = document.createElement('div');
                botDiv.className = 'message bot-message';
                botDiv.innerHTML = '<div class="message-bubble bot-bubble">' + data.response.replace(/\\n/g, '<br>') + '</div>';
                chat.appendChild(botDiv);
                chat.scrollTop = chat.scrollHeight;
            })
            .catch(error => {
                chat.removeChild(typingDiv);
                const errorDiv = document.createElement('div');
                errorDiv.className = 'message bot-message';
                errorDiv.innerHTML = '<div class="message-bubble bot-bubble">Sorry, I encountered an error. Please try again.</div>';
                chat.appendChild(errorDiv);
                chat.scrollTop = chat.scrollHeight;
            });
        }
        
        function handleKeyPress(event) {
            if (event.key === 'Enter') {
                sendMessage();
            }
        }
        
        // Focus input on load
        document.getElementById('userInput').focus();
    </script>
</body>
</html>
'''

class AirlineAssistantHandler(http.server.SimpleHTTPRequestHandler):
    def do_GET(self):
        if self.path == '/':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            self.wfile.write(WEB_PAGE.encode('utf-8'))
        else:
            self.send_error(404)
    
    def do_POST(self):
        if self.path == '/chat':
            try:
                # Read the request data
                content_length = int(self.headers['Content-Length'])
                post_data = self.rfile.read(content_length)
                request_data = json.loads(post_data.decode('utf-8'))
                
                user_message = request_data.get('message', '')
                print(f"User asked: {user_message}")
                
                # Find best answer
                best_faq = find_best_answer(user_message)
                
                if best_faq:
                    response = f"✈️ **PacificBlue Airlines Information** ✈️\\n\\n{best_faq['answer']}\\n\\n---\\n*Need more help? Call 1-800-PAC-BLUE*"
                else:
                    response = "❓ I don't have specific information about that.\\n\\nPlease contact our customer service at 1-800-PAC-BLUE for detailed assistance, or try asking about:\\n• Baggage policies\\n• Flight changes\\n• Check-in procedures\\n• Amenities\\n• Pet travel policies"
                
                # Send response
                self.send_response(200)
                self.send_header('Content-type', 'application/json')
                self.end_headers()
                self.wfile.write(json.dumps({'response': response}).encode('utf-8'))
                
            except Exception as e:
                print(f"Error: {e}")
                self.send_error(500)
        else:
            self.send_error(404)

def start_server():
    PORT = 8000
    with socketserver.TCPServer(("", PORT), AirlineAssistantHandler) as httpd:
        print(f"🚀 PacificBlue Airlines Assistant is running!")
        print(f"🌐 Open your browser and go to: http://localhost:{PORT}")
        print(f"💡 Try asking: 'What is your baggage policy?' or 'How do I change my flight?'")
        print(f"⏹️  Press Ctrl+C to stop the server")
        
        # Try to open browser automatically
        try:
            webbrowser.open(f'http://localhost:{PORT}')
        except:
            pass
            
        try:
            httpd.serve_forever()
        except KeyboardInterrupt:
            print(f"\\n🛑 Server stopped.")

if __name__ == "__main__":
    start_server()

    