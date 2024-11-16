# routes/chat_routes.py
from flask import Blueprint, request, jsonify
import logging

logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

chat_bp = Blueprint('chat', __name__)

# Initialize chatbot instance
try:
    from services.chatbot import HybridSearchChatbot
    from config import Config
    chatbot = HybridSearchChatbot(Config.OPENAI_API_KEY)
    logger.debug("Chatbot initialized successfully")
except Exception as e:
    logger.error(f"Failed to initialize chatbot: {str(e)}")
    raise

@chat_bp.route('/chat', methods=['POST'])
def chat():
    try:
        data = request.json
        logger.debug(f"Received request data: {data}")
        
        if not data or 'query' not in data:
            logger.error("No query provided in request")
            return jsonify({'error': 'No query provided'}), 400
            
        query = data['query']
        logger.debug(f"Processing query: {query}")
        
        response = chatbot.query(query)
        logger.debug(f"Generated response: {response}")
        
        if not response:
            logger.error("No response generated")
            return jsonify({'error': 'No response generated'}), 500
            
        return jsonify({'response': response})
        
    except Exception as e:
        logger.error(f"Error processing request: {str(e)}", exc_info=True)
        return jsonify({'error': str(e)}), 500