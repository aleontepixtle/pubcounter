#!/usr/bin/env python3
"""
Main entry point for the Inventory Submission Web Portal.

This file initializes and runs the Flask application with SocketIO support.
"""

import os
from app import create_app, socketio

app = create_app()

if __name__ == '__main__':
    # Get configuration
    host = os.environ.get('FLASK_HOST', '0.0.0.0')
    port = int(os.environ.get('FLASK_PORT', 5000))
    debug = os.environ.get('FLASK_ENV') == 'development'
    
    print(f"""
    ╔═══════════════════════════════════════════════════════════╗
    ║  Inventory Submission Portal                              ║
    ║  Running on: http://{host}:{port}                    ║
    ║  Environment: {os.environ.get('FLASK_ENV', 'development'):<35} ║
    ╚═══════════════════════════════════════════════════════════╝
    """)
    
    # Run with SocketIO
    socketio.run(
        app,
        host=host,
        port=port,
        debug=debug,
        use_reloader=debug,
        log_output=True
    )