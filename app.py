from flask import Flask, render_template, request, jsonify
from Crewai_agents import Multiagentsystem
import pyodbc
from datetime import datetime

app = Flask(__name__)

DB_CONNECTION_STRING = 'Driver={ODBC Driver 17 for SQL Server};Server=<your_server>;Database=<your_database>;Trusted_Connection=yes;'

def get_chat_history(chat_id, limit=5):
    """Fetch last N chats for a specific chat_id from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('''
            SELECT Question, response FROM IncidentChatHistory 
            WHERE ChatID = ? 
            ORDER BY DateTime ASC
            OFFSET 0 ROWS FETCH NEXT ? ROWS ONLY
        ''', (chat_id, limit))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        history = []
        for row in rows:
            history.append({
                'question': row[0],
                'response': row[1]
            })
        
        return history
    except Exception as e:
        print(f"Database error: {str(e)}")
        return []


def format_chat_context(chat_history):
    """Format chat history as context string"""
    if not chat_history:
        return ""
    
    context = "chat history:\n\n"
    for idx, chat in enumerate(chat_history):
        context += f"\nQuestion: {chat['question']}\nResponse: {chat['response']}\n"
    
    return context


def save_to_database(chat_id, question, response):
    """Save chat history to SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('''
            INSERT INTO IncidentChatHistory (ChatID, Question, response, DateTime)
            VALUES (?, ?, ?, ?)
        ''', (chat_id, question, response, datetime.now()))
        
        conn.commit()
        cursor.close()
        conn.close()
        print(f"Chat {chat_id} saved to database")
        return True
    except Exception as e:
        print(f"Database error: {str(e)}")
        return False


@app.route('/')
def home():
    return render_template('home.html')

@app.route('/app')
def app_index():
    return render_template('index.html')

@app.route('/get-conversations', methods=['GET'])
def get_conversations():
    """Fetch all conversations from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('SELECT DISTINCT ChatID, Question, response, DateTime FROM IncidentChatHistory ORDER BY DateTime DESC')
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        conversations = []
        for row in rows:
            conversations.append({
                'chatId': row[0],
                'question': row[1],
                'response': row[2],
                'dateTime': row[3].isoformat() if row[3] else None
            })
        
        return jsonify(conversations)
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/get-chat/<chat_id>', methods=['GET'])
def get_chat(chat_id):
    """Fetch specific chat history from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('SELECT Question, response FROM IncidentChatHistory WHERE ChatID = ? ORDER BY DateTime ASC', (chat_id,))
        rows = cursor.fetchall()
        cursor.close()
        conn.close()
        
        messages = []
        for row in rows:
            messages.append({
                'role': 'user',
                'content': row[0]
            })
            messages.append({
                'role': 'assistant',
                'content': row[1],
            })
        
        return jsonify({'messages': messages})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/delete-chat/<chat_id>', methods=['DELETE'])
def delete_chat(chat_id):
    """Delete a specific chat from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM IncidentChatHistory WHERE ChatID = ?', (chat_id,))
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'Chat deleted'})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500

@app.route('/clear-all', methods=['DELETE'])
def clear_all():
    """Delete all chats from SQL Server"""
    try:
        conn = pyodbc.connect(DB_CONNECTION_STRING)
        cursor = conn.cursor()
        
        cursor.execute('DELETE FROM IncidentChatHistory')
        conn.commit()
        cursor.close()
        conn.close()
        
        return jsonify({'success': True, 'message': 'All conversations cleared'})
    except Exception as e:
        print(f"Database error: {str(e)}")
        return jsonify({'error': str(e)}), 500 

@app.route('/query', methods=['POST'])
def query():
    user_query = request.json.get('query', '')
    chat_id = request.json.get('chatId', '')  # Receive chatId from frontend
    
    if not user_query:
        return jsonify({'error': 'Query cannot be empty'}), 400
    
    if not chat_id:
        return jsonify({'error': 'Chat ID missing'}), 400
    
    try:
        chat_history = get_chat_history(chat_id, limit=5)
        formatted_context = format_chat_context(chat_history)
        query_with_context = f"user query:\n{user_query}\n\n{formatted_context}\n" if formatted_context else f"user query:\n{user_query}"
        
        result = Multiagentsystem(user_query,query_with_context)
        
        # Extract response and process_flow
        response = result.get('response', '')
        process_flow = result.get('process_flow', [])
        print(f"Process Flow: {process_flow}")
        save_to_database(chat_id, user_query, response)
        
        return jsonify({
            'chatId': chat_id,
            'response': response,
            'process_flow': process_flow
        })
    except Exception as e:
        return jsonify({'error': str(e)}), 500

if __name__ == '__main__':
    app.run(debug=True, port=5000)