# """
# Socket Server Module

# This module provides WebSocket functionality for real-time communication.
# It is used for the live chat feature.
# """

# import os
# import logging
# import json
# from typing import Dict, Any, List, Optional

# # Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
# logger = logging.getLogger(__name__)

# # Try to import Flask-SocketIO
# try:
#     from flask_socketio import SocketIO, emit
#     SOCKETIO_AVAILABLE = True
# except ImportError:
#     logger.warning("Flask-SocketIO not available. Live chat feature will be disabled.")
#     SOCKETIO_AVAILABLE = False

# # Global variables
# socketio = None

# def init_socketio(app):
#     """Initialize Flask-SocketIO with the Flask app."""
#     global socketio
    
#     if not SOCKETIO_AVAILABLE:
#         logger.warning("Flask-SocketIO not available. Live chat feature will be disabled.")
#         return None
    
#     try:
#         # Initialize Flask-SocketIO
#         socketio = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
        
#         # Register event handlers
#         @socketio.on('connect')
#         def handle_connect():
#             logger.info(f"Client connected: {request.sid}")
        
#         @socketio.on('disconnect')
#         def handle_disconnect():
#             logger.info(f"Client disconnected: {request.sid}")
        
#         @socketio.on('message')
#         def handle_message(data):
#             logger.info(f"Message received: {data}")
#             # Echo the message back to the client
#             emit('message', data)
        
#         @socketio.on('speech_to_text')
#         def handle_speech_to_text(data):
#             logger.info("Speech to text request received")
#             # Process speech to text request
#             # This is handled client-side with Azure Speech SDK
#             pass
        
#         logger.info("Flask-SocketIO initialized successfully.")
#         return socketio
#     except Exception as e:
#         logger.error(f"Error initializing Flask-SocketIO: {str(e)}")
#         return None

# def get_socketio():
#     """Get the Flask-SocketIO instance."""
#     global socketio
#     return socketio

# # Import Flask request object for access to session ID
# if SOCKETIO_AVAILABLE:
#     try:
#         from flask import request
#     except ImportError:
#         logger.warning("Flask request object not available.")
"""
Socket Server Module (Informational)

This module provides WebSocket functionality for real-time communication.
It is used for the live chat feature.

NOTE: If your main `app.py` already initializes a Flask-SocketIO instance
and registers event handlers (as seen in the latest `app.py` version),
this `socket_server.py` file might be redundant or its handlers should be
imported and registered onto the `SocketIO` instance created in `app.py`
rather than creating a new one here.

The example below shows how it *could* be structured if `app.py` delegates
SocketIO event handling to this module.
"""

import os
import logging
# import json # Not used in this simplified version
from typing import Dict, Any, List, Optional

# Configure logging
# logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s') # Configured in app.py
logger = logging.getLogger(__name__)

# Try to import Flask-SocketIO and Flask's request context
try:
    from flask_socketio import SocketIO, emit, join_room, leave_room # Added join_room, leave_room
    from flask import request # For request.sid
    SOCKETIO_AVAILABLE = True
    logger.info("Flask-SocketIO and Flask request context available for socket_server.py.")
except ImportError:
    logger.warning("Flask-SocketIO or Flask not fully available. Live chat features in socket_server.py might be limited or disabled.")
    SOCKETIO_AVAILABLE = False
    SocketIO = None # Define for type hinting
    emit = None
    join_room = None
    leave_room = None
    request = None


# This module would typically NOT create its own SocketIO instance if app.py does.
# Instead, app.py would pass its 'socketio' instance to a function in this module,
# or this module would just define handlers that app.py imports and registers.

# Example: Functions to register handlers on an existing SocketIO instance
# (This is a conceptual change from your original `init_socketio`)

def register_chat_events(socketio_instance: SocketIO):
    """
    Registers chat-related SocketIO event handlers on the given SocketIO instance.
    This function would be called from app.py, passing its `socketio` object.
    """
    if not SOCKETIO_AVAILABLE or not socketio_instance or not emit or not request or not join_room or not leave_room:
        logger.warning("Cannot register chat events; SocketIO or dependencies unavailable.")
        return

    @socketio_instance.on('connect')
    def handle_connect():
        # This might conflict if app.py also defines a 'connect' handler.
        # Ensure only one primary 'connect' handler or make them distinct.
        logger.info(f"socket_server.py: Client connected: {request.sid if request else 'Unknown SID'}")
        # emit('connection_ack', {'sid': request.sid if request else 'Unknown SID'}) # Example ack

    @socketio_instance.on('disconnect')
    def handle_disconnect():
        logger.info(f"socket_server.py: Client disconnected: {request.sid if request else 'Unknown SID'}")
        # Add logic to handle user leaving rooms, etc.

    @socketio_instance.on('join_chat_room') # More specific event name
    def handle_join_chat_room(data: Dict[str, Any]):
        username = data.get('username', 'Anonymous')
        room = data.get('room', 'general_chat')
        if request:
            join_room(room)
            logger.info(f"socket_server.py: User '{username}' (SID: {request.sid}) joined room '{room}'")
            emit('user_joined_notification', {'username': username, 'room': room, 'message': f'{username} has joined the room.'}, to=room)
        else:
            logger.warning("socket_server.py: 'join_chat_room' received but Flask request context unavailable.")


    @socketio_instance.on('leave_chat_room') # More specific event name
    def handle_leave_chat_room(data: Dict[str, Any]):
        username = data.get('username', 'Anonymous')
        room = data.get('room', 'general_chat')
        if request:
            leave_room(room)
            logger.info(f"socket_server.py: User '{username}' (SID: {request.sid}) left room '{room}'")
            emit('user_left_notification', {'username': username, 'room': room, 'message': f'{username} has left the room.'}, to=room, include_self=False)
        else:
            logger.warning("socket_server.py: 'leave_chat_room' received but Flask request context unavailable.")


    @socketio_instance.on('chat_message_to_server') # More specific event name
    def handle_chat_message(data: Dict[str, Any]):
        room = data.get('room', 'general_chat')
        username = data.get('username', 'Anonymous')
        message_text = data.get('message', '')
        
        logger.info(f"socket_server.py: Message from '{username}' in room '{room}': {message_text}")
        
        # Broadcast the message to others in the room
        emit('new_chat_message', {'username': username, 'text': message_text, 'room': room}, to=room)

    # Example: Speech-to-text related event (if server-side processing was intended)
    # @socketio_instance.on('audio_chunk_for_stt')
    # def handle_audio_chunk(data):
    #     logger.debug(f"socket_server.py: Received audio chunk for STT from {request.sid if request else 'Unknown SID'}")
    #     # Process audio chunk with Azure Speech SDK (if server-side STT)
    #     # This would be complex and require careful handling of audio streams.
    #     # Client-side STT as in your app.py is often simpler for real-time.
    #     pass

    logger.info("socket_server.py: Chat event handlers registered.")

# If you were to use this module to initialize SocketIO (less likely if app.py does it):
# global_socketio_instance = None
# def init_and_get_socketio(app) -> Optional[SocketIO]:
#     global global_socketio_instance
#     if not SOCKETIO_AVAILABLE or not SocketIO:
#         logger.warning("Flask-SocketIO not available. Live chat feature will be disabled.")
#         return None
#     try:
#         global_socketio_instance = SocketIO(app, cors_allowed_origins="*", async_mode='eventlet')
#         register_chat_events(global_socketio_instance) # Register handlers on this new instance
#         logger.info("socket_server.py: Flask-SocketIO initialized and handlers registered.")
#         return global_socketio_instance
#     except Exception as e:
#         logger.error(f"socket_server.py: Error initializing Flask-SocketIO: {str(e)}", exc_info=True)
#         return None
