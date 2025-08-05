import os
import importlib
import inspect
from typing import Dict, List, Any
from pathlib import Path
import logging

logger = logging.getLogger(__name__)


class PluginManager:
    def __init__(self):
        self.plugins: Dict[str, Any] = {}
        self.node_types: Dict[str, Any] = {}

    async def load_plugins(self):
        """Load all plugins from the plugins directory"""
        plugins_dir = Path(__file__).parent.parent / "plugins"
        
        if not plugins_dir.exists():
            logger.info("Plugins directory does not exist, creating...")
            plugins_dir.mkdir(exist_ok=True)
            return

        for plugin_file in plugins_dir.glob("*.py"):
            if plugin_file.name.startswith("__"):
                continue
                
            try:
                await self._load_plugin(plugin_file)
            except Exception as e:
                logger.error(f"Failed to load plugin {plugin_file.name}: {str(e)}")

    async def _load_plugin(self, plugin_path: Path):
        """Load a single plugin file"""
        module_name = f"plugins.{plugin_path.stem}"
        spec = importlib.util.spec_from_file_location(module_name, plugin_path)
        
        if spec and spec.loader:
            module = importlib.util.module_from_spec(spec)
            spec.loader.exec_module(module)
            
            # Look for node classes in the module
            for name, obj in inspect.getmembers(module):
                if inspect.isclass(obj) and hasattr(obj, "node_type"):
                    self.node_types[obj.node_type] = obj
                    logger.info(f"Loaded node type: {obj.node_type}")

    def get_node_type(self, node_type: str):
        """Get a node class by type"""
        return self.node_types.get(node_type)

    def get_available_node_types(self) -> List[Dict[str, Any]]:
        """Get list of available node types"""
        types = []
        for node_type, node_class in self.node_types.items():
            types.append({
                "type": node_type,
                "title": getattr(node_class, "title", node_type),
                "description": getattr(node_class, "description", ""),
                "category": getattr(node_class, "category", "general"),
                "inputs": getattr(node_class, "inputs", []),
                "outputs": getattr(node_class, "outputs", [])
            })
        return types

    async def cleanup(self):
        """Cleanup resources"""
        self.plugins.clear()
        self.node_types.clear()