import tkinter as tk
from typing import TYPE_CHECKING, List, Optional, Dict, Tuple

from draggable import DraggableWord
from settings import WORDSPACE


class WordSpace(tk.Frame):
    """
    A customizable word sapce with zooming and panning capabilities.
    supports:
    - Dynamic word addition
    - Pivot-based zooming
    - Canvas panning
    - Zoom/POV reset
    """
    
    def __init__(
        self, 
        parent: 'tk.Tk', 
        words: Optional[List[str]] = None, 
        width: int = WORDSPACE['CANVAS']['DEFAULT_WIDTH'], 
        height: int = WORDSPACE['CANVAS']['DEFAULT_HEIGHT']
    ):
        """
        Initialize the WordSpace with optional words and custom dimensions 
        Args:
            parent (tk.Tk): Parent Tkinter window
            words (Optional[List[str]], optional): Initial list of words. Defaults to None.
            width (int, optional): Canvas width. Defaults to 1200.
            height (int, optional): Canvas height. Defaults to 800.
        """

        super().__init__(parent)

        # Attributes
        self.main_window = self.winfo_toplevel()
        self.parent = parent
        self.width = width
        self.height = height
        self.pack()

        # Zoom and offset management
        self.min_scale = WORDSPACE['ZOOM']['MIN_SCALE']  
        self.max_scale = WORDSPACE['ZOOM']['MAX_SCALE']
        self.scale_factor = self.min_scale  
        self.offset_x = width / 2  
        self.offset_y = height / 2  

        # Mouse tracking for zoom
        self.last_mouse_x: Optional[int] = None
        self.last_mouse_y: Optional[int] = None

        # Add highlight mode flag
        self.highlight_mode = False

        # Word management
        self.draggables: List[DraggableWord] = []
        self.original_word_positions: Dict[str, Tuple[float, float]] = {}

        # Create canvas
        self.canvas = tk.Canvas(self, width=width, height=height, bg=WORDSPACE['CANVAS']['BACKGROUND_COLOR'])
        
        # Event bindings
        self._setup_event_bindings()

        # Create and position words
        self.add_words(words or [])

        # Zoom label
        self._create_zoom_label()

        self.canvas.pack()

    def _setup_event_bindings(self) -> None:
        """Set up mouse event bindings for zoom and motion tracking."""
        self.canvas.bind("<MouseWheel>", self.on_mouse_wheel)
        self.canvas.bind("<Motion>", self.on_mouse_move)

    def _create_zoom_label(self) -> None:
        """Create and position the zoom percentage label."""
        self.zoom_label = tk.Label(
            self, 
            text=WORDSPACE['ZOOM']['DISPLAY_FORMAT'].format(0), 
            bg=WORDSPACE['LABELS']['ZOOM_LABEL']['BACKGROUND'], 
            fg=WORDSPACE['LABELS']['ZOOM_LABEL']['FOREGROUND']
        )
        self.zoom_label.place(
            relx=WORDSPACE['LABELS']['ZOOM_LABEL']['RELATIVE_X'], 
            rely=WORDSPACE['LABELS']['ZOOM_LABEL']['RELATIVE_Y'], 
            anchor=WORDSPACE['LABELS']['ZOOM_LABEL']['ANCHOR']
        )

    def on_mouse_move(self, event: tk.Event) -> None:
        """Update the last known mouse position."""
        self.last_mouse_x = event.x
        self.last_mouse_y = event.y

    def on_mouse_wheel(self, event: tk.Event) -> None:
        """Handle mouse wheel zoom events."""
        factor = WORDSPACE['ZOOM']['ZOOM_FACTOR'] if event.delta > 0 else 1/WORDSPACE['ZOOM']['ZOOM_FACTOR']
        self.pivot_zoom(factor)

    def add_words(self, words: List[str]) -> None:
        """Add words to the word space."""
        for i, word in enumerate(words):
            logical_x = WORDSPACE['WORD_PLACEMENT']['INITIAL_X_OFFSET'] + i * WORDSPACE['WORD_PLACEMENT']['INITIAL_X_SPACING']
            logical_y = WORDSPACE['WORD_PLACEMENT']['INITIAL_Y_POSITION']
            
            # Store original position
            self.original_word_positions[word] = (logical_x, logical_y)
            
            self.create_word(logical_x, logical_y, word)

    def create_word(self, logical_x: float, logical_y: float, word: str) -> None:
        """Create a DraggableWord at specified logical coordinates."""
        dw = DraggableWord(self, logical_x, logical_y, word)
        self.draggables.append(dw)

    def pivot_zoom(self, factor: float) -> None:
        """
        Perform a pivot zoom.
        
        Args:
            factor (float): Zoom scaling factor
        """
        if not self.last_mouse_x or not self.last_mouse_y:
            return

        pivot_x, pivot_y = self.last_mouse_x, self.last_mouse_y

        # Logical coordinate conversion
        logical_px = (pivot_x - self.offset_x) / self.scale_factor
        logical_py = (pivot_y - self.offset_y) / self.scale_factor

        # Compute new scale with robust boundary management
        new_scale = max(
            self.min_scale, 
            min(self.max_scale, self.scale_factor * factor)
        )

        # Only proceed if scale actually changed
        if new_scale != self.scale_factor:
            self.scale_factor = new_scale
            
            # Calculate normalized zoom percentage (0-500%)
            scale_range = self.max_scale - self.min_scale
            normalized_scale = (self.scale_factor - self.min_scale) / scale_range
            display_percentage = int(normalized_scale * WORDSPACE['ZOOM']['MAX_ZOOM_PERCENTAGE'])
            
            # Update zoom label
            self.zoom_label.config(
                text=WORDSPACE['ZOOM']['DISPLAY_FORMAT'].format(display_percentage)
            )

            # Advanced pivot alignment
            new_device_x = (logical_px * self.scale_factor) + self.offset_x
            new_device_y = (logical_py * self.scale_factor) + self.offset_y

            self.offset_x += (pivot_x - new_device_x)
            self.offset_y += (pivot_y - new_device_y)
            
            self.update_all_positions()

    def reset_pov(self) -> None:
        """reset POV to show a panoramic of the network."""
        if not self.draggables:
            self._reset_to_default()
            return

        # Compute bounding box
        logical_bounds = self._compute_logical_bounds()
        
        # Intelligent scaling
        self._apply_optimal_scale(logical_bounds)
        
        # Update positions
        self.update_all_positions()

    def toggle_highlight_mode(self):
        """Toggle highlight mode and restore previous highlights"""
        self.highlight_mode = not self.highlight_mode
        
        # Update cursor to indicate mode
        new_cursor = WORDSPACE['INTERACTION']['HIGHLIGHT_CURSOR'] if self.highlight_mode else WORDSPACE['INTERACTION']['DEFAULT_CURSOR']
        self.canvas.config(cursor=new_cursor)
        
        if self.highlight_mode:
            # Restore previous highlights when entering highlight mode
            for word in self.draggables:
                word.restore_highlight_state()
                
    def _reset_to_default(self) -> None:
        """Reset to default zoom when no words are present"""
        self.scale_factor = 1.0
        self.zoom_label.config(text=f"Zoom: {int(self.scale_factor * 100)}%")
        
        # Reset to center of canvas
        canvas_width = int(self.canvas.cget("width"))
        canvas_height = int(self.canvas.cget("height"))
        self.offset_x = canvas_width / 2
        self.offset_y = canvas_height / 2

    def _compute_logical_bounds(self) -> Dict[str, float]:
        """Compute logical bounds of draggable words"""
        logical_xs = [dw.logical_x for dw in self.draggables]
        logical_ys = [dw.logical_y for dw in self.draggables]
        
        return {
            'min_x': min(logical_xs),
            'max_x': max(logical_xs),
            'min_y': min(logical_ys),
            'max_y': max(logical_ys)
        }

    def _apply_optimal_scale(self, bounds: Dict[str, float]) -> None:
        """Apply optimal scaling based on word distribution."""
        center_x = (bounds['min_x'] + bounds['max_x']) / 2
        center_y = (bounds['min_y'] + bounds['max_y']) / 2
        
        # Reset core parameters
        self.scale_factor = 1.0 
        self.zoom_label.config(text=f"Zoom: {int(self.scale_factor * 100)}%")
        
        # Canvas dimensions
        canvas_width = int(self.canvas.cget("width"))
        canvas_height = int(self.canvas.cget("height"))
        
        # Compute optimal offset
        self.offset_x = canvas_width/2 - (center_x * self.scale_factor)
        self.offset_y = canvas_height/2 - (center_y * self.scale_factor)

    def update_all_positions(self) -> None:
        """
        Update canvas positions for all draggable words.
        Provides a central method for synchronizing word positions.
        """
        for dw in self.draggables:
            dw.update_canvas_position()

    def get_draggable_words(self) -> List[DraggableWord]:
        """Retrieve all draggable words."""
        return self.draggables

    def pan_offset(self, dx: float, dy: float) -> None:
        """Shift offset to allow keyboard navigation."""
        self.offset_x += dx
        self.offset_y += dy 

        self.update_all_positions()

    def clamp_offset(self) -> None:
        """Constrain offset to keep words within visible canvas region."""
        if not self.draggables:
            return  # No words, nothing to clamp
        
        # Compute logical bounds from words
        logical_xs = [dw.logical_x for dw in self.draggables]
        logical_ys = [dw.logical_y for dw in self.draggables]
        
        # Margin computation
        margin_x = self.draggables[0].width / (2 * self.scale_factor) + WORDSPACE['CANVAS']['MARGINS']['SAFETY_MARGIN']
        margin_y = self.draggables[0].height / (2 * self.scale_factor) + WORDSPACE['CANVAS']['MARGINS']['SAFETY_MARGIN']
        
        # Compute allowed logical bounds
        allowed_logical_min_x = min(logical_xs) - margin_x
        allowed_logical_max_x = max(logical_xs) + margin_x
        allowed_logical_min_y = min(logical_ys) - margin_y
        allowed_logical_max_y = max(logical_ys) + margin_y
        
        # Canvas dimensions
        canvas_width = int(self.canvas.cget("width"))
        canvas_height = int(self.canvas.cget("height"))
        
        # Compute offset boundaries
        min_offset_x = canvas_width - (allowed_logical_max_x * self.scale_factor)
        max_offset_x = - (allowed_logical_min_x * self.scale_factor)
        min_offset_y = canvas_height - (allowed_logical_max_y * self.scale_factor)
        max_offset_y = - (allowed_logical_min_y * self.scale_factor)
        
        # Apply clamping
        self.offset_x = min(max(self.offset_x, min_offset_x), max_offset_x)
        self.offset_y = min(max(self.offset_y, min_offset_y), max_offset_y)
