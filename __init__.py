# Generation ID: Hutch_1763741128742_i3hnwdrxi (前半)

def myai(board, color):
    """
    オセロの最適な着手位置を返す
    board: 2次元配列(6x6 or 8x8)
    color: 置く色(1=BLACK, 2=WHITE)
    return: (column, row)
    """
    size = len(board)
    opponent_color = 3 - color

    # 利用可能な手を取得
    valid_moves = get_valid_moves(board, color)

    if not valid_moves:
        return None

    # 終盤判定（空きマスが少ない）
    empty_count = sum(1 for row in board for cell in row if cell == 0)
    is_endgame = empty_count <= size * 2

    if is_endgame:
        # ミニマックス法による深い探索
        best_move = minimax_search(board, color, depth=6)
        return best_move

    # 角の確保（最優先）
    corners = get_corners(size)
    for move in valid_moves:
        if move in corners:
            return move

    # 危険なマスを除外
    safe_moves = [m for m in valid_moves if not is_dangerous(m, size)]

    # 確定石を増やす手を評価
    best_move = None
    best_score = -float('inf')

    for move in safe_moves:
        score = evaluate_move(board, color, move, size)
        if score > best_score:
            best_score = score
            best_move = move

    return best_move if best_move else valid_moves[0]


def get_valid_moves(board, color):
    """合法手をすべて取得"""
    size = len(board)
    valid_moves = []
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]

    for row in range(size):
        for col in range(size):
            if board[row][col] == 0:
                if can_place(board, row, col, color, directions, size):
                    valid_moves.append((col, row))

    return valid_moves


def can_place(board, row, col, color, directions, size):
    """指定位置に石が置けるか判定"""
    opponent = 3 - color

    for dr, dc in directions:
        nr, nc = row + dr, col + dc
        found_opponent = False

        while 0 <= nr < size and 0 <= nc < size:
            if board[nr][nc] == opponent:
                found_opponent = True
            elif board[nr][nc] == color:
                if found_opponent:
                    return True
                break
            else:
                break
            nr += dr
            nc += dc

    return False


def get_corners(size):
    """角の座標を取得"""
    return [(0, 0), (size-1, 0), (0, size-1), (size-1, size-1)]


def is_dangerous(move, size):
    """危険なマスか判定"""
    col, row = move
    corners = get_corners(size)

    # 隅のとなり
    for cc, cr in corners:
        if abs(col - cc) <= 1 and abs(row - cr) <= 1:
            if (col, row) != (cc, cr):
                return True

    return False


def evaluate_move(board, color, move, size):
    """手を評価"""
    board_copy = [row[:] for row in board]
    place_stone(board_copy, move[0], move[1], color, size)

    score = 0

    # 確定石の数を重視
    score += count_stable_stones(board_copy, color) * 10

    # 相手の合法手を減らすことを重視
    opponent_moves = len(get_valid_moves(board_copy, 3 - color))
    score -= opponent_moves * 3

    # 反転する石の数
    score += count_flipped_stones(board, move[0], move[1], color, size)

    return score


def place_stone(board, col, row, color, size):
    """石を置いて反転"""
    board[row][col] = color
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    opponent = 3 - color

    for dr, dc in directions:
        flipped = []
        nr, nc = row + dr, col + dc

        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == opponent:
            flipped.append((nr, nc))
            nr += dr
            nc += dc

        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == color:
            for fr, fc in flipped:
                board[fr][fc] = color


def count_flipped_stones(board, col, row, color, size):
    """反転する石の数をカウント"""
    count = 0
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    opponent = 3 - color

    for dr, dc in directions:
        flipped = 0
        nr, nc = row + dr, col + dc

        while 0 <= nr < size and 0 <= nc < size and board[nr][nc] == opponent:
            flipped += 1
            nr += dr
            nc += dc

        if 0 <= nr < size and 0 <= nc < size and board[nr][nc] == color:
            count += flipped

    return count


def count_stable_stones(board, color):
    """確定石の数をカウント"""
    size = len(board)
    count = 0

    for row in range(size):
        for col in range(size):
            if board[row][col] == color:
                if is_stable(board, row, col, color, size):
                    count += 1

    return count


def is_stable(board, row, col, color, size):
    """石が確定石か判定"""
    directions = [(-1,-1), (-1,0), (-1,1), (0,-1), (0,1), (1,-1), (1,0), (1,1)]
    opponent = 3 - color

    for dr, dc in directions:
        nr, nc = row + dr, col + dc

        while 0 <= nr < size and 0 <= nc < size:
            if board[nr][nc] == 0:
                return False
            elif board[nr][nc] == opponent:
                return False
            nr += dr
            nc += dc

    return True


def minimax_search(board, color, depth):
    """ミニマックス法による最適手の探索"""
    valid_moves = get_valid_moves(board, color)

    if not valid_moves:
        return None

    best_move = valid_moves[0]
    best_value = -float('inf')

    for move in valid_moves:
        board_copy = [row[:] for row in board]
        place_stone(board_copy, move[0], move[1], color, len(board))
        value = minimax(board_copy, color, depth - 1, False, 3 - color, len(board))

        if value > best_value:
            best_value = value
            best_move = move

    return best_move


def minimax(board, original_color, depth, is_maximizing, current_color, size):
    """ミニマックスアルゴリズム"""
    if depth == 0:
        return evaluate_board(board, original_color, size)

    valid_moves = get_valid_moves(board, current_color)

    if not valid_moves:
        return minimax(board, original_color, depth - 1, not is_maximizing, 3 - current_color, size)

    if is_maximizing:
        max_value = -float('inf')
        for move in valid_moves:
            board_copy = [row[:] for row in board]
            place_stone(board_copy, move[0], move[1], current_color, size)
            value = minimax(board_copy, original_color, depth - 1, False, 3 - current_color, size)
            max_value = max(max_value, value)
        return max_value
    else:
        min_value = float('inf')
        for move in valid_moves:
            board_copy = [row[:] for row in board]
            place_stone(board_copy, move[0], move[1], current_color, size)
            value = minimax(board_copy, original_color, depth - 1, True, 3 - current_color, size)
            min_value = min(min_value, value)
        return min_value


def evaluate_board(board, color, size):
    """盤面を評価"""
    player_count = sum(1 for row in board for cell in row if cell == color)
    opponent_count = sum(1 for row in board for cell in row if cell == (3 - color))

    return player_count - opponent_count

# Generation ID: Hutch_1763741128742_i3hnwdrxi (後半)
