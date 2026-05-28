import flet as ft
import flet.canvas as cv
import networkx as nx
import math
from ui.styles import theme_colors

class GraphVisualizer(ft.Container):
    def __init__(self, width=700, height=520):
        self.canvas_width = width
        self.canvas_height = height
        self.node_radius = 26
        self.positions = {}
        self.graph_data = {"nodes": [], "edges": []}
        
        self.canvas = cv.Canvas(
            width=self.canvas_width,
            height=self.canvas_height,
            shapes=[]
        )
        
        self.stack = ft.Stack(
            controls=[self.canvas],
            width=self.canvas_width,
            height=self.canvas_height,
        )
        
        super().__init__(
            content=self.stack,
            width=self.canvas_width + 10,
            height=self.canvas_height + 10,
            bgcolor=theme_colors.visualizer_bg,
            border_radius=16,
            border=theme_colors.panel_border,
            padding=5,
        )

    def set_graph_data(self, graph_data: dict, reset_layout: bool = False):
        if reset_layout:
            self.positions.clear()
        self.graph_data = graph_data
        self.refresh()

    def _calculate_layout(self):
        nodes = self.graph_data.get("nodes", [])
        edges = self.graph_data.get("edges", [])
        
        if not nodes:
            self.positions = {}
            return
            
        # Conservar posiciones previas si el nodo aún existe
        new_positions = {node: self.positions[node] for node in nodes if node in self.positions}
        
        # Filtrar nodos nuevos que requieren ubicación
        nodes_to_position = [node for node in nodes if node not in new_positions]
        if nodes_to_position:
            # Crear un grafo DiGraph temporal para el spring layout
            temp_g = nx.DiGraph()
            temp_g.add_nodes_from(nodes)
            for src, dst, w in edges:
                temp_g.add_edge(src, dst, weight=w)
                
            pos = nx.spring_layout(temp_g, k=1.3, seed=42)
            
            xs = [p[0] for p in pos.values()]
            ys = [p[1] for p in pos.values()]
            min_x, max_x = min(xs) if xs else -1, max(xs) if xs else 1
            min_y, max_y = min(ys) if ys else -1, max(ys) if ys else 1
            
            padding = 65
            for node in nodes:
                if node in new_positions:
                    continue
                x, y = pos[node]
                
                # Normalizar a un rango [0, 1]
                x_norm = (x - min_x) / (max_x - min_x) if max_x != min_x else 0.5
                y_norm = (y - min_y) / (max_y - min_y) if max_y != min_y else 0.5
                
                # Escalar a dimensiones reales del lienzo
                px = padding + x_norm * (self.canvas_width - 2 * padding)
                py = padding + y_norm * (self.canvas_height - 2 * padding)
                new_positions[node] = [px, py]
                
        self.positions = new_positions

    def refresh(self):
        self._calculate_layout()
        
        # Limpiar los controles excepto el Canvas (que siempre está en el fondo)
        self.stack.controls = [self.canvas]
        
        for node in self.graph_data.get("nodes", []):
            if node not in self.positions:
                continue
            x, y = self.positions[node]
            
            def make_drag_handlers(node_name, ctrl):
                start_x = [0.0]
                start_y = [0.0]
                last_update = [0.0]
                
                def on_pan_start(e: ft.DragStartEvent):
                    start_x[0] = self.positions[node_name][0]
                    start_y[0] = self.positions[node_name][1]
                    last_update[0] = 0.0
                    
                def on_pan_update(e: ft.DragUpdateEvent):
                    dx = e.global_delta.x if e.global_delta else 0
                    dy = e.global_delta.y if e.global_delta else 0
                    self.positions[node_name][0] = start_x[0] + dx
                    self.positions[node_name][1] = start_y[0] + dy
                    
                    # Restringir movimiento dentro del canvas
                    self.positions[node_name][0] = max(
                        self.node_radius + 5,
                        min(self.canvas_width - self.node_radius - 5, self.positions[node_name][0])
                    )
                    self.positions[node_name][1] = max(
                        self.node_radius + 5,
                        min(self.canvas_height - self.node_radius - 5, self.positions[node_name][1])
                    )
                    
                    # Reposicionar el detector del nodo en el Stack
                    ctrl.left = self.positions[node_name][0] - self.node_radius
                    ctrl.top = self.positions[node_name][1] - self.node_radius
                    
                    # Redibujar las conexiones (aristas) en el Canvas
                    self.draw_edges()
                    
                    import time
                    now = time.time()
                    if now - last_update[0] > 0.016:  # ~60 FPS
                        self.stack.update()
                        last_update[0] = now
                        
                def on_pan_end(e: ft.DragEndEvent):
                    self.stack.update()
                    
                return on_pan_start, on_pan_update, on_pan_end
            
            node_container = ft.Container(
                content=ft.Text(node, size=15, weight=ft.FontWeight.BOLD, color="white"),
                alignment=ft.alignment.Alignment.CENTER,
                width=self.node_radius * 2,
                height=self.node_radius * 2,
                border_radius=self.node_radius,
                gradient=ft.LinearGradient(
                    colors=["#6366F1", "#3B82F6"],
                    begin=ft.alignment.Alignment.TOP_LEFT,
                    end=ft.alignment.Alignment.BOTTOM_RIGHT
                ),
                shadow=ft.BoxShadow(
                    blur_radius=8,
                    color="#4F46E5,0.35",
                    spread_radius=1
                ),
                animate_scale=ft.Animation(150, ft.AnimationCurve.EASE_OUT),
                animate=ft.Animation(150, ft.AnimationCurve.EASE_OUT)
            )
            
            detector_control = ft.GestureDetector(
                content=node_container,
                left=x - self.node_radius,
                top=y - self.node_radius,
            )
            
            on_start, on_update, on_end = make_drag_handlers(node, detector_control)
            detector_control.on_pan_start = on_start
            detector_control.on_pan_update = on_update
            detector_control.on_pan_end = on_end
            node_container.on_hover = lambda e, nc=node_container: self._on_node_hover(e, nc)
            
            self.stack.controls.append(detector_control)
            
        self.draw_edges()
        try:
            self.update()
        except Exception:
            pass

    def _on_node_hover(self, e, container):
        is_hover = e.data == "true"
        container.scale = 1.1 if is_hover else 1.0
        container.shadow = ft.BoxShadow(
            blur_radius=14 if is_hover else 8,
            color="#3B82F6,0.6" if is_hover else "#3B82F6,0.35",
            spread_radius=2 if is_hover else 1
        )
        container.update()

    def _interpolate_color(self, factor: float) -> str:
        color_start = theme_colors.edge_min_color
        color_end = theme_colors.edge_max_color
        
        r1 = int(color_start[1:3], 16)
        g1 = int(color_start[3:5], 16)
        b1 = int(color_start[5:7], 16)
        
        r2 = int(color_end[1:3], 16)
        g2 = int(color_end[3:5], 16)
        b2 = int(color_end[5:7], 16)
        
        r = int(r1 + (r2 - r1) * factor)
        g = int(g1 + (g2 - g1) * factor)
        b = int(b1 + (b2 - b1) * factor)
        
        opacity = 0.25 + 0.70 * factor
        return f"#{r:02X}{g:02X}{b:02X},{opacity:.2f}"

    def draw_edges(self):
        nodes = self.graph_data.get("nodes", [])
        edges = self.graph_data.get("edges", [])
        R = self.node_radius
        
        shapes = []
        
        # Encontrar aristas bidireccionales
        bidirectional = set()
        edge_set = {(src, dst) for src, dst, _ in edges}
        for src, dst in edge_set:
            if (dst, src) in edge_set and src != dst:
                bidirectional.add((src, dst))
                
        # Obtener los pesos min y max del grafo actual
        weights = [e[2] for e in edges] if edges else []
        min_w = min(weights) if weights else 0.0
        max_w = max(weights) if weights else 1.0
        w_range = max_w - min_w
                
        for src, dst, weight in edges:
            if src not in self.positions or dst not in self.positions:
                continue
                
            p_s = self.positions[src]
            p_t = self.positions[dst]
            
            # Calcular factor de peso normalizado o absoluto
            if w_range > 0.01:
                factor = (weight - min_w) / w_range
            else:
                factor = weight
            factor = max(0.0, min(1.0, factor))
            
            # Obtener color y grosor según el factor
            edge_color = self._interpolate_color(factor)
            stroke_w = 1.8 + 0.6 * factor
            
            line_paint = ft.Paint(
                color=edge_color,
                stroke_width=stroke_w,
                style=ft.PaintingStyle.STROKE
            )
            
            arrow_paint = ft.Paint(
                color=edge_color,
                style=ft.PaintingStyle.FILL
            )
            
            text_paint = ft.Paint(
                color=theme_colors.text_sub,
                style=ft.PaintingStyle.FILL
            )
            
            if src == dst:
                # Bucle a sí mismo (self-loop)
                x, y = p_s
                x_start = x - R * 0.5
                y_start = y - R * 0.866
                x_end = x + R * 0.5
                y_end = y - R * 0.866
                
                pc_x = x
                pc_y = y - 2.2 * R
                
                shapes.append(
                    cv.Path(
                        elements=[
                            cv.Path.MoveTo(x_start, y_start),
                            cv.Path.QuadraticTo(pc_x, pc_y, x_end, y_end)
                        ],
                        paint=line_paint
                    )
                )
                
                # Cabeza de flecha
                dx = x_end - pc_x
                dy = y_end - pc_y
                d = math.sqrt(dx*dx + dy*dy)
                ux = dx / d if d > 0 else 1
                uy = dy / d if d > 0 else 0
                vx = -uy
                vy = ux
                
                arrow_L = 8
                arrow_W = 4
                
                base_x = x_end - arrow_L * ux
                base_y = y_end - arrow_L * uy
                p1_x = base_x + arrow_W * vx
                p1_y = base_y + arrow_W * vy
                p2_x = base_x - arrow_W * vx
                p2_y = base_y - arrow_W * vy
                
                shapes.append(
                    cv.Path(
                        elements=[
                            cv.Path.MoveTo(x_end, y_end),
                            cv.Path.LineTo(p1_x, p1_y),
                            cv.Path.LineTo(p2_x, p2_y),
                            cv.Path.LineTo(x_end, y_end)
                        ],
                        paint=arrow_paint
                    )
                )
                
                shapes.append(
                    cv.Text(
                        x=pc_x,
                        y=pc_y - 12,
                        value=f"{weight:.1f}",
                        style=ft.TextStyle(size=10, color=theme_colors.text_sub),
                        alignment=ft.alignment.Alignment.CENTER
                    )
                )
            else:
                # Arista entre nodos distintos
                x_s, y_s = p_s
                x_t, y_t = p_t
                
                dx = x_t - x_s
                dy = y_t - y_s
                d = math.sqrt(dx*dx + dy*dy)
                if d < 1e-3:
                    continue
                    
                ux = dx / d
                uy = dy / d
                vx = -uy
                vy = ux
                
                if (src, dst) in bidirectional:
                    # Dibujar arco curvado
                    h = 24  # Altura del Bezier
                    mid_x = (x_s + x_t) / 2
                    mid_y = (y_s + y_t) / 2
                    pc_x = mid_x + h * vx
                    pc_y = mid_y + h * vy
                    
                    dx_start = pc_x - x_s
                    dy_start = pc_y - y_s
                    d_start = math.sqrt(dx_start**2 + dy_start**2)
                    ux_start = dx_start / d_start if d_start > 0 else ux
                    uy_start = dy_start / d_start if d_start > 0 else uy
                    
                    dx_end = x_t - pc_x
                    dy_end = y_t - pc_y
                    d_end = math.sqrt(dx_end**2 + dy_end**2)
                    ux_end = dx_end / d_end if d_end > 0 else ux
                    uy_end = dy_end / d_end if d_end > 0 else uy
                    
                    x_start = x_s + R * ux_start
                    y_start = y_s + R * uy_start
                    x_end = x_t - R * ux_end
                    y_end = y_t - R * uy_end
                    
                    shapes.append(
                        cv.Path(
                            elements=[
                                cv.Path.MoveTo(x_start, y_start),
                                cv.Path.QuadraticTo(pc_x, pc_y, x_end, y_end)
                            ],
                            paint=line_paint
                        )
                    )
                    
                    # Cabeza de flecha
                    arrow_L = 10
                    arrow_W = 5
                    vx_end = -uy_end
                    vy_end = ux_end
                    
                    base_x = x_end - arrow_L * ux_end
                    base_y = y_end - arrow_L * uy_end
                    p1_x = base_x + arrow_W * vx_end
                    p1_y = base_y + arrow_W * vy_end
                    p2_x = base_x - arrow_W * vx_end
                    p2_y = base_y - arrow_W * vy_end
                    
                    shapes.append(
                        cv.Path(
                            elements=[
                                cv.Path.MoveTo(x_end, y_end),
                                cv.Path.LineTo(p1_x, p1_y),
                                cv.Path.LineTo(p2_x, p2_y),
                                cv.Path.LineTo(x_end, y_end)
                            ],
                            paint=arrow_paint
                        )
                    )
                    
                    # Posicionar texto de peso
                    label_x = 0.25 * x_start + 0.5 * pc_x + 0.25 * x_end
                    label_y = 0.25 * y_start + 0.5 * pc_y + 0.25 * y_end
                    label_x += 12 * vx
                    label_y += 12 * vy
                    
                    shapes.append(
                        cv.Text(
                            x=label_x,
                            y=label_y - 6,
                            value=f"{weight:.1f}",
                            style=ft.TextStyle(size=11, color=theme_colors.text_sub, weight=ft.FontWeight.BOLD),
                            alignment=ft.alignment.Alignment.CENTER
                        )
                    )
                else:
                    # Dibujar línea recta
                    x_start = x_s + R * ux
                    y_start = y_s + R * uy
                    x_end = x_t - R * ux
                    y_end = y_t - R * uy
                    
                    shapes.append(
                        cv.Line(x_start, y_start, x_end, y_end, paint=line_paint)
                    )
                    
                    # Cabeza de flecha
                    arrow_L = 10
                    arrow_W = 5
                    base_x = x_end - arrow_L * ux
                    base_y = y_end - arrow_L * uy
                    p1_x = base_x + arrow_W * vx
                    p1_y = base_y + arrow_W * vy
                    p2_x = base_x - arrow_W * vx
                    p2_y = base_y - arrow_W * vy
                    
                    shapes.append(
                        cv.Path(
                            elements=[
                                cv.Path.MoveTo(x_end, y_end),
                                cv.Path.LineTo(p1_x, p1_y),
                                cv.Path.LineTo(p2_x, p2_y),
                                cv.Path.LineTo(x_end, y_end)
                            ],
                            paint=arrow_paint
                        )
                    )
                    
                    # Posicionar texto de peso
                    mid_x = (x_start + x_end) / 2
                    mid_y = (y_start + y_end) / 2
                    label_x = mid_x + 12 * vx
                    label_y = mid_y + 12 * vy
                    
                    shapes.append(
                        cv.Text(
                            x=label_x,
                            y=label_y - 6,
                            value=f"{weight:.1f}",
                            style=ft.TextStyle(size=11, color=theme_colors.text_sub, weight=ft.FontWeight.BOLD),
                            alignment=ft.alignment.Alignment.CENTER
                        )
                    )
                    
        self.canvas.shapes = shapes
