import logging
import customtkinter as ctk
import threading
from typing import Dict, Optional
import os

from services.voice_service import VoiceService
from ui.components.prefix_configuration import PrefixConfigurationWidget
from ui.components.status_display import StatusDisplay
from ui.styles.theme_config import setup_theme
from config.settings import app_settings, PrefixConfig
from utils.exceptions import MinecraftSTTError


class MinecraftSTTWindow:
    """Main application window."""
    
    def __init__(self):
        self._logger = logging.getLogger(__name__)
        self._voice_service: Optional[VoiceService] = None
        
        # Configuration state
        self._prefix_configs: Dict[str, PrefixConfig] = app_settings.default_prefix_configs.copy()
        self._auto_send_enabled = app_settings.default_auto_send
        
        # UI state
        self._is_running = False
        self._is_binding_hotkey = False
        self._current_binding_prefix: Optional[str] = None
        self._is_model_ready = False
        
        # UI components
        self._root: Optional[ctk.CTk] = None
        self._status_display: Optional[StatusDisplay] = None
        self._prefix_widgets: Dict[str, PrefixConfigurationWidget] = {}
        self._control_buttons: Dict[str, ctk.CTkButton] = {}
        
        self._setup_ui()
        self._initialize_voice_service()
    
    def _setup_ui(self) -> None:
        """Set up the user interface."""
        setup_theme()
        
        # Create main window
        self._root = ctk.CTk()
        self._root.title(app_settings.ui.window_title)
        self._root.geometry(f"{app_settings.ui.window_width}x{app_settings.ui.window_height}")
        self._root.resizable(False, False)
        
        if os.path.exists(app_settings.ui.icon_path):
            self._root.after(201, lambda: self._root.iconbitmap(app_settings.ui.icon_path))
        
        # Create main frame
        main_frame = ctk.CTkFrame(self._root, corner_radius=15)
        main_frame.pack(padx=20, pady=20, fill="both", expand=True)
        
        # Title
        title_label = ctk.CTkLabel(
            main_frame,
            text=app_settings.ui.window_title,
            font=ctk.CTkFont(size=24, weight="bold")
        )
        title_label.pack(pady=(20, 10))
        
        # Status display
        self._status_display = StatusDisplay(main_frame, "Initializing...")
        
        # Control buttons
        self._create_control_buttons(main_frame)
        
        # Prefix configuration
        self._create_prefix_configuration(main_frame)
        
        # Bind events
        self._root.bind("<Key>", self._on_key_press)
        self._root.focus_set()
        
        # Initially disable all buttons
        self._set_ui_enabled(False)
        
        self._logger.info("UI setup complete")
    
    def _initialize_voice_service(self) -> None:
        """Initialize the voice service and start model loading."""
        def init_service():
            try:
                # Create hotkey mappings
                hotkey_mappings = {
                    config.hotkey.lower(): config.prefix
                    for config in self._prefix_configs.values()
                }
                
                self._logger.info("Creating voice service...")
                
                # Create voice service
                self._voice_service = VoiceService(
                    hotkey_mappings=hotkey_mappings,
                    status_callback=self._update_status,
                    model_ready_callback=self._on_model_ready,
                    auto_send=self._auto_send_enabled
                )
                
                self._logger.info("Voice service created, starting model initialization...")
                
                # Start model initialization
                self._voice_service.initialize_model()
                
                self._logger.info("Model initialization started")
                
            except Exception as error:
                self._logger.error(f"Failed to initialize voice service: {error}")
                self._update_status(f"Initialization failed: {error}")
                self._set_ui_enabled(True)
        
        # Run initialization in separate thread
        init_thread = threading.Thread(
            target=init_service,
            daemon=True,
            name="ServiceInitializer"
        )
        init_thread.start()
        self._logger.info("Service initialization thread started")
    
    def _on_model_ready(self, is_ready: bool) -> None:
        """Handle model ready callback."""
        self._is_model_ready = is_ready
        
        if is_ready:
            self._logger.info("Speech recognition model is ready")
            self._set_ui_enabled(True)
        else:
            self._logger.error("Speech recognition model failed to load")
            self._update_status("Model loading failed. Please restart the application.")
    
    def _set_ui_enabled(self, enabled: bool) -> None:
        """Enable or disable UI controls."""
        if not self._control_buttons:
            return
            
        state = "normal" if enabled else "disabled"
        
        # Enable/disable control buttons
        for button in self._control_buttons.values():
            button.configure(state=state)
        
        # Enable/disable prefix configuration widgets
        for widget in self._prefix_widgets.values():
            widget.set_enabled(enabled)
    
    def _create_control_buttons(self, parent: ctk.CTkFrame) -> None:
        """Create control buttons."""
        controls_frame = ctk.CTkFrame(parent, corner_radius=10)
        controls_frame.pack(pady=10, padx=20, fill="x")
        
        button_frame = ctk.CTkFrame(controls_frame, fg_color="transparent")
        button_frame.pack(pady=15, padx=40, fill="x")
        
        # Configure grid
        button_frame.grid_columnconfigure(0, weight=1)
        button_frame.grid_columnconfigure(1, weight=1)
        
        # Start/Stop button
        start_button = ctk.CTkButton(
            button_frame,
            text="Start VC",
            corner_radius=10,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._toggle_voice_chat,
            state="disabled"  # Initially disabled
        )
        start_button.grid(row=0, column=0, padx=(0, 10))
        
        # Auto-send toggle button
        auto_send_text = "Auto-Send: ON" if self._auto_send_enabled else "Auto-Send: OFF"
        auto_send_button = ctk.CTkButton(
            button_frame,
            text=auto_send_text,
            corner_radius=10,
            height=40,
            font=ctk.CTkFont(size=12, weight="bold"),
            command=self._toggle_auto_send,
            state="disabled"  # Initially disabled
        )
        auto_send_button.grid(row=0, column=1, padx=(10, 0))
        
        # Update button colors
        self._update_auto_send_button_color(auto_send_button)
        
        # Store button references
        self._control_buttons = {
            'start': start_button,
            'auto_send': auto_send_button
        }
    
    def _create_prefix_configuration(self, parent: ctk.CTkFrame) -> None:
        """Create prefix configuration section."""
        prefix_main_frame = ctk.CTkFrame(parent, height=300, corner_radius=10)
        prefix_main_frame.pack(pady=10, padx=20, fill="x")
        prefix_main_frame.pack_propagate(False)
        
        # Title
        ctk.CTkLabel(
            prefix_main_frame,
            text="Prefix Configurations:",
            font=ctk.CTkFont(size=16, weight="bold")
        ).pack(pady=(15, 10))
        
        # Create prefix widgets
        for prefix_id, config in self._prefix_configs.items():
            widget = PrefixConfigurationWidget(
                prefix_main_frame,
                prefix_id,
                config,
                lambda new_prefix, pid=prefix_id: self._on_prefix_changed(pid, new_prefix),
                self._start_hotkey_binding
            )
            self._prefix_widgets[prefix_id] = widget
    
    def _toggle_voice_chat(self) -> None:
        """Toggle voice chat on/off."""
        if not self._is_model_ready:
            self._update_status("Cannot start: Speech recognition model not ready")
            return
            
        if not self._is_running:
            self._start_voice_chat()
        else:
            self._stop_voice_chat()
    
    def _start_voice_chat(self) -> None:
        """Start voice chat service."""
        if not self._voice_service or not self._is_model_ready:
            self._update_status("Cannot start: Voice service not ready")
            return
            
        try:
            # Start voice service
            self._voice_service.start()
            
            # Update UI
            self._is_running = True
            self._control_buttons['start'].configure(
                text="Stop VC",
                fg_color="#800020",
                hover_color="#99182C"
            )
            
        except Exception as error:
            self._logger.error(f"Error starting voice chat: {error}")
            self._update_status(f"Error: {str(error)}")
    
    def _stop_voice_chat(self) -> None:
        """Stop voice chat service."""
        if self._voice_service:
            self._voice_service.stop()
        
        # Update UI
        self._is_running = False
        self._control_buttons['start'].configure(
            text="Start VC",
            fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
            hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"]
        )
        self._update_status("Stopped")
    
    def _toggle_auto_send(self) -> None:
        """Toggle auto-send feature."""
        self._auto_send_enabled = not self._auto_send_enabled
        
        # Update button
        button = self._control_buttons['auto_send']
        if self._auto_send_enabled:
            button.configure(text="Auto-Send: ON")
            status_msg = "Auto-send enabled. Messages will be sent automatically"
        else:
            button.configure(text="Auto-Send: OFF")
            status_msg = "Auto-send disabled. Messages will open in chat for editing"
        
        self._update_auto_send_button_color(button)
        self._update_status(status_msg)
        
        # Update service if running
        if self._voice_service:
            self._voice_service.set_auto_send(self._auto_send_enabled)
    
    def _update_auto_send_button_color(self, button: ctk.CTkButton) -> None:
        """Update auto-send button color based on state."""
        if self._auto_send_enabled:
            button.configure(
                fg_color=ctk.ThemeManager.theme["CTkButton"]["fg_color"],
                hover_color=ctk.ThemeManager.theme["CTkButton"]["hover_color"]
            )
        else:
            button.configure(
                fg_color="#d63384",
                hover_color="#e91e63"
            )
    
    def _on_prefix_changed(self, prefix_id: str, new_prefix: str) -> None:
        """Handle prefix configuration changes."""
        if prefix_id in self._prefix_configs:
            self._prefix_configs[prefix_id].prefix = new_prefix
            self._logger.info(f"Prefix {prefix_id} changed to: '{new_prefix}'")
            
            # Update service if running
            if self._voice_service:
                self._update_service_hotkey_mappings()
    
    def _start_hotkey_binding(self, prefix_id: str) -> None:
        """Start hotkey binding process."""
        if self._is_running:
            self._update_status("Stop voice chat first to change hotkeys")
            return
        
        self._is_binding_hotkey = True
        self._current_binding_prefix = prefix_id
        
        # Update widget state
        widget = self._prefix_widgets[prefix_id]
        widget.set_change_button_state("Press key...", enabled=False)
        
        config = self._prefix_configs[prefix_id]
        self._update_status(f"Press a key to set as hotkey for {config.label}...")
        
        # Focus window to receive key events
        self._root.focus_force()
    
    def _on_key_press(self, event) -> None:
        """Handle key press events for hotkey binding."""
        if not self._is_binding_hotkey or not self._current_binding_prefix:
            return
        
        prefix_id = self._current_binding_prefix
        new_hotkey = event.keysym.upper()
        
        # Check for conflicts
        for pid, config in self._prefix_configs.items():
            if pid != prefix_id and config.hotkey == new_hotkey:
                self._update_status(f"Hotkey {new_hotkey} already in use!")
                self._reset_hotkey_binding(prefix_id)
                return
        
        # Update configuration
        self._prefix_configs[prefix_id].hotkey = new_hotkey
        
        # Update widget
        widget = self._prefix_widgets[prefix_id]
        widget.update_hotkey_display(new_hotkey)
        widget.set_change_button_state("Change Key", enabled=True)
        
        # Update status
        config = self._prefix_configs[prefix_id]
        self._update_status(f"Hotkey for {config.label} changed to: {new_hotkey}")
        
        # Reset binding state
        self._is_binding_hotkey = False
        self._current_binding_prefix = None
        
        # Update service if running
        if self._voice_service:
            self._update_service_hotkey_mappings()
        
        self._logger.info(f"Hotkey for {prefix_id} changed to: {new_hotkey}")
    
    def _reset_hotkey_binding(self, prefix_id: str) -> None:
        """Reset hotkey binding state."""
        widget = self._prefix_widgets[prefix_id]
        widget.set_change_button_state("Change Key", enabled=True)
        
        self._is_binding_hotkey = False
        self._current_binding_prefix = None
    
    def _update_service_hotkey_mappings(self) -> None:
        """Update hotkey mappings in the voice service."""
        if not self._voice_service:
            return
        
        hotkey_mappings = {
            config.hotkey.lower(): config.prefix
            for config in self._prefix_configs.values()
        }
        
        self._voice_service.update_hotkey_mappings(hotkey_mappings)
    
    def _update_status(self, message: str) -> None:
        """Update status display."""
        if self._status_display:
            self._status_display.update_status(message)
        
        self._logger.info(f"Status: {message}")
    
    def _on_closing(self) -> None:
        """Handle window closing event."""
        self._logger.info("Application closing")
        if self._is_running:
            self._stop_voice_chat()
        
        # Clean up UI components
        for widget in self._prefix_widgets.values():
            widget.destroy()
        
        if self._status_display:
            self._status_display.destroy()
        
        if self._root:
            self._root.destroy()
    
    def run(self) -> None:
        """Run the application."""
        self._logger.info("Starting Minecraft-STT GUI")
        
        if not self._root:
            raise MinecraftSTTError("UI not initialized")
        
        # Set up window close handler
        self._root.protocol("WM_DELETE_WINDOW", self._on_closing)
        
        # Start main loop
        self._root.mainloop()