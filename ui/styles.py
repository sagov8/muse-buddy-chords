import flet as ft

class ThemeColors:
    def __init__(self, is_dark=False):
        self.update_theme(is_dark)

    def update_theme(self, is_dark):
        self.is_dark = is_dark
        if is_dark:
            self.page_bg = "#0B0C10"
            self.panel_bg = "#141521"
            self.visualizer_bg = "#1A1C29"
            self.text_title = "#EEF2F6"
            self.text_sub = "#94A3B8"
            self.border = "#25283D"
            self.edge_regular = "#475569"
            self.edge_bidirectional = "#818CF8"
            self.divider = "#25283D"
        else:
            self.page_bg = "#F8FAFC"
            self.panel_bg = "#FFFFFF"
            self.visualizer_bg = "#F1F5F9"
            self.text_title = "#0F172A"
            self.text_sub = "#475569"
            self.border = "#E2E8F0"
            self.edge_regular = "#CBD5E1"
            self.edge_bidirectional = "#4F46E5"
            self.divider = "#E2E8F0"

    @property
    def panel_border(self):
        return ft.Border(
            left=ft.BorderSide(1, self.border),
            top=ft.BorderSide(1, self.border),
            right=ft.BorderSide(1, self.border),
            bottom=ft.BorderSide(1, self.border),
        )

theme_colors = ThemeColors(is_dark=False)