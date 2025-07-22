import json
from src.core.action import Action
from src.core.logger import Logger

class Test(Action):
    def __init__(self, action: str, context: str, settings: dict, plugin):
        super().__init__(action, context, settings, plugin)
        # Set up timer to update time every second
        # Verified
        Logger.info(f"[TestAction] Initialized with context {context}")
    
    def on_will_disappear(self):
        # Verified
        # Clear the timer when action disappears
        Logger.info(f"[TestAction] Will disappear for context {self.context}")
    
    def on_did_receive_global_settings(self, settings: dict):
        # Verified
        # Handle global settings update
        Logger.info(f"[TestAction] Received global settings: {settings}")

    def on_key_down(self, payload: dict):
        # Verified
        Logger.info(f"[TestAction] Key down event with payload: {payload}")

    def on_key_up(self, payload: dict):
        # Verified
        self.set_state(1)
        Logger.info(f"[TestAction] Key up event with payload: {payload}")

    def on_dial_down(self, payload: dict):
        # Verified
        Logger.info(f"[TestAction] Dial down event with payload: {payload}")

    def on_dial_up(self, payload: dict):
        # Verified
        Logger.info(f"[TestAction] Dial up event with payload: {payload}")

    def on_dial_rotate(self, payload: dict):
        # Verified
        Logger.info(f"[TestAction] Dial rotate event with payload: {payload}")

    def on_device_did_connect(self, payload: dict):
        # Verified
        Logger.info(f"[TestAction] Device connected with payload: {payload}")

    def on_device_did_disconnect(self, data: dict):
        # Verified
        Logger.info(f"[TestAction] Device disconnected with data: {data}")

    def on_application_did_launch(self, data: dict):
        # Verified
        Logger.info(f"[TestAction] Application launched with data: {data}")

    def on_application_did_terminate(self, data: dict):
        # Verified
        Logger.info(f"[TestAction] Application terminated with data: {data}")

    def on_system_did_wake_up(self, data: dict):
        # Verified
        Logger.info(f"[TestAction] System woke up with data: {data}")

    def on_property_inspector_did_appear(self, data: dict):
        # Verified
        Logger.info(f"[TestAction] Property inspector appeared with data: {data}")

    def on_property_inspector_did_disappear(self, data: dict):
        # Verified
        Logger.info(f"[TestAction] Property inspector disappeared with data: {data}")

    def on_send_to_plugin(self, payload: dict):
        # Verified
        Logger.info(f"[TestAction] Received message from property inspector with payload: {payload}")