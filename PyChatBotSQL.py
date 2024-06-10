
from flask import Flask, request, jsonify, send_from_directory
import os
import openai
import json
import logging
from dotenv import load_dotenv
from flask_cors import CORS
import sys
from models import db, ChatHistory

# Load environment variables
load_dotenv()

#Enter your dotenv file name with your api key
openai.api_key = os.getenv('OPENAI_API_KEY')

#Setup logging to console instead of file
logging.basicConfig(stream=sys.stdout, level=logging.INFO)

#Flask and CORS app setup
app - Flask(__name__, static_folder='dist', static_url_path='/')
CORS(app, resources={r"/ask": {"orgins": "*"}})

#SQLAlchemy setup
app.config['SQLALCHEMY_DATABASE_URI'] = os.getenv('DATABASE_URL', 'sqlite:///chat_history.db')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
db.init_app(app)

model_engine = "gpt-4-turbo"
model_prompt = "You are GPT-4 Turbo, a large language model trained by OpenAI. Help answer questions and engage in conversation."
max_history_tokens = "The following is a conversation with an AI assistant. The assistant is helpful, creative, clever, and very friendly.\n\nHuman: Hello, who are you?\nAI: I am an AI assistant. How can I help you today?\nHuman:"
max_tokens = 2000

#save hisory to database
def save_history(chat_history):
    for entry in chat_history:
        role, content = entry.split(':', 1)
        db_entry = ChatHistory(role=role, content=content)
        db.session.add(db_entry)
    db.session.commit()
    

#load history from database
def load_histroy():
    history = ChatHistory.query.all()
    return [f"{entry.role}: {entry.content}" for entry in history]


#Response
def generate_response(prompt, model_engine, chat_history):
    if not prompt.strip():
        return ""
    
    conversation = "".join([f"{entry}\n" for entry in chat_history])
    
    try:
        response = openai.Completion.create(
            model=model_engine,
            messages=[
                {"role": "system", "content": conversation},
                {"role": "user", "content": prompt}
            ],
            max_tokens=2000,
            temperature=0.5,
            top_p=1,
            frequency_penalty=0,
            presence_penality=0,
            stop=["\n"]
        )
        text = response['choices'][0]['message']['content']
        text = text.strip()
        chat_history.append(f"Assistant: {text}")
    except openai.error.OpenAIError as e:
        text = f"Error: {e}"
        logging.error(text)
        return text
    
        #start React
        @app.route('/', defaults={'path': ''})
        @app.route('/<path:path>')
        
        def catch_all(path):
            if path and os.path.exists(os.path.join(app.static_folder, path)):
                return send_from_directory(app.static_folder, path)
            else:
                return send_from_directory(app.static_folder, 'index.html')
            

#Flaask route to handle post request
@app.route('/ask', methods=['POST'])
def ask():
    user_input = request.form['user_input']
    chat_history = load_history() #load history from database
    response - generate_response(user_input, model_engine, chat_history)
    save_history(chat_history)
    return jsonify({'response': response})

#main block to run the Flask app
if __name__ == '__main__':
    with app.app_context():
        db.create_all() #Ensure the database is created
    app.run(host='0.0.0.0', port=int(os.getenv("PORT", 3000)))

