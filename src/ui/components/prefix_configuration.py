import logging
import customtkinter as ctk
from typing import Dict, Callable, Optional

from config.settings import PrefixConfig


class PrefixConfigurationWidget:
    """Widget for managing prefix configurations."""
    
    def __init__(
            self, 
            parent: ctk.CTkFrame,
            prefix_id: str,
            config: PrefixConfig,
            on_prefix_change: Callable[[str], None],
            on_hotkey_change: Callable[[str], None]
        ):
        self._logger = logging.getLogger(__name__)
        self._parent = parent
        self._prefix_id = prefix_id
        self._config = config
        self._on_prefix_change = on_prefix_change
        self._on_hotkey_change = on_hotkey_change
        
        self._frame: Optional[ctk.CTkFrame] = None
        self._prefix_var: Optional[ctk.StringVar] = None
        self._widgets: Dict[str, ctk.CTkWidget] = {}
        self._is_enabled = True
        
        self._create_widgets()
    
    def _create_widgets(self) -> None:
        """Create the widget components."""
        # Main frame
        self._frame = ctk.CTkFrame(self._parent, corner_radius=12)
        self._frame.pack(pady=10, padx=15, fill="x")
        
        # Container frame for grid layout
        container = ctk.CTkFrame(self._frame, fg_color="transparent")
        container.pack(expand=True, fill="both", pady=12, padx=20)
        
        # Configure grid
        for i in range(4):
            container.grid_columnconfigure(i, weight=1)
        
        # Label
        label = ctk.CTkLabel(
            container,
            text=f"{self._config.label}:",
            font=ctk.CTkFont(size=13, weight="bold"),
            anchor="center"
        )
        label.grid(row=0, column=0, padx=5, sticky="ew")
        
        # Prefix entry
        self._prefix_var = ctk.StringVar(value=self._config.prefix)
        prefix_entry = ctk.CTkEntry(
            container,
            textvariable=self._prefix_var,
            placeholder_text="Prefix",
            font=ctk.CTkFont(size=12),
            width=70,
            height=32,
            corner_radius=8,
            justify="center"
        )
        prefix_entry.grid(row=0, column=1, padx=5, sticky="ew")
        
        # Hotkey display
        hotkey_label = ctk.CTkLabel(
            container,
            text=f"Key: {self._config.hotkey}",
            font=ctk.CTkFont(size=12, weight="bold"),
            anchor="center",
            fg_color=("gray75", "gray25"),
            corner_radius=6,
            height=28
        )
        hotkey_label.grid(row=0, column=2, padx=5, sticky="ew")
        
        # Change hotkey button
        change_button = ctk.CTkButton(
            container,
            text="Change Key",
            corner_radius=8,
            font=ctk.CTkFont(size=11, weight="bold"),
            height=32,
            width=50,
            command=self._on_change_hotkey_clicked
        )
        change_button.grid(row=0, column=3, padx=5, sticky="ew")
        
        # Store widget references
        self._widgets = {
            'label': label,
            'prefix_entry': prefix_entry,
            'hotkey_label': hotkey_label,
            'change_button': change_button
        }
        
        # Bind prefix change events
        self._prefix_var.trace_add('write', self._on_prefix_var_changed)
    
    def _on_prefix_var_changed(self, *args) -> None:
        """Handle prefix variable changes."""
        new_prefix = self._prefix_var.get()
        self._config.prefix = new_prefix
        self._on_prefix_change(new_prefix)
    
    def _on_change_hotkey_clicked(self) -> None:
        """Handle change hotkey button click."""
        self._on_hotkey_change(self._prefix_id)
    
    def update_hotkey_display(self, hotkey: str) -> None:
        """Update the hotkey display."""
        self._config.hotkey = hotkey
        self._widgets['hotkey_label'].configure(text=f"Key: {hotkey}")
    
    def set_change_button_state(self, text: str, enabled: bool = True) -> None:
        """Set the change button state."""
        self._widgets['change_button'].configure(text=text)
        if not enabled:
            self._widgets['change_button'].configure(state="disabled")
        else:
            self._widgets['change_button'].configure(state="normal")

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable the entire widget."""
        self._is_enabled = enabled
        
        if enabled:
            self._widgets['prefix_entry'].configure(state="normal")
            
            button = self._widgets['change_button']
            button.configure(state="normal")

            # Refresh the change button to fix visual artifacts...
            original_text = button.cget("text")
            button.configure(text=original_text + " ") 
            button.update_idletasks()
            button.configure(text=original_text)
        else:
            self._widgets['prefix_entry'].configure(state="disabled")
            self._widgets['change_button'].configure(state="disabled")

    def destroy(self) -> None:
        """Destroy the widget."""
        if self._frame:
            self._frame.destroy()