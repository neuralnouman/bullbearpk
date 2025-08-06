#!/usr/bin/env python3
"""
AI Assistant Routes for BullBearPK
==================================

API endpoints for AI assistant chat functionality using Groq API:
1. Chat with AI assistant
2. Get chat history
3. Clear chat history
"""

import os
import logging
from flask import Blueprint, jsonify, request
from groq import Groq
from datetime import datetime
import json

logger = logging.getLogger(__name__)
ai_assistant_routes = Blueprint('ai_assistant_routes', __name__)

# Initialize Groq client
GROQ_API_KEY = "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"
client = Groq(api_key=GROQ_API_KEY)

# System prompt for the AI assistant
SYSTEM_PROMPT = """You are an AI investment assistant for BullBearPK, a Pakistani stock market investment platform. 

Your role is to help users with:
1. Investment advice and recommendations
2. Market analysis and insights
3. Portfolio management guidance
4. Risk assessment and management
5. Stock research and analysis
6. Investment strategy planning

Key guidelines:
- Focus on Pakistani stock market (PSX)
- Provide practical, actionable advice
- Consider user's risk tolerance and investment goals
- Be informative but not overly technical
- Always mention that you're not providing financial advice
- Encourage users to do their own research
- Be helpful, friendly, and professional

Current context: You're helping users navigate the Pakistani stock market and make informed investment decisions."""

@ai_assistant_routes.route('/chat', methods=['POST'])
def chat_with_assistant():
    """
    Chat with AI assistant
    
    Request Body:
    {
        "message": "What stocks should I invest in?",
        "user_id": "user123",
        "chat_history": [
            {
                "role": "user",
                "content": "Hello"
            },
            {
                "role": "assistant", 
                "content": "Hi! How can I help you with your investments?"
            }
        ]
    }
    
    Returns:
    {
        "success": true,
        "message": "AI response",
        "timestamp": "2025-01-23T10:30:00Z"
    }
    """
    try:
        data = request.json
        user_message = data.get('message', '')
        user_id = data.get('user_id', 'default_user')
        chat_history = data.get('chat_history', [])
        
        if not user_message.strip():
            return jsonify({
                'success': False,
                'message': 'Please provide a message'
            }), 400
        
        logger.info(f"Processing chat message for user {user_id}: {user_message[:50]}...")
        
        # Prepare messages for Groq
        messages = [{"role": "system", "content": SYSTEM_PROMPT}]
        
        # Add chat history (limit to last 10 messages to avoid token limits)
        for msg in chat_history[-10:]:
            messages.append({
                "role": msg.get("role", "user"),
                "content": msg.get("content", "")
            })
        
        # Add current user message
        messages.append({"role": "user", "content": user_message})
        
        # Call Groq API
        chat_completion = client.chat.completions.create(
            messages=messages,
            model="llama3-8b-8192",  # Using Llama 3.1 8B model
            temperature=0.7,
            max_tokens=1000,
            top_p=1,
            stream=False
        )
        
        ai_response = chat_completion.choices[0].message.content
        
        logger.info(f"AI response generated for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': ai_response,
            'timestamp': datetime.now().isoformat(),
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error in AI assistant chat: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error processing your message: {str(e)}'
        }), 500

@ai_assistant_routes.route('/chat/history', methods=['GET'])
def get_chat_history():
    """
    Get chat history for a user
    
    Query Parameters:
    - user_id: User ID
    - limit: Number of messages to return (default: 50)
    
    Returns:
    {
        "success": true,
        "chat_history": [
            {
                "id": "msg123",
                "role": "user",
                "content": "Hello",
                "timestamp": "2025-01-23T10:30:00Z"
            }
        ]
    }
    """
    try:
        user_id = request.args.get('user_id', 'default_user')
        limit = int(request.args.get('limit', 50))
        
        # For now, return empty history since we're not storing it
        # In a real implementation, you'd fetch from database
        return jsonify({
            'success': True,
            'chat_history': [],
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error getting chat history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error retrieving chat history: {str(e)}'
        }), 500

@ai_assistant_routes.route('/chat/clear', methods=['POST'])
def clear_chat_history():
    """
    Clear chat history for a user
    
    Request Body:
    {
        "user_id": "user123"
    }
    
    Returns:
    {
        "success": true,
        "message": "Chat history cleared"
    }
    """
    try:
        data = request.json
        user_id = data.get('user_id', 'default_user')
        
        # For now, just return success since we're not storing history
        # In a real implementation, you'd clear from database
        logger.info(f"Chat history cleared for user {user_id}")
        
        return jsonify({
            'success': True,
            'message': 'Chat history cleared successfully',
            'user_id': user_id
        }), 200
        
    except Exception as e:
        logger.error(f"Error clearing chat history: {str(e)}", exc_info=True)
        return jsonify({
            'success': False,
            'message': f'Error clearing chat history: {str(e)}'
        }), 500 