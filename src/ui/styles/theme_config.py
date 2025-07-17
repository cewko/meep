import customtkinter as ctk
from config.settings import app_settings


def setup_theme() -> None:
    """Set up the application theme."""
    ctk.set_appearance_mode(app_settings.ui.theme)
    ctk.set_default_color_theme(app_settings.ui.color_theme)

