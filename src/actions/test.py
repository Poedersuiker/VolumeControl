from src.core.action import Action
from src.core.logger import Logger

class TestAction(Action):
    def __init__(self, context, settings, plugin):
        super().__init__(context, settings, plugin)
        Logger.info(f"TestAction created for context: {context}")

    def on_key_down(self, payload):
        Logger.info(f"TestAction on_key_down: {payload}")

    def on_key_up(self, payload):
        Logger.info(f"TestAction on_key_up: {payload}")

    def on_will_appear(self, payload):
        Logger.info(f"TestAction on_will_appear: {payload}")

    def on_will_disappear(self, payload):
        Logger.info(f"TestAction on_will_disappear: {payload}")

    def on_did_receive_settings(self, settings):
        Logger.info(f"TestAction on_did_receive_settings: {settings}")

    def on_did_receive_global_settings(self, settings):
        Logger.info(f"TestAction on_did_receive_global_settings: {settings}")

    def on_title_parameters_did_change(self, payload):
        Logger.info(f"TestAction on_title_parameters_did_change: {payload}")

    def on_device_did_connect(self, data):
        Logger.info(f"TestAction on_device_did_connect: {data}")

    def on_device_did_disconnect(self, data):
        Logger.info(f"TestAction on_device_did_disconnect: {data}")

    def on_application_did_launch(self, data):
        Logger.info(f"TestAction on_application_did_launch: {data}")

    def on_application_did_terminate(self, data):
        Logger.info(f"TestAction on_application_did_terminate: {data}")

    def on_system_did_wake_up(self, data):
        Logger.info(f"TestAction on_system_did_wake_up: {data}")

    def on_property_inspector_did_appear(self, data):
        Logger.info(f"TestAction on_property_inspector_did_appear: {data}")

    def on_property_inspector_did_disappear(self, data):
        Logger.info(f"TestAction on_property_inspector_did_disappear: {data}")

    def on_send_to_plugin(self, payload):
        Logger.info(f"TestAction on_send_to_plugin: {payload}")