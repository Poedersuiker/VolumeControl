import json
import threading
import websocket
import logging
import os
import sys
from typing import Any, Dict, List, Optional
from http.server import HTTPServer, BaseHTTPRequestHandler
from .action import Action
from .logger import Logger

class Plugin:
    """Core class for the Stream Dock plugin, responsible for managing WebSocket connections and handling Stream Dock events.
    
    This class maintains the WebSocket connection with the Stream Dock software, handles various events (such as button appearance, disappearance, settings changes, etc.),
    and manages the plugin's Action instances. Each action instance corresponds to a button on the Stream Dock interface.
    """
    
    def __init__(self, port: int, plugin_uuid: str, event: str, info: Dict[str, Any]):
        """Initializes the plugin instance
        
        Args:
            port: WebSocket server port number
            plugin_uuid: The unique identifier of the plugin
            event: The event type
            info: An object containing plugin information
        """
        self.actions: Dict[str, Action] = {}
        self.global_settings: Any = None
        self.plugin_uuid = plugin_uuid
        self.http_server = None
        self.http_server_thread = None
        
        # Start the HTTP server
        # self._start_http_server()
        
        # Initialize WebSocket
        self.ws = websocket.WebSocketApp(
            f'ws://127.0.0.1:{port}',
            on_open=lambda ws: self._on_open(ws, event, plugin_uuid),
            on_message=self._on_message,
            on_error=lambda ws, error: Logger.error(f"WebSocket error: {error}")
        )
        
        # Start WebSocket connection in a separate thread
        threading.Thread(target=self.ws.run_forever, daemon=True).start()
    
    def _on_open(self, ws, event: str, plugin_uuid: str):
        """Callback function when the WebSocket connection is established
        
        Registers the plugin with Stream Dock and sends the initialization event.
        
        Args:
            ws: The WebSocket connection instance
            event: The event type
            plugin_uuid: The plugin UUID
        """        
        Logger.info("WebSocket connected")
        
        ws.send(json.dumps({'event': event, 'uuid': plugin_uuid}))
    
    def _on_message(self, ws, message):
        """Handles WebSocket messages received from Stream Dock
        
        Executes corresponding operations based on the received event type, including:
        - Handling global settings updates
        - Handling button appearance/disappearance events
        - Handling button settings changes
        - Handling title parameter changes
        
        Args:
            ws: The WebSocket connection instance
            message: The received JSON message
        """        
        data = json.loads(message)
        event = data.get('event')
        Logger.info(event)
        if event == 'didReceiveGlobalSettings':
            self.global_settings = data.get('payload', {}).get('settings')
            for action in self.actions.values():
                if hasattr(action, 'on_did_receive_global_settings'):
                    action.on_did_receive_global_settings(self.global_settings)
        elif event == 'willAppear':
            context = data.get('context')
            if context not in self.actions:
                from .action_factory import ActionFactory
                action = ActionFactory.create_action(
                    data.get('action'),
                    context,
                    data.get('payload', {}).get('settings', {}),
                    self
                )
                if action:
                    self.actions[context] = action
                else:
                    Logger.error(f"Failed to create action for context: {context}")
        elif event == 'willDisappear':
            context = data.get('context')
            if context in self.actions:
                action = self.actions[context]
                if hasattr(action, 'on_will_disappear'):
                    action.on_will_disappear()
                del self.actions[context]
        elif event == 'didReceiveSettings':
            context = data.get('context')
            if context in self.actions:
                action = self.actions[context]
                settings = data.get('payload', {}).get('settings', {})
                if hasattr(action, 'on_did_receive_settings'):
                    action.on_did_receive_settings(settings)
                else:
                    action.settings = settings
        elif event == 'titleParametersDidChange':
            context = data.get('context')
            if context in self.actions:
                action = self.actions[context]
                payload = data.get('payload', {})
                if hasattr(action, 'on_title_parameters_did_change'):
                    action.on_title_parameters_did_change(payload)
                else:
                    action.title = payload.get('title', '')
                    action.title_parameters = payload.get('titleParameters', {})
        # Handle context-specific events
        context_events = {
            'keyDown': 'on_key_down',
            'keyUp': 'on_key_up',
            'dialDown': 'on_dial_down',
            'dialUp': 'on_dial_up',
            'dialRotate': 'on_dial_rotate'
        }
        
        if event in context_events:
            context = data.get('context')
            if context in self.actions:
                action = self.actions[context]
                handler = context_events[event]
                if hasattr(action, handler):
                    getattr(action, handler)(data.get('payload', {}))
        # Handle global events
        global_events = {
            'deviceDidConnect': 'on_device_did_connect',
            'deviceDidDisconnect': 'on_device_did_disconnect',
            'applicationDidLaunch': 'on_application_did_launch',
            'applicationDidTerminate': 'on_application_did_terminate',
            'systemDidWakeUp': 'on_system_did_wake_up'
        }
        
        if event in global_events:
            handler = global_events[event]
            for action in self.actions.values():
                if hasattr(action, handler):
                    getattr(action, handler)(data)
        elif event == 'propertyInspectorDidAppear':
            context = data.get('context')
            if context in self.actions:
                action = self.actions[context]
                if hasattr(action, 'on_property_inspector_did_appear'):
                    action.on_property_inspector_did_appear(data)
        elif event == 'propertyInspectorDidDisappear':
            context = data.get('context')
            if context in self.actions:
                action = self.actions[context]
                if hasattr(action, 'on_property_inspector_did_disappear'):
                    action.on_property_inspector_did_disappear(data)
        elif event == 'sendToPlugin':
            context = data.get('context')
            if context in self.actions:
                action = self.actions[context]
                if hasattr(action, 'on_send_to_plugin'):
                    action.on_send_to_plugin(data.get('payload', {}))
    
    def set_global_settings(self, payload: Any):
        """Updates the plugin's global settings
        
        Args:
            payload: The new global settings value
        """        
        self.ws.send(json.dumps({
            'event': 'setGlobalSettings',
            'context': self.plugin_uuid,
            'payload': payload
        }))
        self.global_settings = payload
    
    def get_global_settings(self):
        """Requests to get the plugin's current global settings
        
        After sending the request, the settings value will be returned via a WebSocket message
        """        
        self.ws.send(json.dumps({
            'event': 'getGlobalSettings',
            'context': self.plugin_uuid
        }))
    
    def get_action(self, context: str) -> Optional[Action]:
        """Gets the Action instance for the specified context
        
        Args:
            context: The context identifier of the Action
            
        Returns:
            The Action instance if it exists, otherwise None
        """        
        return self.actions.get(context)
    
    def get_actions(self, action: str) -> List[Action]:
        """Gets a list of all Action instances of the specified type
        
        Args:
            action: The type identifier of the Action
            
        Returns:
            A list of Action instances that match the specified type
        """        
        return [a for a in self.actions.values() if a.action == action]
    
    def _start_http_server(self, port: int = 8000):
        """Starts the HTTPS server
        
        Args:
            port: The HTTPS server port number, defaults to 8000
        """
        import ssl
        import os
        
        class RequestHandler(BaseHTTPRequestHandler):
            def do_GET(self):
                if self.path == '/api':
                    self.send_response(200)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'status': 'ok', 'message': 'API endpoint'}
                    self.wfile.write(json.dumps(response).encode())
                else:
                    self.send_response(404)
                    self.send_header('Content-type', 'application/json')
                    self.end_headers()
                    response = {'status': 'error', 'message': 'Not found'}
                    self.wfile.write(json.dumps(response).encode())
        
        try:
            self.http_server = HTTPServer(('0.0.0.0', port), RequestHandler)
            
            # Configure SSL
            import tempfile
            
            # Create temporary files to store the certificate and key
            cert_file = tempfile.NamedTemporaryFile(delete=False)
            key_file = tempfile.NamedTemporaryFile(delete=False)
            
            # Generate a self-signed certificate and private key
            from cryptography import x509
            from cryptography.x509.oid import NameOID
            from cryptography.hazmat.primitives import hashes
            from cryptography.hazmat.primitives.asymmetric import rsa
            from cryptography.hazmat.primitives import serialization
            from datetime import datetime, timedelta
            
            # Generate private key
            private_key = rsa.generate_private_key(
                public_exponent=65537,
                key_size=2048
            )
            
            # Generate certificate
            subject = issuer = x509.Name([
                x509.NameAttribute(NameOID.COMMON_NAME, u"localhost"),
                x509.NameAttribute(NameOID.ORGANIZATION_NAME, u"Stream Dock Plugin"),
                x509.NameAttribute(NameOID.ORGANIZATIONAL_UNIT_NAME, u"Development"),
                x509.NameAttribute(NameOID.COUNTRY_NAME, u"CN"),
                x509.NameAttribute(NameOID.STATE_OR_PROVINCE_NAME, u"Development State"),
                x509.NameAttribute(NameOID.LOCALITY_NAME, u"Development City"),
            ])
            
            cert = x509.CertificateBuilder().subject_name(
                subject
            ).issuer_name(
                issuer
            ).public_key(
                private_key.public_key()
            ).serial_number(
                x509.random_serial_number()
            ).not_valid_before(
                datetime.utcnow()
            ).not_valid_after(
                datetime.utcnow() + timedelta(days=365)
            ).sign(private_key, hashes.SHA256())
            
            # Write the certificate and private key to temporary files
            cert_file.write(cert.public_bytes(serialization.Encoding.PEM))
            key_file.write(private_key.private_bytes(
                encoding=serialization.Encoding.PEM,
                format=serialization.PrivateFormat.PKCS8,
                encryption_algorithm=serialization.NoEncryption()
            ))
            cert_file.close()
            key_file.close()
            
            # Configure SSL context
            context = ssl.SSLContext(ssl.PROTOCOL_TLS_SERVER)
            context.load_cert_chain(cert_file.name, key_file.name)
            
            # Wrap the socket
            self.http_server.socket = context.wrap_socket(self.http_server.socket, server_side=True)
            
            # Delete temporary files
            os.unlink(cert_file.name)
            os.unlink(key_file.name)
            
            self.http_server_thread = threading.Thread(target=self.http_server.serve_forever, daemon=True)
            self.http_server_thread.start()
            Logger.info(f"HTTPS server started on port {port}")
        except Exception as e:
            Logger.error(f"Failed to start HTTPS server: {e}")
    
    def stop(self):
        """Stops the plugin service
        
        Stops the HTTP server and WebSocket connection
        """
        if self.http_server:
            self.http_server.shutdown()
            self.http_server.server_close()
            Logger.info("HTTP server stopped")