import flet as ft

def progression_row(prog):
    return ft.Row(
        controls=[
            ft.Container(
                content=ft.Text(chord, size=18),
                padding=10,
                border=ft.Border(
                    left=ft.BorderSide(1),
                    top=ft.BorderSide(1),
                    right=ft.BorderSide(1),
                    bottom=ft.BorderSide(1),
                ),
                border_radius=8,
                margin=5,
            )
            for chord in prog
        ],
        wrap=True
    )