"""
UI Module - User Interface Components

Smart UI components for the annotation interface.
"""

from .components.canvas import SmartCanvas
from .components.controls import ControlPanel
from .dialogs.dialogs import show_about, show_help

__all__ = ['SmartCanvas', 'ControlPanel', 'show_about', 'show_help']
