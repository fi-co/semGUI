import tkinter as tk
from typing import TYPE_CHECKING, Optional
from settings import DRAGGABLE_WORD, CANVAS_INTERACTION



if TYPE_CHECKING:       # Use TYPE_CHECKING to avoid circular imports
    from wordspace import WordSpace

class DraggableWord:
    """Represents a draggable word item on a canvas, displayed as a circle with text."""

    DEFAULT_WIDTH = DRAGGABLE_WORD['SIZE']['DEFAULT_WIDTH']
    DEFAULT_HEIGHT = DRAGGABLE_WORD['SIZE']['DEFAULT_HEIGHT']
    OVAL_FILL_COLOR = DRAGGABLE_WORD['COLORS']['FILL']
    OVAL_OUTLINE_COLOR = DRAGGABLE_WORD['COLORS']['OUTLINE']
    TEXT_COLOR = DRAGGABLE_WORD['COLORS']['TEXT']
    TEXT_FONT = (DRAGGABLE_WORD['FONT']['FAMILY'], DRAGGABLE_WORD['FONT']['SIZE'], DRAGGABLE_WORD['FONT']['STYLE'])
    OVAL_OUTLINE_WIDTH = DRAGGABLE_WORD['OUTLINE']['DEFAULT_WIDTH']
    HIGHLIGHT_COLOR = DRAGGABLE_WORD['COLORS']['HIGHLIGHT']
    HIGHLIGHT_WIDTH = DRAGGABLE_WORD['OUTLINE']['HIGHLIGHT_WIDTH']
    TAG = DRAGGABLE_WORD['TAGS']['DRAGGABLE']

    def __init__(
        self, 
        parent_space: 'WordSpace', 
        logical_x: float, 
        logical_y: float, 
        word: str, 
        width: int = DEFAULT_WIDTH, 
        height: int = DEFAULT_HEIGHT
    ):
        """
        Initialize a draggable word with given parameters.

        Args:
            parent_space: The parent WordSpace containing this word
            logical_x: Initial x-coordinate (logical space)
            logical_y: Initial y-coordinate (logical space)
            word: Text of the word
            width: Width of the draggable item (default 40)
            height: Height of the draggable item (default 40)
        """
        self.parent_space = parent_space
        self.canvas = parent_space.canvas
        self.word = word
        self.width = width
        self.height = height
        self.is_highlighted = False

        # Store logical center (unscaled)
        self.logical_x = logical_x
        self.logical_y = logical_y

        # Drag state tracking
        self._drag_start_x: Optional[float] = None
        self._drag_start_y: Optional[float] = None

        # Create canvas elements
        self._create_canvas_elements()
        
        # Initial position update
        self.update_canvas_position()

    def _create_canvas_elements(self) -> None:
        """Create the circle with text (word obj) in the canvas."""
        # Create the oval shape
        self.oval_id = self.canvas.create_oval(
            0, 0, 0, 0, 
            fill=self.OVAL_FILL_COLOR, 
            outline=self.OVAL_OUTLINE_COLOR, 
            width=self.OVAL_OUTLINE_WIDTH,
            tags=self.TAG  # Add a tag for easier binding
        )
        
        # Create text label
        self.text_id = self.canvas.create_text(
            0, 0, 
            text=self.word, 
            fill=self.TEXT_COLOR, 
            font=self.TEXT_FONT,
            tags=self.TAG  # Add a tag for easier binding
        )

        # Set up event bindings
        for item_id in (self.oval_id, self.text_id):
            # Drag bindings
            self.canvas.tag_bind(item_id, "<ButtonPress-1>", self._on_click)
            self.canvas.tag_bind(item_id, "<B1-Motion>", self._on_drag_move)
            self.canvas.tag_bind(item_id, "<ButtonRelease-1>", self._on_drag_end)

    def remove_from_canvas(self) -> None:
        """Remove this word."""
        self.canvas.delete(self.oval_id)
        self.canvas.delete(self.text_id)

    def update_canvas_position(self) -> None:
        """Recompute device coordinates from logical coordinates, applying scale factor and offset."""
        sf = self.parent_space.scale_factor
        ox = self.parent_space.offset_x
        oy = self.parent_space.offset_y

        # Device center
        center_x = ox + (self.logical_x * sf)
        center_y = oy + (self.logical_y * sf)

        # Compute bounding box coordinates
        x0 = center_x - self.width/2
        y0 = center_y - self.height/2
        x1 = center_x + self.width/2
        y1 = center_y + self.height/2

        # Update oval and text positions
        self.canvas.coords(self.oval_id, x0, y0, x1, y1)
        self.canvas.coords(self.text_id, center_x, center_y)

    def _on_drag_start(self, event: tk.Event) -> None:
        """
        Record the initial mouse offset for dragging.

        Args:
            event: Tkinter event containing mouse coordinates
        """
        # Current device coords of the oval
        x0, y0, _, _ = self.canvas.coords(self.oval_id)
        self._drag_start_x = event.x - x0
        self._drag_start_y = event.y - y0

    def _on_drag_end(self, event: tk.Event) -> None:
        """
        Handle the end of a drag operation.
        Resets drag state tracking variables.

        Args:
            event: Tkinter event containing final mouse coordinates
        """
        self._drag_start_x = None
        self._drag_start_y = None

    def _on_click(self, event: tk.Event) -> None:
            """Handle clicks based on current mode"""
            if self.parent_space.highlight_mode:
                self._highlight_word()
            else:
                self._on_drag_start(event)

    def _highlight_word(self) -> None:
        """Toggle highlight state of word and store the state"""
        self.is_highlighted = not self.is_highlighted
        
        if self.is_highlighted:
            # Apply highlight
            self.canvas.itemconfig(
                self.oval_id,
                outline=self.HIGHLIGHT_COLOR,
                width=self.HIGHLIGHT_WIDTH
            )
        else:
            # Remove highlight
            self.canvas.itemconfig(
                self.oval_id,
                outline=self.OVAL_OUTLINE_COLOR,
                width=self.OVAL_OUTLINE_WIDTH
            )


    def reset_highlight(self) -> None:
        """Reset highlight state"""
        if hasattr(self, '_original_outline'):
            self.canvas.itemconfig(
                self.oval_id,
                outline=self._original_outline,
                width=self._original_width
            )
        return self.is_highlighted


    def restore_highlight_state(self) -> None:
        """Restore the highlight state when re-entering highlight mode"""
        if self.is_highlighted:
            self.canvas.itemconfig(
                self.oval_id,
                outline=self.HIGHLIGHT_COLOR,
                width=self.HIGHLIGHT_WIDTH
            )

    def _on_drag_move(self, event: tk.Event) -> None:
        """Handle drag motion, disabled in highlight mode"""
        if self.parent_space.highlight_mode or self._drag_start_x is None:
            return  # Do nothing if in highlight mode or not dragging
            
        # Get scale factor and offsets
        sf = self.parent_space.scale_factor
        ox = self.parent_space.offset_x
        oy = self.parent_space.offset_y

        # Get canvas dimensions
        c_width = int(self.canvas.cget("width"))
        c_height = int(self.canvas.cget("height"))

        # Compute new position
        new_x0 = event.x - self._drag_start_x
        new_y0 = event.y - self._drag_start_y
        
        # Calculate new right edge position
        new_x1 = new_x0 + self.width
        new_y1 = new_y0 + self.height

        # Boundary checks
        new_x0 = max(0, min(new_x0, c_width - self.width))
        new_y0 = max(0, min(new_y0, c_height - self.height))
        new_x1 = new_x0 + self.width
        new_y1 = new_y0 + self.height

        # Apply new coordinates
        self.canvas.coords(self.oval_id, new_x0, new_y0, new_x1, new_y1)

        # Update text position
        center_x = (new_x0 + new_x1) / 2
        center_y = (new_y0 + new_y1) / 2
        self.canvas.coords(self.text_id, center_x, center_y)

        # Update logical coordinates
        self.logical_x = (center_x - ox) / sf
        self.logical_y = (center_y - oy) / sf
