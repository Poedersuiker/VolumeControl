from src.core.plugin import Plugin
import argparse
import sys
import threading
from src.core.logger import Logger
import time

def main():
    Logger.info("Plugin Start")
    parser = argparse.ArgumentParser(description='Stream Dock Plugin')
    parser.add_argument('-port', type=int, required=True, help='WebSocket port number')
    parser.add_argument('-pluginUUID', type=str, required=True, help='Unique identifier for the plugin')
    parser.add_argument('-registerEvent', type=str, required=True, help='Event type for plugin registration')
    parser.add_argument('-info', type=str, required=True, help='JSON string containing Stream Dock and device information')
    args = parser.parse_args()

    try:
        plugin = Plugin(args.port, args.pluginUUID, args.registerEvent, args.info)
        stop_event = threading.Event()

        def on_close(ws, close_status_code, close_msg):
            Logger.info("Connection closed")
            stop_event.set()

        plugin.ws.on_close = on_close

        Logger.info("Plugin is ready for testing. Press Ctrl+C to exit.")
        # Keep the main thread alive
        while not stop_event.is_set():
            time.sleep(1)

    except KeyboardInterrupt:
        Logger.info("Plugin stopped by user.")
        sys.exit(0)
    except Exception as e:
        Logger.error(f"An error occurred: {e}")
        sys.exit(1)

if __name__ == '__main__':
    main()