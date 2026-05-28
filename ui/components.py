import flet as ft
from ui.styles import theme_colors

def border_all(width, color):
    side = ft.BorderSide(width, color)
    return ft.Border(left=side, top=side, right=side, bottom=side)

def progression_row(prog, on_reorder=None):
    controls = []
    
    is_dark = theme_colors.is_dark
    
    # Define color scheme for the chips
    bg_color = "#1E1B4B" if is_dark else "#EEF2FF"          # Soft indigo tint
    border_color = "#4338CA" if is_dark else "#C7D2FE"      # Indigo border
    text_color = "#E0E7FF" if is_dark else "#312E81"        # Dark/light text color
    
    # Drag-over highlight colors
    drag_bg = "#312E81" if is_dark else "#C7D2FE"
    drag_border = "#6366F1" if is_dark else "#4F46E5"

    for i, chord in enumerate(prog):
        # Create the inner chip container
        chip_container = ft.Container(
            content=ft.Text(chord, size=15, weight=ft.FontWeight.BOLD, color=text_color),
            padding=ft.Padding(12, 6, 12, 6),
            bgcolor=bg_color,
            border=border_all(1.5, border_color),
            border_radius=20,
            shadow=ft.BoxShadow(
                spread_radius=0,
                blur_radius=3,
                color="rgba(0,0,0,0.06)" if not is_dark else "rgba(0,0,0,0.2)",
                offset=ft.Offset(0, 1.5),
            ),
            scale=1.0,
            animate_scale=ft.Animation(200, ft.AnimationCurve.EASE_OUT),
        )

        # Hover handler for scale micro-animation
        def make_hover_handler(c):
            def hover_event(e):
                c.scale = 1.05 if e.data == "true" else 1.0
                c.update()
            return hover_event

        chip_container.on_hover = make_hover_handler(chip_container)

        # Drag preview / feedback
        feedback_chip = ft.Container(
            content=ft.Text(chord, size=15, weight=ft.FontWeight.BOLD, color=text_color),
            padding=ft.Padding(12, 6, 12, 6),
            bgcolor=bg_color,
            border=border_all(1.5, border_color),
            border_radius=20,
            opacity=0.75,
        )

        # Placeholder left in original spot when dragging
        placeholder = ft.Container(
            width=50,
            height=30,
            border=border_all(1.5, "#374151" if is_dark else "#E2E8F0"),
            border_radius=20,
            bgcolor="transparent",
        )

        draggable = ft.Draggable(
            group="progression",
            content=chip_container,
            content_feedback=feedback_chip,
            content_when_dragging=placeholder,
            data=i, # Store the source index as draggable's data
        )

        # Setup drag target callbacks to capture source and destination indices
        def make_drag_handlers(target_c, idx):
            def will_accept(e):
                target_c.bgcolor = drag_bg
                target_c.border = border_all(1.5, drag_border)
                target_c.scale = 1.08
                target_c.update()
                
            def leave(e):
                target_c.bgcolor = bg_color
                target_c.border = border_all(1.5, border_color)
                target_c.scale = 1.0
                target_c.update()
                
            def accept(e):
                # Restore original styles immediately
                target_c.bgcolor = bg_color
                target_c.border = border_all(1.5, border_color)
                target_c.scale = 1.0
                target_c.update()
                
                if on_reorder:
                    src_draggable = e.page.get_control(e.src_id)
                    if src_draggable and src_draggable.data is not None:
                        src_idx = src_draggable.data
                        on_reorder(src_idx, idx)
                        
            return will_accept, leave, accept

        wa, le, ac = make_drag_handlers(chip_container, i)

        drag_target = ft.DragTarget(
            group="progression",
            content=draggable,
            on_will_accept=wa,
            on_leave=le,
            on_accept=ac,
        )
        
        controls.append(drag_target)

    return ft.Row(
        controls=controls,
        wrap=True,
        spacing=8,
        run_spacing=8,
    )