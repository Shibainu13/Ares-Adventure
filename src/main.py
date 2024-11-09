import sys
from PyQt5.QtWidgets import QApplication, QWidget, QComboBox, QPushButton, QLabel, QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
from PyQt5.QtGui import QIcon, QPixmap, QPainter, QColor, QMovie, QFont
from PyQt5.QtCore import Qt, QTimer, QThread, pyqtSignal, QSize
import search_algorithms._utils as _utils
import search_algorithms.bfs as BFS
import search_algorithms.dfs as DFS
import search_algorithms.ucs as UCS
import search_algorithms.a_star as ASTAR
from collections import deque

def isInterger(s):
    try:
        int(s)
        return True
    except ValueError:
        return False

class AlgorithmThread(QThread):
    finished = pyqtSignal(object)

    def __init__(self, algorithm, grid, ares_pos, stones, switches, stone_weights):
        super().__init__()
        self.algorithm = algorithm
        self.grid = grid
        self.ares_pos = ares_pos
        self.stones = stones
        self.switches = switches
        self.stone_weights = stone_weights

    def run(self):
        # Sleep for 1ms to allow the UI to update
        QThread.sleep(1)
        result = self.run_algorithm(self.algorithm)
        self.finished.emit((result, self.algorithm))

    def run_algorithm(self, algorithm):
        if algorithm == 'BFS':
            return BFS.bfs(self.grid, self.ares_pos, self.stones, self.switches, self.stone_weights)
        elif algorithm == 'DFS':
            return DFS.dfs(self.grid, self.ares_pos, self.stones, self.switches, self.stone_weights)
        elif algorithm == 'UCS':
            return UCS.ucs(self.grid, self.ares_pos, self.stones, self.switches, self.stone_weights)
        elif algorithm == 'A*':
            return ASTAR.a_star(self.grid, self.ares_pos, self.stones, self.stone_weights, self.switches)
        return None

class SokobanVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize UI Components
        self.maps = [f'../maps/input{i}.txt' for i in range(1, 11)]
        self.is_running = False
        self.initUI()
    
    def initUI(self):
        # Set Window Title
        self.setWindowTitle("Ares' Adventure")
        self.setWindowIcon(QIcon('../asset/ares.png'))
        
        # Main Layout
        main_layout = QVBoxLayout()
        
        # Top Controls Layout
        top_layout = QHBoxLayout()
        
        # Map Dropdown
        self.map_dropdown = QComboBox()
        self.map_dropdown.addItems([f'Map {i}' for i in range(1, 11)])
        self.map_dropdown.currentIndexChanged.connect(self.load_map)
        top_layout.addWidget(QLabel('Select Map:'))
        top_layout.addWidget(self.map_dropdown)
        
        # Algorithm Dropdown
        self.algorithm_dropdown = QComboBox()
        self.algorithm_dropdown.addItems(['BFS', 'DFS', 'UCS', 'A*'])
        top_layout.addWidget(QLabel('Select Algorithm:'))
        top_layout.addWidget(self.algorithm_dropdown)
        
        # Info Display (Steps & Cost)
        self.steps_label = QLabel('Steps: 0')
        self.cost_label = QLabel('Total Cost: 0')

        # Loading Animation
        self.loading_label = QLabel()
        self.loading_movie = QMovie('../asset/loading.gif')
        self.loading_label.setMovie(self.loading_movie)
        self.loading_movie.setScaledSize(QSize(20, 20))

        # Add components to top layout
        top_layout.addWidget(self.steps_label)
        top_layout.addWidget(self.cost_label)
        top_layout.addWidget(self.loading_label)
        self.loading_label.hide()
        self.steps_label.setFixedWidth(80)  # Increase width for steps label
        self.cost_label.setFixedWidth(100)  # Increase width for cost label
        
        # Add top layout to main layout
        main_layout.addLayout(top_layout)
        
        # Grid Layout for Map
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(0)
        self.map_container = QWidget()
        self.map_container.setLayout(self.grid_layout)
        main_layout.addWidget(self.map_container, alignment=Qt.AlignCenter)
        
        # Bottom Controls Layout
        bottom_layout = QHBoxLayout()
        
        # Start Button
        self.start_button = QPushButton('Start')
        self.start_button.clicked.connect(self.start_visualization)
        bottom_layout.addWidget(self.start_button)
            
        # Reset Button
        self.reset_button = QPushButton('Reset')
        self.reset_button.clicked.connect(self.reset_map)
        bottom_layout.addWidget(self.reset_button)
        
        # Add bottom layout to main layout
        main_layout.addLayout(bottom_layout)
        
        # Set Main Layout
        self.setLayout(main_layout)
        
        # Timer for visualization
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        
        # Load Initial Map
        self.load_map()
    
    def load_assets(self):
        self.assets = {}
        font = QFont('../asset/JetBrainsMono-Regular.ttf', 16)

        # Load player assets on blank background
        player_assets = QPixmap(40, 40)
        player_assets.fill(Qt.transparent)
        painter = QPainter(player_assets)
        painter.drawPixmap(0, 0, QPixmap('../asset/real_blank.png').scaled(40, 40, Qt.KeepAspectRatio))
        painter.drawPixmap(0, 0, QPixmap('../asset/ares.png').scaled(40, 40, Qt.KeepAspectRatio))
        painter.end()
        self.assets['@'] = player_assets
        self.assets['+'] = player_assets

        # Load other assets
        self.assets['o'] = QPixmap('../asset/blank.png').scaled(40, 40, Qt.KeepAspectRatio)
        self.assets['#'] = QPixmap('../asset/brick.png').scaled(40, 40, Qt.KeepAspectRatio)
        self.assets[' '] = QPixmap('../asset/real_blank.png').scaled(40, 40, Qt.KeepAspectRatio)
        self.assets['.'] = QPixmap('../asset/switch.png').scaled(40, 40, Qt.KeepAspectRatio)

        # Load stone assets
        original_stone = QPixmap('../asset/stone.png').scaled(40, 40, Qt.KeepAspectRatio)
        stone_assets = QPixmap(40, 40)
        stone_assets.fill(Qt.transparent)
        painter = QPainter(stone_assets)
        painter.drawPixmap(0, 0, QPixmap('../asset/real_blank.png').scaled(40, 40, Qt.KeepAspectRatio))
        painter.drawPixmap(0, 0, original_stone)
        painter.end()
        # self.assets['$'] = stone_assets

        for weight in self.stone_weights:
            weight_str = str(weight)
            pixmap = QPixmap(40, 40)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.drawPixmap(0, 0, stone_assets)
            painter.setFont(font)
            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.setPen(QColor(255, 255, 255))
            text_rect = painter.boundingRect(pixmap.rect(), Qt.AlignRight, weight_str)
            painter.drawText((40 - text_rect.width()) // 2, (40 + text_rect.height()) // 2, weight_str)
            painter.end()
            self.assets[weight_str] = pixmap

        # Load stone on switch assets
        stone_on_switch = QPixmap(40, 40)
        stone_on_switch.fill(Qt.transparent)
        painter = QPainter(original_stone)
        tint_color = QColor(255, 255, 0) # Yellow tint
        tint_color.setAlpha(100)
        painter.setCompositionMode(QPainter.CompositionMode_SourceAtop)
        painter.fillRect(original_stone.rect(), tint_color)
        painter.setCompositionMode(QPainter.CompositionMode_SourceOver)
        painter.end()
        painter = QPainter(stone_on_switch)
        painter.drawPixmap(0, 0, QPixmap('../asset/real_blank.png').scaled(40, 40, Qt.KeepAspectRatio))
        painter.drawPixmap(0, 0, original_stone)
        painter.end()
        # self.assets['*'] = stone_on_switch

        for weight in self.stone_weights:
            weight_str = str(weight)
            real_str = str(-weight)
            pixmap = QPixmap(40, 40)
            pixmap.fill(Qt.transparent)
            painter = QPainter(pixmap)
            painter.drawPixmap(0, 0, stone_on_switch)
            painter.setFont(font)
            painter.setRenderHint(QPainter.TextAntialiasing)
            painter.setPen(QColor(255, 255, 255))
            text_rect = painter.boundingRect(pixmap.rect(), Qt.AlignRight, weight_str)
            painter.drawText((40 - text_rect.width()) // 2, (40 + text_rect.height()) // 2, weight_str)
            painter.end()
            self.assets[real_str] = pixmap

    def load_map(self):
        # Stop any ongoing visualization if running
        if self.timer.isActive():
            self.timer.stop()
            self.reset_map()
            
        # Reset status texts
        self.steps_label.setText('Steps: 0')
        self.cost_label.setText('Total Cost: 0')
        
        # Get the selected map file
        map_file = self.maps[self.map_dropdown.currentIndex()]
        
        # Read and parse the map file
        with open(map_file, 'r') as f:
            input_data = f.read()
        self.stone_weights, self.grid = _utils.parse_input(input_data)
        self.ares_pos, self.stones, self.switches = _utils.find_positions(self.grid, self.stone_weights)

        # Load assets
        self.load_assets()
        
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        
        # Setup map dimensions, fill empty cells with ' ' and mark inside/outside walls
        map_height = len(self.grid)
        map_width = max(len(row) for row in self.grid)
        self.grid = [row + [' '] * (map_width - len(row)) for row in self.grid]
        self.mark_inside_outside_walls(map_height, map_width)
        
        # Load textures based on cell type
        for row in range(map_height):
            for col in range(map_width):
                cell = QLabel()
                cell.setFixedSize(40, 40)
                
                cell_type = self.grid[row][col]
                cell.setPixmap(self.assets[cell_type])
                
                # Add cell to grid layout
                self.grid_layout.addWidget(cell, row, col)
        
        # Adjust window size based on map size
        self.setFixedSize(max(map_width * 40 + 100, 600), map_height * 40 + 150)
    
    def mark_inside_outside_walls(self, map_height, map_width):
        visited = [[False for _ in range(map_width)] for _ in range(map_height)]

        # Find pairs coordinates of border cells
        def border_pairs():
            result = []
            for c in range(map_width):
                result.append((0, c))
                result.append((map_height - 1, c))
            for r in range(1, map_height - 1):
                result.append((r, 0))
                result.append((r, map_width - 1))
            return result
        
        # BFS to mark inside/outside walls
        def bfs(start_x, start_y):
            queue = deque([(start_x, start_y)])
            visited[start_x][start_y] = True

            while queue:
                x, y = queue.popleft()
                self.grid[x][y] = 'o'
                for dx, dy in [(0, 1), (0, -1), (1, 0), (-1, 0)]:
                    nx, ny = x + dx, y + dy
                    if 0 <= nx < map_height and 0 <= ny < map_width and not visited[nx][ny] and self.grid[nx][ny] == ' ':
                        visited[nx][ny] = True
                        queue.append((nx, ny))

        # Mark outside walls
        for r, c in border_pairs():
            if not visited[r][c] and self.grid[r][c] == ' ':
                bfs(r, c)

    def start_visualization(self):
        # Act as a pause button if is_running
        if self.is_running and self.timer.isActive():
            self.timer.stop()
            self.start_button.setText('Continue')
            return
        elif self.is_running and not self.timer.isActive():
            self.timer.start(150)
            self.start_button.setText('Pause')
            return
          
        self.loading_label.show()
        self.loading_movie.start()
        
        # Show loading animation
        self.loading_label.show()
        self.loading_movie.start()
        
        # Show loading animation
        self.loading_label.show()
        self.loading_movie.start()
        
        self.reset_map()
        algorithm = self.algorithm_dropdown.currentText()

        # Run the selected algorithm in a separate thread
        self.thread = AlgorithmThread(algorithm, self.grid, self.ares_pos, self.stones, self.switches, self.stone_weights)
        self.thread.finished.connect(self.on_algorithm_finished)
        self.thread.start()

    def on_algorithm_finished(self, result):
        # Hide loading animation
        self.loading_label.hide()
        self.loading_movie.stop()

        result, algorithm = result

        if result is None:
            QMessageBox.information(self, 'Error', 'No solution found.')
            return
        
        save_file = f'../output/output-{self.map_dropdown.currentIndex() + 1:02}.txt'
        with open(save_file, 'a+') as file:
            self.save_result_to_file(file, result, algorithm)
            file.close()

        self.steps = 0
        self.total_weight = result['weight_track']
        self.path = result['path']
        
        self.steps_label.setText(f"Steps: {self.steps}")
        self.cost_label.setText(f"Total Cost: 0")
        
        self.path_index = 0
        self.timer.start(min(150, 5000 // result['steps']))
        self.start_button.setText('Pause')
        self.is_running = True
        
    def next_step(self):
        if self.path_index >= len(self.path):
            self.timer.stop()  # Stop the timer when path is complete
            self.start_button.setText('Start')
            self.is_running = False
            return

        move = self.path[self.path_index]
        self.execute_move(move)
        self.path_index += 1
        self.steps += 1
        
        # Update the stats after each step
        self.steps_label.setText(f'Steps: {self.steps}')
        self.cost_label.setText(f'Total Cost: {self.total_weight[self.steps - 1]}')
        
    def execute_move(self, move):
        # Define movement deltas
        deltas = {
            'u': (-1, 0), 'U': (-1, 0),  # Up
            'd': (1, 0), 'D': (1, 0),    # Down
            'l': (0, -1), 'L': (0, -1),  # Left
            'r': (0, 1), 'R': (0, 1)     # Right
        }
        
        # Get the current position of the player (Ares)
        current_row, current_col = self.ares_pos
        delta_row, delta_col = deltas[move]
        
        # Calculate new player position
        new_row = current_row + delta_row
        new_col = current_col + delta_col
        
        # Check if it's a stone-pushing move (uppercase letter)
        if move.isupper():
            # Calculate stone's new position
            stone_row = new_row + delta_row
            stone_col = new_col + delta_col
            
            # Move the stone to the new position
            self.grid[stone_row][stone_col] = self.grid[new_row][new_col] if self.grid[stone_row][stone_col] == ' ' else str(-int(self.grid[new_row][new_col]))
            self.grid[new_row][new_col] = '+' if self.grid[new_row][new_col] == '.' else '@'
            
            # Update UI for the stone's new position
            self.update_cell(stone_row, stone_col, stone=True)
        
        # Move the player to the new position
        self.grid[new_row][new_col] = '@' if self.grid[new_row][new_col] == '.' else '+'
        self.grid[current_row][current_col] = '.' if (current_row, current_col) in self.switches else ' '

        # Update UI for player's new position
        self.update_cell(new_row, new_col, player=True)
        self.update_cell(current_row, current_col)

        # Update player's position for the next move
        self.ares_pos = (new_row, new_col)

    def update_cell(self, row, col, player=False, stone=False):
        """Updates the cell at (row, col) with the appropriate color and style."""
        cell = self.grid_layout.itemAtPosition(row, col).widget()
        
        # Determine the cell's style based on its contents
        cell_type = self.grid[row][col]
        if cell_type == '#' or cell_type == '.' or cell_type == 'o' or cell_type == ' ':  # Wall, Switch, Blank, Inside Wall
            cell.setPixmap(self.assets[cell_type])
        elif player:
            cell.setPixmap(self.assets['@']) # Player
        elif stone:
            cell.setPixmap(self.assets[cell_type])
 
    def reset_map(self):
        # Stop any ongoing visualization if running
        if self.timer.isActive():
            self.timer.stop()

        # Reset the visualization (clear the steps, cost, and reset map)
        self.is_running = False
        self.start_button.setText('Start')
        self.steps_label.setText('Steps: 0')
        self.cost_label.setText('Total Cost: 0')
        self.path_index = 0
        self.steps = 0
        self.total_weight = 0
        self.load_map()

    def save_result_to_file(self, file, result, algorithm):
        # Check if the algorithm result is already saved in the file
        file.seek(0)
        if any(algorithm in line for line in file):
            return

        # Save the algorithm result to the file
        output = (
            f"{algorithm}\n"
            f"Steps: {result['steps']}, "
            f"Weight: {result['weight']}, "
            f"Node: {result['nodes']}, "
            f"Time (ms): {result['time_ms']}, "
            f"Memory (MB): {result['memory_mb']}\n"
            f"{result['path']}\n"
        )
        file.write(output)

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    sokoban_visualizer = SokobanVisualizer()
    sokoban_visualizer.show()
    sys.exit(app.exec_())
