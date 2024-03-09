from flask import Flask, render_template, request, jsonify, session, url_for, redirect
from openai import OpenAI
import os
import json
from datetime import datetime



app = Flask(__name__)

# Initialize the OpenAI client
client = OpenAI()

# Set the secret key for session management to something random
app.secret_key = os.urandom(24)

# Define relevant keywords for the case study
RELEVANT_KEYWORDS = [
    "renewable energy", "solar panels", "wind turbines", "rural", "sustainability",
    "planning", "implementation", "community involvement", "environmental impact", "maintenance",
    "energy needs", "feasibility", "funding options", "technological advancements", "long-term sustainability"
]

@app.route('/')
def home():
    session['question_count'] = 0
    return render_template('index.html')


@app.route('/start_chat', methods=['POST'])
def start_chat():
    session['user_name'] = request.form['userName']
    session['user_id'] = request.form['userId']
    # Initialize or reset the chat log if necessary
    session['chat_log'] = []
    # session['chat_log'].append({'user:', session['username'], 'ID:', session['user_Id']})
    return jsonify({'message': 'Chat session started'})




@app.route('/ask', methods=['POST'])
def ask():
    if 'chat_log' not in session:
        session['chat_log'] = []

    user_message = request.form['message']
    is_final_answer = request.form.get('isFinalAnswer') == 'true'
    chat_entry = {
        'user_name': session.get('user_name', 'Unknown User'),
        'user_id': session.get('user_id', 'Unknown ID'),
        'sender': 'user',
        'message': user_message
    }
    # Append the user's message to the session chat log
    session['chat_log'].append(chat_entry)

    if not is_final_answer and not is_question_relevant(user_message):
        bot_response = "Please ask a question that is relevant to the renewable energy project in rural areas."
        session['chat_log'].append({'sender': 'bot', 'message': bot_response})
        return jsonify({"message": bot_response})

    # Your existing logic for handling the message and generating a response
    try:
        system_message = ("You are interviewing a consultant, you are the company in a project about renewable energy."
                          "here is all the information for the case:"
                          "This case study focuses on the development of a renewable energy project "
                          "aimed at providing sustainable, reliable, and cost-effective power solutions "
                          "to rural communities. The project explores the feasibility, planning, "
                          "implementation, and maintenance of renewable energy installations, "
                          "including solar panels and wind turbines, to enhance the energy security "
                          "and improve the quality of life for rural inhabitants. Special attention "
                          "is given to community involvement, environmental impact assessments, "
                          "and the integration of renewable energy sources into existing power grids."
                          "Final note, you are the client, the interview already began be concise and precise"
                          "simulate real-life situation and ignore any irrelevant questions. DON'T GIVE HIM ANSWERS"
                          )
        completion = client.chat.completions.create(
            model="gpt-3.5-turbo",
            messages=[
                {"role": "system", "content": system_message},
                {"role": "user", "content": user_message}
            ]
        )
        if completion.choices:
            bot_response = completion.choices[0].message.content
        else:
            bot_response = "Sorry, I couldn't generate a response."

        # Append the bot's response to the chat log
        session['chat_log'].append({'sender': 'bot', 'message': bot_response})

    except Exception as e:
        print(f"Error generating response from OpenAI: {e}")
        bot_response = "Sorry, I couldn't process your request at the moment."
        session['chat_log'].append({'sender': 'bot', 'message': bot_response})
        return jsonify({"message": bot_response})

    session.modified = True  # Ensure the session is marked as modified
    return jsonify({"message": bot_response})


@app.route('/submit_final')
def submit_final():
    return render_template('submit_final.html')

@app.route('/process_final_answer', methods=['POST'])
def process_final_answer():
    final_answer = request.form['finalAnswer']
    chat_log = session.get('chat_log', [])
    chat_log.append({'sender': 'user', 'message': final_answer, 'final': True})
    session['chat_log'] = chat_log
    save_chat_log_to_file(chat_log)
    return redirect(url_for('confirmation'))

@app.route('/confirmation')
def confirmation():
    # Simple confirmation page indicating successful submission
    return "Thank you for your submission."

def save_chat_log_to_file(chat_log):
    os.makedirs('chat_logs', exist_ok=True)  # Ensure the directory exists
    timestamp = datetime.now().strftime('%Y-%m-%d_%H-%M-%S')
    filename = f"chat_logs/chat_log_{timestamp}.json"
    with open(filename, 'w', encoding='utf-8') as f:
        json.dump(chat_log, f, indent=4)
# I had a small function to compare, canceled.
def is_question_relevant(question):
    question_lower = question.lower()
    # return any(keyword in question_lower for keyword in RELEVANT_KEYWORDS)
    return 1
if __name__ == "__main__":
    app.run(debug=True)