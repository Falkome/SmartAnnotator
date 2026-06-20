"""
UI Components - Smart Interface Components

Canvas, control panel, and brush tool components for the smart annotation interface.
"""

from .canvas import SmartCanvas
from .controls import ControlPanel
from .brush_tool import BrushTool
from .label_widget import LabelWidget
from .compact_controls import CompactFileControls, CompactToolControls, CompactModelStatus

__all__ = ['SmartCanvas', 'ControlPanel', 'BrushTool', 'LabelWidget', 
          'CompactFileControls', 'CompactToolControls', 'CompactModelStatus']
