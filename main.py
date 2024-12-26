import pygame
import random

# 初始化pygame
pygame.init()


# 設定遊戲視窗大小和網格大小
WIDTH, HEIGHT = 400, 600
CELL_SIZE = 30
COLUMNS, ROWS = 10, HEIGHT // CELL_SIZE

# 定義遊戲中使用的顏色
COLORS = {
    'background': (0, 0, 0),     # 背景色
    'grid': (30, 30, 30),        # 網格線顏色
    'text': (200, 200, 200),     # 文字顏色
    'button_start': (0, 150, 0), # 開始按鈕顏色
    'button_restart': (150, 100, 0), # 重新開始按鈕顏色
    'border': (50, 50, 50)       # 邊框顏色
}

# 定義方塊的顏色列表
PIECE_COLORS = [
    (0, 255, 255),    # 青色
    (255, 255, 0),    # 黃色
    (255, 0, 255),    # 紫色
    (0, 255, 0),      # 綠色
    (255, 100, 100),  # 紅色
    (100, 100, 255),  # 藍色
    (255, 165, 0)     # 橙色
]

# 定義俄羅斯方塊的形狀
SHAPES = [
    [[1, 1, 1, 1]],           # I形方塊
    [[1, 1], [1, 1]],         # O形方塊
    [[0, 1, 1], [1, 1, 0]],   # S形方塊
    [[1, 1, 0], [0, 1, 1]],   # Z形方塊
    [[1, 0, 0], [1, 1, 1]],   # L形方塊
    [[0, 0, 1], [1, 1, 1]],   # J形方塊
    [[0, 1, 0], [1, 1, 1]]    # T形方塊
]

# 設定移動延遲時間(毫秒)
INITIAL_MOVE_DELAY = 200  # 初始移動延遲
MOVE_REPEAT_DELAY = 50    # 重複移動延遲

class Brick:
    """方塊類別，用於表示遊戲中的方塊"""
    def __init__(self):
        """初始化方塊"""
        self.shape = random.choice(SHAPES)  # 隨機選擇一個形狀
        self.color = random.choice(PIECE_COLORS)  # 隨機選擇一個顏色
        self.x = COLUMNS // 2 - len(self.shape[0]) // 2  # 設定初始X座標
        self.y = 0  # 設定初始Y座標

    def rotate(self):
        """旋轉方塊"""
        self.shape = [list(row) for row in zip(*self.shape[::-1])]

class Tetris:
    """俄羅斯方塊遊戲主類別"""
    def __init__(self):
        # 始化遊戲網格，大小為 COLUMNS x ROWS
        self.grid = [[0] * ROWS for _ in range(COLUMNS)]
        # 當前方塊和下一個方塊
        self.current_brick = Brick()
        self.next_brick = Brick()
        # 遊戲狀態標誌
        self.running = False      # 遊戲是否運行中
        self.game_over = False    # 遊戲是否結束
        # 分數相關
        self.score = 0
        self.high_score = self.load_high_score()
        # 按鍵控制相關時間記錄
        self.last_move_time = {'left': 0, 'right': 0}  # 上次移動時間
        self.key_press_time = {'left': 0, 'right': 0}  # 按鍵按下時間
        self.drop_shadow = True  # 是否顯示落點預覽
        self.drop_position = 0  # 落點位置

    def load_high_score(self):
        """從檔案載入最高分數"""
        try:
            with open('tetris_high_score.txt', 'r') as file:
                return int(file.read())
        except:
            return 0

    def save_high_score(self):
        """儲存最高分數到檔案"""
        try:
            with open('tetris_high_score.txt', 'w') as file:
                file.write(str(self.high_score))
        except:
            pass

    def handle_movement(self, direction, current_time):
        """處理方塊的移動
        
        Args:
            direction: 移動方向('left' 或 'right')
            current_time: 當前時間
        """
        key_state = pygame.key.get_pressed()
        dx = -1 if direction == 'left' else 1
        if (current_time - self.key_press_time[direction] >= INITIAL_MOVE_DELAY and
            current_time - self.last_move_time[direction] >= MOVE_REPEAT_DELAY):
            if self.move(dx, 0):
                self.last_move_time[direction] = current_time

    def is_valid_position(self, brick, offset_x=0, offset_y=0):
        """檢查位置是否有效
        Args:
            brick: 方塊物件
            offset_x: X軸偏移量
            offset_y: Y軸偏移量
        Returns:
            bool: 位置是否有效
        """
        if not brick:  # 添加空值檢查
            return False
        
        for y, row in enumerate(brick.shape):
            for x, cell in enumerate(row):
                if cell:  # 如果當前格子有方塊
                    grid_x = brick.x + x + offset_x  # 計算方塊在網格中的x座標
                    grid_y = brick.y + y + offset_y  # 計算方塊在網格中的y座標
                    
                    # 檢查邊界
                    if (grid_x < 0 or grid_x >= COLUMNS or 
                        grid_y >= ROWS):
                        return False
                        
                    # 檢查碰撞
                    if grid_y >= 0 and self.grid[grid_x][grid_y]:
                        return False
        return True

    def lock_brick(self):
        """將當前方塊鎖定在網格中"""
        for y, row in enumerate(self.current_brick.shape):
            for x, cell in enumerate(row):
                if cell:
                    self.grid[self.current_brick.x + x][self.current_brick.y + y] = self.current_brick.color

    def clear_lines(self):
        """清除已填滿的行並計算分數"""
        cleared_lines = 0  # 紀錄清除的行數
        for y in range(ROWS):  # 從下往上檢查每一行
            if all(self.grid[x][y] for x in range(COLUMNS)):  # 檢查該行是否已填滿
                cleared_lines += 1  # 清除行數加1
                # 將該行以上的所有行往下移一格
                for move_y in range(y, 0, -1):
                    for x in range(COLUMNS):
                        self.grid[x][move_y] = self.grid[x][move_y - 1]
                # 最上面一行清空
                for x in range(COLUMNS):
                    self.grid[x][0] = 0
        
        self.score += cleared_lines ** 2 * 10
        if self.score > self.high_score:
            self.high_score = self.score
            self.save_high_score()

    def spawn_brick(self):
        """生成新方塊
        將下一個方塊設為當前方塊，並檢查是否導致遊戲結束
        """
        self.current_brick = self.next_brick
        self.next_brick = Brick()
        # 如果新方塊無法放置，則遊戲結束
        if not self.is_valid_position(self.current_brick):
            self.game_over = True
            self.running = False

    def move(self, dx, dy):
        """移動方塊
        Args:
            dx: x方向移動距離
            dy: y方向移動距離
        Returns:
            bool: 是否成功移動
        """
        if not self.running:  # 添加運行狀態檢查
            return False
        
        if self.is_valid_position(self.current_brick, dx, dy):
            self.current_brick.x += dx
            self.current_brick.y += dy
            return True
        elif dy > 0:  # 明確檢查是否為向下移動
            self.lock_brick()
            self.clear_lines()
            self.spawn_brick()
        return False

    def rotate_brick(self):
        """旋轉當前方塊"""
        original_shape = self.current_brick.shape[:]
        self.current_brick.rotate()
        if not self.is_valid_position(self.current_brick):
            self.current_brick.shape = original_shape

    def get_drop_position(self):
        """計算當前方塊的落點位置"""
        drop_y = 0
        while self.is_valid_position(self.current_brick, 0, drop_y + 1):
            drop_y += 1
        return drop_y
    
    def drop_position(self):
        """更新落點位置"""
        self.drop_position = self.get_drop_position()

class Renderer:
    """遊戲渲染器類別"""
    def __init__(self, screen, game):
        """初始化渲染器
        
        Args:
            screen: pygame螢幕物件
            game: Tetris遊戲物件
        """
        self.screen = screen
        self.game = game
        self.start_button_rect = pygame.Rect(WIDTH + 20, HEIGHT // 2 + 50, 100, 40)
        self.restart_button_rect = pygame.Rect(WIDTH + 20, HEIGHT // 2 + 120, 100, 40)
        self.preview_pos = (WIDTH + 25, 50)
        self.score_pos = (WIDTH + 25, 200)
        self.high_score_pos = (WIDTH + 25, 280)
        self.game_over_font = pygame.font.SysFont("Arial", 48)

    def draw_grid(self):
        """繪製遊戲網格"""
        pygame.draw.rect(self.screen, COLORS['border'], 
                        pygame.Rect(0, 0, COLUMNS * CELL_SIZE, ROWS * CELL_SIZE), 2)
        
        for x in range(COLUMNS):
            for y in range(ROWS):
                color = self.game.grid[x][y] if self.game.grid[x][y] else COLORS['grid']
                pygame.draw.rect(self.screen, color, 
                    pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE))
                pygame.draw.rect(self.screen, COLORS['border'], 
                    pygame.Rect(x * CELL_SIZE, y * CELL_SIZE, CELL_SIZE, CELL_SIZE), 1)

    def draw_score_box(self, pos, label, value):
        """繪製分數框
        
        Args:
            pos: 位置座標
            label: 標籤文字
            value: 分數值
        """
        font = pygame.font.SysFont("Arial", 20)
        box_width, box_height = 120, 60
        
        box_rect = pygame.Rect(pos[0], pos[1], box_width, box_height)
        pygame.draw.rect(self.screen, COLORS['grid'], box_rect)
        pygame.draw.rect(self.screen, COLORS['border'], box_rect, 1)
        
        label_text = font.render(label, True, COLORS['text'])
        value_text = font.render(str(value), True, COLORS['text'])
        self.screen.blit(label_text, (pos[0] + 10, pos[1] + 10))
        self.screen.blit(value_text, (pos[0] + 10, pos[1] + 35))

    def draw_preview_box(self):
        """繪製下一個方塊預覽框"""
        font = pygame.font.SysFont("Arial", 20)
        next_text = font.render("Next:", True, COLORS['text'])
        self.screen.blit(next_text, (self.preview_pos[0], self.preview_pos[1] - 30))

        preview_size = 4 * CELL_SIZE
        preview_rect = pygame.Rect(self.preview_pos[0], self.preview_pos[1], 
                                 preview_size, preview_size)
        pygame.draw.rect(self.screen, COLORS['grid'], preview_rect)
        pygame.draw.rect(self.screen, COLORS['border'], preview_rect, 1)

        brick = self.game.next_brick
        brick_width = len(brick.shape[0]) * CELL_SIZE
        brick_height = len(brick.shape) * CELL_SIZE
        
        start_x = self.preview_pos[0] + (preview_size - brick_width) // 2
        start_y = self.preview_pos[1] + (preview_size - brick_height) // 2

        for y, row in enumerate(brick.shape):
            for x, cell in enumerate(row):
                if cell:
                    pygame.draw.rect(self.screen, brick.color,
                        pygame.Rect(start_x + x * CELL_SIZE, start_y + y * CELL_SIZE, 
                                  CELL_SIZE, CELL_SIZE))
                    pygame.draw.rect(self.screen, COLORS['border'],
                        pygame.Rect(start_x + x * CELL_SIZE, start_y + y * CELL_SIZE, 
                                  CELL_SIZE, CELL_SIZE), 1)

    def draw_buttons(self):
        """繪製遊戲按鈕"""
        font = pygame.font.SysFont("Arial", 20)
        
        pygame.draw.rect(self.screen, COLORS['button_start'], self.start_button_rect)
        start_text = font.render("START", True, COLORS['text'])
        self.screen.blit(start_text, (self.start_button_rect.x + 20, 
                                     self.start_button_rect.y + 10))

        pygame.draw.rect(self.screen, COLORS['button_restart'], self.restart_button_rect)
        restart_text = font.render("RESTART", True, COLORS['text'])
        self.screen.blit(restart_text, (self.restart_button_rect.x + 5, 
                                      self.restart_button_rect.y + 10))

    def draw_game_over(self):
        """繪製遊戲結束畫面"""
        # 創建半透明黑色背景
        s = pygame.Surface((WIDTH, HEIGHT))
        s.set_alpha(128)  # 設置透明度（0-255）
        s.fill(COLORS['background'])
        self.screen.blit(s, (0, 0))
        
        # 繪製 GAME OVER 文字
        text = self.game_over_font.render("GAME OVER", True, COLORS['text'])
        text_rect = text.get_rect(center=(WIDTH // 2, HEIGHT // 2))
        self.screen.blit(text, text_rect)
        
        # 顯示最終分數
        score_font = pygame.font.SysFont("Arial", 24)
        score_text = score_font.render(f"最終分數: {self.game.score}", True, COLORS['text'])
        score_rect = score_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 50))
        self.screen.blit(score_text, score_rect)
        
        # 顯示重新開始提示
        hint_font = pygame.font.SysFont("Arial", 20)
        hint_text = hint_font.render("按 RESTART 重新開始", True, COLORS['text'])
        hint_rect = hint_text.get_rect(center=(WIDTH // 2, HEIGHT // 2 + 100))
        self.screen.blit(hint_text, hint_rect)

    def draw_controls(self):
        """繪製控制說明"""
        font = pygame.font.SysFont("Arial", 16)
        controls = [
            "          ",
            "← → : Move",
            "↑ : Rotate",
            "↓ : Soft drop"
        ]
        y = HEIGHT - 150
        for text in controls:
            surface = font.render(text, True, COLORS['text'])
            self.screen.blit(surface, (WIDTH + 20, y))
            y += 20

    def render(self):
        """渲染遊戲畫面"""
        self.screen.fill(COLORS['background'])
        self.draw_grid()
        
        if self.game.running:
            # 繪製落點預覽
            if self.game.drop_shadow:
                drop_y = self.game.get_drop_position()
                for y, row in enumerate(self.game.current_brick.shape):
                    for x, cell in enumerate(row):
                        if cell:
                            shadow_color = tuple(c // 4 for c in self.game.current_brick.color)
                            pygame.draw.rect(self.screen, shadow_color,
                                pygame.Rect(
                                    (self.game.current_brick.x + x) * CELL_SIZE,
                                    (self.game.current_brick.y + y + drop_y) * CELL_SIZE,
                                    CELL_SIZE, CELL_SIZE))
            
            for y, row in enumerate(self.game.current_brick.shape):
                for x, cell in enumerate(row):
                    if cell:
                        pygame.draw.rect(self.screen, self.game.current_brick.color,
                            pygame.Rect((self.game.current_brick.x + x) * CELL_SIZE,
                                      (self.game.current_brick.y + y) * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE))
                        pygame.draw.rect(self.screen, COLORS['border'],
                            pygame.Rect((self.game.current_brick.x + x) * CELL_SIZE,
                                      (self.game.current_brick.y + y) * CELL_SIZE,
                                      CELL_SIZE, CELL_SIZE), 1)
            
            self.draw_preview_box()

        self.draw_buttons()
        self.draw_score_box(self.score_pos, "Score:", self.game.score)
        self.draw_score_box(self.high_score_pos, "High Score:", self.game.high_score)
        if self.game.game_over:
            self.draw_game_over()
        self.draw_controls()
        pygame.display.flip()

def main():
    """遊戲主函數"""
    # 初始化遊戲視窗和時鐘
    screen = pygame.display.set_mode((WIDTH + 150, HEIGHT))
    pygame.display.set_caption("Tetris")
    clock = pygame.time.Clock()
    game = Tetris()
    renderer = Renderer(screen, game)

    # 設定方塊下落速度
    normal_drop_time = 500  # 正常下落速度
    fast_drop_time = 50     # 快速下落速度
    drop_time = normal_drop_time
    last_drop = pygame.time.get_ticks()

    # 主遊戲迴圈
    while True:
        current_time = pygame.time.get_ticks()
        
        # 處理事件
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                game.save_high_score()
                pygame.quit()
                return
            elif event.type == pygame.KEYDOWN and game.running:
                if event.key == pygame.K_LEFT:
                    game.key_press_time['left'] = current_time
                    game.move(-1, 0)
                elif event.key == pygame.K_RIGHT:
                    game.key_press_time['right'] = current_time
                    game.move(1, 0)
                elif event.key == pygame.K_UP:
                    game.rotate_brick()
            elif event.type == pygame.KEYUP:
                if event.key == pygame.K_LEFT:
                    game.key_press_time['left'] = 0
                elif event.key == pygame.K_RIGHT:
                    game.key_press_time['right'] = 0
            elif event.type == pygame.MOUSEBUTTONDOWN:
                mouse_pos = event.pos
                if renderer.start_button_rect.collidepoint(mouse_pos) and not game.running:
                    game = Tetris()
                    renderer = Renderer(screen, game)
                    game.running = True
                elif renderer.restart_button_rect.collidepoint(mouse_pos):
                    game = Tetris()
                    renderer = Renderer(screen, game)
                    game.running = True

        # 遊戲運行時的邏輯處理
        if game.running:
            keys = pygame.key.get_pressed()
            
            # 處理左右移動
            if keys[pygame.K_LEFT] and game.key_press_time['left']:
                game.handle_movement('left', current_time)
            if keys[pygame.K_RIGHT] and game.key_press_time['right']:
                game.handle_movement('right', current_time)
            
            # 處理方塊下落
            drop_time = fast_drop_time if keys[pygame.K_DOWN] else normal_drop_time
            if current_time - last_drop > drop_time:
                game.move(0, 1)
                last_drop = current_time

        # 更新畫面
        renderer.render()
        clock.tick(60)

if __name__ == "__main__":
    main()
