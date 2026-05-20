from collections import deque
import random

# GOAL STATE
GOAL_STATE = [
    [1, 2, 3],
    [4, 5, 6],
    [7, 8, 0]
]

# 0 là ô trống
MOVES = {
    "UP": (-1, 0),
    "DOWN": (1, 0),
    "LEFT": (0, -1),
    "RIGHT": (0, 1)
}


# NODE 
class Node:
    def __init__(self, state, parent=None, action=None, path_cost=0):
        self.state = state
        self.parent = parent
        self.action = action
        self.path_cost = path_cost


# CÁC HÀM XỬ LÝ 8-PUZZLE
def print_state(state):
    for row in state:
        print(row)
    print()


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


def is_cycle(node):
    """
    Kiểm tra trạng thái hiện tại có bị lặp với node cha, ông, cụ... hay không
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
    Sinh các node con từ node hiện tại
    """
    children = []

    zero_i, zero_j = find_zero(node.state)

    for action, (di, dj) in MOVES.items():
        new_i = zero_i + di
        new_j = zero_j + dj

        if 0 <= new_i < 3 and 0 <= new_j < 3:
            new_state = copy_state(node.state)

            new_state[zero_i][zero_j], new_state[new_i][new_j] = \
                new_state[new_i][new_j], new_state[zero_i][zero_j]

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
    Truy ngược từ node đích về node gốc
    """
    path = []

    while node is not None:
        path.append(node)
        node = node.parent

    path.reverse()
    return path


# DEPTH-LIMITED SEARCH
def depth_limited_search(start_state, limit):
    root = Node(
        state=start_state,
        parent=None,
        action=None,
        path_cost=0
    )

    frontier = deque()
    frontier.append(root)

    result = "failure"

    while frontier:
        node = frontier.pop()

        if is_goal(node.state):
            return node

        if node.path_cost > limit:
            result = "cutoff"

        elif not is_cycle(node):
            for child in expand(node):
                frontier.append(child)

    return result


# ITERATIVE DEEPENING SEARCH
def iterative_deepening_search(start_state, max_depth=30):
    for depth in range(max_depth + 1):
        print("Đang tìm với giới hạn độ sâu =", depth)

        result = depth_limited_search(start_state, depth)

        if result != "cutoff" and result != "failure":
            return result

    return "failure"



# RANDOM STATE HỢP LỆ
def random_state_by_moves(steps=20):
    current = copy_state(GOAL_STATE)

    for _ in range(steps):
        node = Node(current)
        children = expand(node)
        current = random.choice(children).state

    return current

def random_start_state(steps=10):
    """
    Tạo trạng thái random bằng cách xuất phát từ goal
    rồi di chuyển ngẫu nhiên 'steps' lần.
    steps càng lớn thì trạng thái càng bị xáo trộn nhiều.
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
        node = Node(current_state)
        children = expand(node)

        # Tránh vừa đi xong lại đi ngược lại ngay
        if last_action is not None:
            children = [
                child for child in children
                if child.action != opposite[last_action]
            ]

        chosen_child = random.choice(children)
        current_state = chosen_child.state
        last_action = chosen_child.action

    return current_state
# =========================
# MAIN
# =========================

if __name__ == "__main__":

    start_state = random_start_state(steps=8)

    # Nếu muốn random thì dùng dòng này:
    # start_state = random_state_by_moves(steps=15)

    print("TRẠNG THÁI BAN ĐẦU:")
    print_state(start_state)

    print("TRẠNG THÁI ĐÍCH:")
    print_state(GOAL_STATE)

    result = iterative_deepening_search(start_state, max_depth=20)

    if result == "failure":
        print("Không tìm thấy lời giải.")

    else:
        path = solution_path(result)

        print("TÌM THẤY LỜI GIẢI")
        print("Tổng số bước:", result.path_cost)
        print()

        for i, node in enumerate(path):
            print("Bước", i)

            if node.action is not None:
                print("Hành động:", node.action)

            print("Path cost:", node.path_cost)
            print_state(node.state)