import json
import threading
import websocket
from typing import Any, Dict, List, Optional
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
        
        Executes corresponding operations based on the received event type.
        
        Args:
            ws: The WebSocket connection instance
            message: The received JSON message
        """        
        try:
            data = json.loads(message)
            event = data.get('event')
            Logger.info(f"Received event: {event}")

            event_handlers = {
                'didReceiveGlobalSettings': self._handle_did_receive_global_settings,
                'willAppear': self._handle_will_appear,
                'willDisappear': self._handle_will_disappear,
                'didReceiveSettings': self._handle_did_receive_settings,
                'titleParametersDidChange': self._handle_title_parameters_did_change,
                'keyDown': self._handle_key_down,
                'keyUp': self._handle_key_up,
                'dialDown': self._handle_dial_down,
                'dialUp': self._handle_dial_up,
                'dialRotate': self._handle_dial_rotate,
                'deviceDidConnect': self._handle_device_did_connect,
                'deviceDidDisconnect': self._handle_device_did_disconnect,
                'applicationDidLaunch': self._handle_application_did_launch,
                'applicationDidTerminate': self._handle_application_did_terminate,
                'systemDidWakeUp': self._handle_system_did_wake_up,
                'propertyInspectorDidAppear': self._handle_property_inspector_did_appear,
                'propertyInspectorDidDisappear': self._handle_property_inspector_did_disappear,
                'sendToPlugin': self._handle_send_to_plugin,
            }

            handler = event_handlers.get(event)
            if handler:
                handler(data)
            else:
                Logger.warning(f"No handler for event: {event}")
        except json.JSONDecodeError:
            Logger.error(f"Failed to decode JSON message: {message}")
        except Exception as e:
            Logger.error(f"An error occurred while handling message: {e}")

    def _handle_did_receive_global_settings(self, data: Dict[str, Any]):
        self.global_settings = data.get('payload', {}).get('settings')
        for action in self.actions.values():
            if hasattr(action, 'on_did_receive_global_settings'):
                action.on_did_receive_global_settings(self.global_settings)

    def _handle_will_appear(self, data: Dict[str, Any]):
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

    def _handle_will_disappear(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_will_disappear'):
                action.on_will_disappear()
            del self.actions[context]

    def _handle_did_receive_settings(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            settings = data.get('payload', {}).get('settings', {})
            if hasattr(action, 'on_did_receive_settings'):
                action.on_did_receive_settings(settings)
            else:
                action.settings = settings

    def _handle_title_parameters_did_change(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            payload = data.get('payload', {})
            if hasattr(action, 'on_title_parameters_did_change'):
                action.on_title_parameters_did_change(payload)
            else:
                action.title = payload.get('title', '')
                action.title_parameters = payload.get('titleParameters', {})

    def _handle_key_down(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_key_down'):
                action.on_key_down(data.get('payload', {}))

    def _handle_key_up(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_key_up'):
                action.on_key_up(data.get('payload', {}))

    def _handle_dial_down(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_dial_down'):
                action.on_dial_down(data.get('payload', {}))

    def _handle_dial_up(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_dial_up'):
                action.on_dial_up(data.get('payload', {}))

    def _handle_dial_rotate(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_dial_rotate'):
                action.on_dial_rotate(data.get('payload', {}))

    def _handle_device_did_connect(self, data: Dict[str, Any]):
        for action in self.actions.values():
            if hasattr(action, 'on_device_did_connect'):
                action.on_device_did_connect(data)

    def _handle_device_did_disconnect(self, data: Dict[str, Any]):
        for action in self.actions.values():
            if hasattr(action, 'on_device_did_disconnect'):
                action.on_device_did_disconnect(data)

    def _handle_application_did_launch(self, data: Dict[str, Any]):
        for action in self.actions.values():
            if hasattr(action, 'on_application_did_launch'):
                action.on_application_did_launch(data)

    def _handle_application_did_terminate(self, data: Dict[str, Any]):
        for action in self.actions.values():
            if hasattr(action, 'on_application_did_terminate'):
                action.on_application_did_terminate(data)

    def _handle_system_did_wake_up(self, data: Dict[str, Any]):
        for action in self.actions.values():
            if hasattr(action, 'on_system_did_wake_up'):
                action.on_system_did_wake_up(data)

    def _handle_property_inspector_did_appear(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_property_inspector_did_appear'):
                action.on_property_inspector_did_appear(data)

    def _handle_property_inspector_did_disappear(self, data: Dict[str, Any]):
        context = data.get('context')
        if context in self.actions:
            action = self.actions[context]
            if hasattr(action, 'on_property_inspector_did_disappear'):
                action.on_property_inspector_did_disappear(data)

    def _handle_send_to_plugin(self, data: Dict[str, Any]):
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

    def stop(self):
        """Stops the plugin service
        
        Stops the WebSocket connection
        """
        self.ws.close()
        Logger.info("WebSocket connection closed")