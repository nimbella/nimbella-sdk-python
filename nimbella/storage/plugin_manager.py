from .plugins.abstract_storage_plugin import AbstractStoragePlugin
import sys
import logging
import importlib
from importlib import resources

# Plugin lookup table: Plugin Provider Id -> Plugin Class
PLUGINS = {}

# Return plugin class from provider identifier.
# Loads all local plugins before searching for provider plugin.
def find_plugin(id):
    if not PLUGINS:
        import_plugins()
        register_plugins()

    logging.debug(f'Looking for plugin from identifier: {id}')
    return PLUGINS.get(id)

# Find & import all potential Python plugins under the storage/plugins directory 
def import_plugins(package = "nimbella.storage.plugins"):
    files = resources.contents(package)
    plugins = [f[:-3] for f in files if f.endswith(".py") and f[0] != "_"]
    logging.debug(f'Discovered files in the {package} directory: {plugins}')
    for plugin in plugins:
        importlib.import_module(f"{package}.{plugin}")
        logging.debug(f'Importing potential plugin file: {package}.{plugin}')

# Use registered sub-classes of the abstract plugin class
# to build lookup table from plugin ids to classes.
def register_plugins():
    for sc in AbstractStoragePlugin.__subclasses__():
        plugin_name = sc.id()
        logging.debug(f'Found plugin with provider id: {plugin_name}')
        PLUGINS[plugin_name] = sc
