# app.py

from flask import Flask, request, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from scripts import parse_documents, embed_and_store, query_pipeline

app = Flask(__name__)
app.config['SECRET_KEY'] = 'your-secret-key'  # You can change this as needed

# Enable CORS and Socket.IO
CORS(app)
socketio = SocketIO(app, cors_allowed_origins="*")  # Allow all origins for development

@app.route('/process-documents', methods=['POST'])
def process_documents():
    try:
        # Step 1: Parse docs
        parse_documents.parse_all()

        # Step 2: Embed and store
        embed_and_store.embed_chunks()

        return jsonify({
            'status': 'success',
            'message': 'Documents processed and embedded successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/query', methods=['POST'])
def query():
    try:
        data = request.get_json()
        if not data or 'query' not in data:
            return jsonify({
                'status': 'error',
                'message': 'Query parameter is required'
            }), 400

        user_query = data['query']
        query_pipeline.query_system(user_query)

        return jsonify({
            'status': 'success',
            'message': 'Query processed successfully'
        })
    except Exception as e:
        return jsonify({
            'status': 'error',
            'message': str(e)
        }), 500

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({
        'status': 'healthy',
        'message': 'Insurance Document Query Assistant is running'
    })

# Socket.IO events (optional but useful for logs/real-time UI)
@socketio.on('connect')
def handle_connect():
    print('Client connected')

@socketio.on('disconnect')
def handle_disconnect():
    print('Client disconnected')

if __name__ == '__main__':
    socketio.run(app, host='0.0.0.0', port=5000, debug=True)
