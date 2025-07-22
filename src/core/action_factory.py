import os
import importlib
import inspect
from typing import Dict, Type, Optional
from .action import Action
from .logger import Logger

class ActionFactory:
    """Action Factory class, responsible for managing and creating different types of Action instances
    
    This class maintains a mapping from action types to concrete Action classes, and provides the functionality to dynamically create Action instances.
    New Action types can be registered through the register_action method, and Action instances can be created through the create_action method.
    """
    
    _action_types: Dict[str, Type[Action]] = {}
    
    @classmethod
    def register_action(cls, action_type: str, action_class: Type[Action]):
        """Registers a new Action type
        
        Args:
            action_type: The identifier of the Action type
            action_class: The concrete implementation class of the Action
        """
        cls._action_types[action_type] = action_class
    
    @classmethod
    def create_action(cls, action: str, context: str, settings: dict, plugin) -> Optional[Action]:
        """Creates an Action instance
        
        Args:
            action: The identifier of the Action, can be the full action string (e.g., com.xxx.xxx.time)
            context: The context identifier of the Action
            settings: The settings of the Action
            
        Returns:
            Returns the corresponding Action instance if the action_type is successfully registered, otherwise returns None
        """
        try:
            # Extract the action name from the full action string
            action_name = action.split('.')[-1]
            
            action_class = cls._action_types.get(action_name)
            if action_class:
                action_instance = action_class(action, context, settings, plugin)
                if not isinstance(action_instance, Action):
                    Logger.error(f"Created instance is not an Action type: {action_name}")
                    return None
                return action_instance
            else:
                Logger.error(f"Action type not found: {action_name}")
            return None
        except Exception as e:
            Logger.error(f"Error creating action {action}: {str(e)}")
            return None

    @classmethod
    def scan_and_register_actions(cls):
        """Scans the actions directory and automatically registers all Action types"""
        import sys
        import traceback

        # Get the correct actions directory path
        if getattr(sys, 'frozen', False):
            # If it's a bundled environment, use sys._MEIPASS
            base_path = sys._MEIPASS
            # In a bundled environment, look for the actions directory under src
            actions_dir = os.path.join(base_path, 'src', 'actions')
        else:
            # Use a relative path in the development environment
            actions_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), 'actions')
        if not os.path.exists(actions_dir):
            Logger.error(f"Actions directory not found: {actions_dir}")
            return

        # Add the src directory to the Python path
        src_dir = os.path.dirname(actions_dir)
        if src_dir not in sys.path:
            sys.path.insert(0, src_dir)

        for file_name in os.listdir(actions_dir):
            if file_name.endswith('.py') and not file_name.startswith('__'):
                module_name = file_name[:-3]  # Remove the .py suffix
                
                try:
                    module = importlib.import_module(f'actions.{module_name}')
                    Logger.info(f"Loading action module: {module_name}")
                    for name, obj in inspect.getmembers(module):
                        if (inspect.isclass(obj) and 
                            issubclass(obj, Action) and 
                            obj != Action):
                            action_type = module_name.lower()
                            cls.register_action(action_type, obj)
                            Logger.info(f"Successfully registered action: {action_type} -> {obj.__name__}")
                            Logger.info(f"Registered action types: {cls._action_types}")
                except Exception as e:
                    import traceback
                    Logger.error(f"Error loading action module {module_name}: {str(e)}")
                    Logger.error(traceback.format_exc())

# Automatically scan and register all Action types
ActionFactory.scan_and_register_actions()