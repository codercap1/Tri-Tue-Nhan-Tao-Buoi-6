import tkinter as tk
from tkinter import messagebox
from tkinter import scrolledtext
from collections import deque
import random
import time


# ============================================================
# CẤU HÌNH BÀI TOÁN 8-PUZZLE
# ============================================================

GOAL_STATE = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

MOVES = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}


# ============================================================
# NODE ĐÚNG THEO SLIDE
# Node = {
#   state: current state,
#   parent: reference to parent node,
#   action: action from parent to reach this node,
#   path_cost: total cost from root
# }
# ============================================================

class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost


# ============================================================
# CÁC HÀM XỬ LÝ TRẠNG THÁI
# ============================================================

def copy_state(state):
    return [row[:] for row in state]


def state_to_tuple(state):
    return tuple(tuple(row) for row in state)


def is_goal(state):
    return state == GOAL_STATE


def find_zero(state):
    for i in range(3):
        for j in range(3):
            if state[i][j] == 0:
                return i, j
    return None


def state_to_string(state):
    result = ""
    for row in state:
        result += str(row) + "\n"
    return result


def is_cycle(node):
    """
    Kiểm tra trạng thái hiện tại có lặp lại trên đường đi từ root đến node không.
    Nếu có thì không expand nữa để tránh vòng lặp.
    """
    current_state = state_to_tuple(node.state)
    parent = node.parent

    while parent is not None:
        if state_to_tuple(parent.state) == current_state:
            return True
        parent = parent.parent

    return False


def expand(node):
    """
    Sinh các node con từ node hiện tại.
    Mỗi lần di chuyển ô trống có chi phí = 1.
    """
    children = []

    zero_i, zero_j = find_zero(node.state)

    for action, (di, dj) in MOVES.items():
        new_i = zero_i + di
        new_j = zero_j + dj

        if 0 <= new_i < 3 and 0 <= new_j < 3:
            new_state = copy_state(node.state)

            new_state[zero_i][zero_j], new_state[new_i][new_j] = (
                new_state[new_i][new_j],
                new_state[zero_i][zero_j]
            )

            child = Node(
                state=new_state,
                parent=node,
                action=action,
                path_cost=node.path_cost + 1
            )

            children.append(child)

    return children


def solution_path(node):
    """
    Truy vết lời giải từ node đích về root.
    """
    path = []

    while node is not None:
        path.append(node)
        node = node.parent

    path.reverse()
    return path


def random_start_state(steps=12):
    """
    Tạo trạng thái ban đầu random nhưng luôn giải được.
    Cách làm: xuất phát từ goal rồi di chuyển ngẫu nhiên nhiều bước.
    """
    current_state = copy_state(GOAL_STATE)
    last_action = None

    opposite = {
        "UP": "DOWN",
        "DOWN": "UP",
        "LEFT": "RIGHT",
        "RIGHT": "LEFT"
    }

    for _ in range(steps):
        temp_node = Node(current_state)
        children = expand(temp_node)

        if last_action is not None:
            children = [
                child for child in children
                if child.action != opposite[last_action]
            ]

        chosen = random.choice(children)
        current_state = chosen.state
        last_action = chosen.action

    return current_state


# ============================================================
# GIAO DIỆN TKINTER
# ============================================================

class PuzzleApp:
    def change_speed(self, value):
        """
        Thanh kéo càng lớn thì thuật toán chạy càng nhanh.
        value: 1 -> 100
        delay_time: 1.00s -> 0.01s
        """
        self.speed_value = int(value)

        max_delay = 1.0
        min_delay = 0.01

        ratio = self.speed_value / 100

        self.delay_time = max_delay - ratio * (max_delay - min_delay)

        self.speed_label.config(
            text=f"Tốc độ giải: {self.speed_value}% | delay: {self.delay_time:.2f}s"
        )
    def __init__(self, root):
        self.root = root
        self.root.title("8-Puzzle IDS - Iterative Deepening Search")
        self.root.geometry("1280x820")
        self.root.minsize(1150, 700)
        self.root.configure(bg="#eef3f9")

        self.start_state = random_start_state(steps=10)

        self.tile_labels = []
        self.goal_labels = []

        self.is_running = False
        self.is_paused = False
        self.speed_value = 35
        self.delay_time = 0.35
        self.max_depth = 25

        self.COLOR_BG = "#eef3f9"
        self.COLOR_PANEL = "#ffffff"
        self.COLOR_BLUE = "#0b2c6b"
        self.COLOR_ORANGE = "#f47c00"
        self.COLOR_DARK = "#1f2937"
        self.COLOR_EMPTY = "#111827"
        self.COLOR_TILE = "#f8fafc"
        self.COLOR_BORDER = "#cbd5e1"

        self.create_widgets()
        self.draw_puzzle(self.start_state)
        self.draw_goal()

    # ========================================================
    # TẠO GIAO DIỆN
    # ========================================================

    def create_widgets(self):
        header = tk.Frame(self.root, bg=self.COLOR_BLUE, height=80)
        header.pack(fill="x")

        title = tk.Label(
            header,
            text="8-PUZZLE - ITERATIVE DEEPENING SEARCH",
            font=("Arial", 24, "bold"),
            bg=self.COLOR_BLUE,
            fg="white"
        )
        title.pack(pady=22)

        body = tk.Frame(self.root, bg=self.COLOR_BG)
        body.pack(fill="both", expand=True, padx=18, pady=16)

        left_panel = tk.Frame(
            body,
            bg=self.COLOR_PANEL,
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        left_panel.pack(side="left", fill="y", padx=(0, 14))

        center_panel = tk.Frame(
            body,
            bg=self.COLOR_PANEL,
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        center_panel.pack(side="left", fill="y", padx=(0, 14))

        right_panel = tk.Frame(
            body,
            bg=self.COLOR_PANEL,
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        right_panel.pack(side="right", fill="both", expand=True)

        # ================= LEFT PANEL =================

        current_title = tk.Label(
            left_panel,
            text="Trạng thái hiện tại",
            font=("Arial", 17, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        current_title.pack(pady=(18, 10))

        self.board_frame = tk.Frame(left_panel, bg=self.COLOR_DARK)
        self.board_frame.pack(padx=22, pady=8)

        for i in range(3):
            row = []
            for j in range(3):
                label = tk.Label(
                    self.board_frame,
                    text="",
                    width=4,
                    height=2,
                    font=("Arial", 26, "bold"),
                    relief="flat",
                    bg=self.COLOR_TILE,
                    fg=self.COLOR_BLUE
                )
                label.grid(row=i, column=j, padx=4, pady=4)
                row.append(label)
            self.tile_labels.append(row)

        info_frame = tk.Frame(left_panel, bg=self.COLOR_PANEL)
        info_frame.pack(pady=8)

        self.depth_label = tk.Label(
            info_frame,
            text="Depth hiện tại: 0",
            font=("Arial", 12, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_BLUE
        )
        self.depth_label.pack(pady=2)

        self.action_label = tk.Label(
            info_frame,
            text="Action: None",
            font=("Arial", 12),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        self.action_label.pack(pady=2)

        self.cost_label = tk.Label(
            info_frame,
            text="Path cost: 0",
            font=("Arial", 12),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        self.cost_label.pack(pady=2)

        self.speed_label = tk.Label(
            info_frame,
            text=f"Tốc độ giải: {self.speed_value}% | delay: {self.delay_time:.2f}s",
            font=("Arial", 12, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_ORANGE
        )
        self.speed_label.pack(pady=6)
        speed_slider_frame = tk.Frame(info_frame, bg=self.COLOR_PANEL)
        speed_slider_frame.pack(pady=6)

        speed_text = tk.Label(
            speed_slider_frame,
            text="Chậm",
            font=("Arial", 9),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        speed_text.grid(row=0, column=0, padx=3)

        self.speed_scale = tk.Scale(
            speed_slider_frame,
            from_=1,
            to=100,
            orient="horizontal",
            length=180,
            showvalue=True,
            command=self.change_speed,
            bg=self.COLOR_PANEL,
            fg=self.COLOR_BLUE,
            troughcolor="#cbd5e1",
            highlightthickness=0
        )
        self.speed_scale.set(self.speed_value)
        self.speed_scale.grid(row=0, column=1, padx=3)

        speed_text_fast = tk.Label(
            speed_slider_frame,
            text="Nhanh",
            font=("Arial", 9),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        speed_text_fast.grid(row=0, column=2, padx=3)

        button_frame = tk.Frame(left_panel, bg=self.COLOR_PANEL)
        button_frame.pack(pady=8)

        self.random_btn = self.create_button(
            button_frame,
            "Random",
            self.random_state,
            row=0,
            column=0
        )

        self.solve_btn = self.create_button(
            button_frame,
            "Giải",
            self.solve_ids,
            row=0,
            column=1
        )

        self.pause_btn = self.create_button(
            button_frame,
            "Tạm dừng",
            self.toggle_pause,
            row=1,
            column=0
        )

        # ================= CENTER PANEL =================

        goal_title = tk.Label(
            center_panel,
            text="Goal State",
            font=("Arial", 17, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        goal_title.pack(pady=(18, 10))

        self.goal_frame = tk.Frame(center_panel, bg=self.COLOR_DARK)
        self.goal_frame.pack(padx=18, pady=8)

        for i in range(3):
            row = []
            for j in range(3):
                label = tk.Label(
                    self.goal_frame,
                    text="",
                    width=3,
                    height=1,
                    font=("Arial", 20, "bold"),
                    relief="flat",
                    bg="#f1f5f9",
                    fg=self.COLOR_BLUE
                )
                label.grid(row=i, column=j, padx=3, pady=3)
                row.append(label)
            self.goal_labels.append(row)

        algorithm_box = tk.Frame(
            center_panel,
            bg="#f8fafc",
            highlightbackground=self.COLOR_BORDER,
            highlightthickness=1
        )
        algorithm_box.pack(padx=18, pady=18, fill="x")

        algo_title = tk.Label(
            algorithm_box,
            text="Thuật toán bám đã dùng",
            font=("Arial", 13, "bold"),
            bg="#f8fafc",
            fg=self.COLOR_ORANGE
        )
        algo_title.pack(pady=(10, 4))

        algo_text = (
            "ITERATIVE-DEEPENING-SEARCH\n"
            "for depth = 0 to ∞ do\n"
            "  result = DEPTH-LIMITED-SEARCH(depth)\n"
            "  if result ≠ cutoff then return result\n\n"
            "DEPTH-LIMITED-SEARCH\n"
            "frontier ← stack with root node\n"
            "while frontier not empty do\n"
            "  node ← POP(frontier)\n"
            "  if IS-GOAL(node.STATE) return node\n"
            "  if DEPTH(node) ≥ limit return cutoff\n"
            "  else if not IS-CYCLE(node)\n"
            "      for each child in EXPAND(node)\n"
            "          add child to frontier"
        )

        algo_label = tk.Label(
            algorithm_box,
            text=algo_text,
            font=("Consolas", 10),
            bg="#f8fafc",
            fg=self.COLOR_DARK,
            justify="left",
            anchor="w"
        )
        algo_label.pack(padx=12, pady=(0, 12), anchor="w")

        legend_box = tk.Frame(center_panel, bg=self.COLOR_PANEL)
        legend_box.pack(padx=18, pady=5, fill="x")

        self.status_label = tk.Label(
            legend_box,
            text="Trạng thái: Sẵn sàng",
            font=("Arial", 12, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_BLUE
        )
        self.status_label.pack(anchor="w", pady=3)

        self.limit_label = tk.Label(
            legend_box,
            text="Depth limit hiện tại: -",
            font=("Arial", 12),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        self.limit_label.pack(anchor="w", pady=3)

        # ================= RIGHT PANEL =================

        log_header = tk.Frame(right_panel, bg=self.COLOR_PANEL)
        log_header.pack(fill="x", padx=14, pady=(14, 4))

        log_title = tk.Label(
            log_header,
            text="Quá trình xét theo từng DEPTH",
            font=("Arial", 17, "bold"),
            bg=self.COLOR_PANEL,
            fg=self.COLOR_DARK
        )
        log_title.pack(side="left")

        self.log_box = scrolledtext.ScrolledText(
            right_panel,
            width=78,
            height=32,
            font=("Consolas", 10),
            bg="#0f172a",
            fg="#e5e7eb",
            insertbackground="white",
            relief="flat",
            padx=12,
            pady=12
        )
        self.log_box.pack(fill="both", expand=True, padx=14, pady=(4, 14))

    def create_button(self, parent, text, command, row, column=0):
        btn = tk.Button(
            parent,
            text=text,
            font=("Arial", 11, "bold"),
            width=16,
            height=1,
            bg=self.COLOR_BLUE,
            fg="white",
            activebackground=self.COLOR_ORANGE,
            activeforeground="white",
            relief="flat",
            command=command,
            cursor="hand2"
        )
        btn.grid(row=row, column=column, padx=5, pady=5)
        return btn

    # ========================================================
    # HIỂN THỊ PUZZLE
    # ========================================================

    def draw_puzzle(self, state):
        for i in range(3):
            for j in range(3):
                value = state[i][j]

                if value == 0:
                    self.tile_labels[i][j].config(
                        text="",
                        bg=self.COLOR_EMPTY,
                        fg="white"
                    )
                else:
                    self.tile_labels[i][j].config(
                        text=str(value),
                        bg=self.COLOR_TILE,
                        fg=self.COLOR_BLUE
                    )

        self.root.update()

    def draw_goal(self):
        for i in range(3):
            for j in range(3):
                value = GOAL_STATE[i][j]

                if value == 0:
                    self.goal_labels[i][j].config(
                        text="",
                        bg=self.COLOR_EMPTY
                    )
                else:
                    self.goal_labels[i][j].config(
                        text=str(value),
                        bg="#f1f5f9",
                        fg=self.COLOR_BLUE
                    )

    def update_node_info(self, node):
        self.depth_label.config(text=f"Depth hiện tại: {node.path_cost}")
        self.action_label.config(text=f"Action: {node.action}")
        self.cost_label.config(text=f"Path cost: {node.path_cost}")
        self.root.update()

    # ========================================================
    # LOG
    # ========================================================

    def log(self, text):
        self.log_box.insert(tk.END, text)
        self.log_box.see(tk.END)
        self.root.update()


    # ========================================================
    # ĐIỀU KHIỂN TỐC ĐỘ / TẠM DỪNG
    # ========================================================

    def toggle_pause(self):
        if not self.is_running:
            return

        self.is_paused = not self.is_paused

        if self.is_paused:
            self.pause_btn.config(text="Tiếp tục")
            self.status_label.config(text="Trạng thái: Đang tạm dừng")
            self.log("\n===== ĐÃ TẠM DỪNG =====\n\n")
        else:
            self.pause_btn.config(text="Tạm dừng")
            self.status_label.config(text="Trạng thái: Đang chạy")
            self.log("\n===== TIẾP TỤC =====\n\n")

    
    def wait_with_pause(self):
        elapsed = 0.0

        while elapsed < self.delay_time:
            self.root.update()

            while self.is_paused:
                self.root.update()
                time.sleep(0.05)

            time.sleep(0.03)
            elapsed += 0.03

    # ========================================================
    # RANDOM TRẠNG THÁI
    # ========================================================

    def random_state(self):
        if self.is_running:
            messagebox.showwarning(
                "Đang chạy",
                "Không thể random khi thuật toán đang chạy."
            )
            return

        self.start_state = random_start_state(steps=12)
        self.draw_puzzle(self.start_state)

        self.depth_label.config(text="Depth hiện tại: 0")
        self.action_label.config(text="Action: None")
        self.cost_label.config(text="Path cost: 0")
        self.limit_label.config(text="Depth limit hiện tại: -")
        self.status_label.config(text="Trạng thái: Đã random trạng thái mới")

        self.log_box.delete("1.0", tk.END)
        self.log("TRẠNG THÁI BAN ĐẦU RANDOM:\n")
        self.log(state_to_string(self.start_state))
        self.log("\n")

    # ========================================================
    # DEPTH-LIMITED SEARCH
    # Bám sát thuật toán:
    # frontier <- stack
    # result <- failure
    # while frontier not empty:
    #   node <- pop(frontier)
    #   if goal return node
    #   if depth >= limit result <- cutoff
    #   elif not cycle:
    #       for child in expand(node):
    #           add child to frontier
    # return result
    # ========================================================

    def depth_limited_search(self, start_state, limit):
        root = Node(
            state=start_state,
            parent=None,
            action=None,
            path_cost=0
        )

        frontier = deque()
        frontier.append(root)

        result = "failure"
        step = 0

        while frontier:
            node = frontier.pop()

            self.log(f"Node xét thứ: {step}\n")
            self.log(f"Action: {node.action}\n")
            self.log(f"Path cost / Depth: {node.path_cost}\n")
            self.log(state_to_string(node.state))
            self.log("\n")

            self.draw_puzzle(node.state)
            self.update_node_info(node)
            self.wait_with_pause()

            step += 1

            # if problem.IS-GOAL(node.STATE) then return node
            if is_goal(node.state):
                self.log("=> Gặp trạng thái đích. Return node.\n\n")
                return node

            # if DEPTH(node) >= limit then result <- cutoff
            if node.path_cost >= limit:
                result = "cutoff"
                self.log("=> Đạt giới hạn depth, không expand node này.\n\n")

            # else if not IS-CYCLE(node) do
            elif not is_cycle(node):
                self.log("=> Không bị cycle, tiến hành EXPAND(node).\n")

                # for each child in EXPAND(problem, node) do
                children = expand(node)

                self.log("Các node con sinh ra:\n")

                # add child to frontier
                for child in children:
                    self.log(f"  Child action: {child.action}\n")
                    self.log(f"  Child depth: {child.path_cost}\n")
                    self.log(state_to_string(child.state))
                    self.log("\n")

                    frontier.append(child)

                self.log("-" * 52 + "\n\n")

            else:
                self.log("=> Bị cycle, bỏ qua node này.\n\n")

        return result

    # ========================================================
    # ITERATIVE DEEPENING SEARCH
    # Bám sát thuật toán:
    # for depth = 0 to infinity:
    #   result = depth_limited_search(problem, depth)
    #   if result != cutoff then return result
    # ========================================================

    def solve_ids(self):
        if self.is_running:
            messagebox.showwarning(
                "Đang chạy",
                "Thuật toán đang chạy."
            )
            return

        self.is_running = True
        self.is_paused = False
        self.pause_btn.config(text="Tạm dừng")
        self.status_label.config(text="Trạng thái: Đang chạy")

        self.log_box.delete("1.0", tk.END)

        self.log("TRẠNG THÁI BAN ĐẦU:\n")
        self.log(state_to_string(self.start_state))
        self.log("\n")

        self.log("TRẠNG THÁI ĐÍCH:\n")
        self.log(state_to_string(GOAL_STATE))
        self.log("\n")

        result = "failure"

        for depth in range(self.max_depth + 1):
            self.limit_label.config(text=f"Depth limit hiện tại: {depth}")

            self.log("=" * 64 + "\n")
            self.log(f"ĐANG XÉT VỚI DEPTH LIMIT = {depth}\n")
            self.log("=" * 64 + "\n\n")

            result = self.depth_limited_search(self.start_state, depth)

            if result != "cutoff" and result != "failure":
                break

            self.log(f"Không tìm thấy lời giải ở depth limit = {depth}\n\n")

        self.is_running = False
        self.is_paused = False
        self.pause_btn.config(text="Tạm dừng")

        self.log("=" * 64 + "\n")

        if result == "failure" or result == "cutoff":
            self.status_label.config(text="Trạng thái: Không tìm thấy lời giải")
            self.log("KHÔNG TÌM THẤY LỜI GIẢI TRONG GIỚI HẠN DEPTH.\n")

            messagebox.showinfo(
                "Kết quả",
                "Không tìm thấy lời giải trong giới hạn depth."
            )

        else:
            self.status_label.config(text="Trạng thái: Tìm thấy lời giải")
            self.log("TÌM THẤY LỜI GIẢI\n")
            self.log(f"Độ sâu lời giải: {result.path_cost}\n\n")

            path = solution_path(result)

            self.log("ĐƯỜNG ĐI CUỐI CÙNG:\n\n")

            for i, node in enumerate(path):
                self.log(f"Bước {i}\n")
                self.log(f"Action: {node.action}\n")
                self.log(f"Path cost: {node.path_cost}\n")
                self.log(state_to_string(node.state))
                self.log("\n")

            self.draw_puzzle(result.state)
            self.update_node_info(result)

            messagebox.showinfo(
                "Kết quả",
                f"Tìm thấy lời giải ở depth = {result.path_cost}"
            )


# ============================================================
# MAIN
# ============================================================

if __name__ == "__main__":
    root = tk.Tk()
    app = PuzzleApp(root)
    root.mainloop()