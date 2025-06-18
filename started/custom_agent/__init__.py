# This makes custom_agent a Python package
from . import agent
from .agent import root_agent

# Export the root_agent so ADK Web can find it
__all__ = ['root_agent', 'agent']
