
import sys
import time
from PyQt5.QtWidgets import (
    QApplication, QWidget, QComboBox, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
)
from PyQt5.QtGui import (QIcon, QPixmap, QPainter, QColor)
from PyQt5.QtCore import Qt, QTimer
import search_algorithms._utils as _utils
import search_algorithms.bfs as BFS
import search_algorithms.dfs as DFS
import search_algorithms.ucs as UCS
import search_algorithms.a_star as ASTAR

class SokobanVisualizer(QWidget):
    def __init__(self):
        super().__init__()
        
        # Initialize UI Components
        self.maps = [f'../maps/input{i}.txt' for i in range(1, 11)]
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
        top_layout.addWidget(self.steps_label)
        top_layout.addWidget(self.cost_label)
        self.steps_label.setFixedWidth(80)  # Increase width for steps label
        self.cost_label.setFixedWidth(100)  # Increase width for cost label
        
        # Add top layout to main layout
        main_layout.addLayout(top_layout)
        
        # Grid Layout for Map
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)
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

        # Load assets
        self.load_assets()
        
        # Set Main Layout
        self.setLayout(main_layout)
        
        # Timer for visualization
        self.timer = QTimer()
        self.timer.timeout.connect(self.next_step)
        
        # Load Initial Map
        self.load_map()
    
    def load_assets(self):
        self.assets = {}

        player_assets = QPixmap(40, 40)
        player_assets.fill(Qt.transparent)
        painter = QPainter(player_assets)
        painter.drawPixmap(0, 0, QPixmap('../asset/real_blank.png').scaled(40, 40, Qt.KeepAspectRatio))
        painter.drawPixmap(0, 0, QPixmap('../asset/ares.png').scaled(40, 40, Qt.KeepAspectRatio))
        painter.end()
        self.assets['player'] = player_assets

        self.assets['invalid_cell'] = QPixmap('../asset/blank.png').scaled(40, 40, Qt.KeepAspectRatio)
        self.assets['wall'] = QPixmap('../asset/brick.png').scaled(40, 40, Qt.KeepAspectRatio)
        self.assets['blank'] = QPixmap('../asset/real_blank.png').scaled(40, 40, Qt.KeepAspectRatio)
        self.assets['switch'] = QPixmap('../asset/switch.png').scaled(40, 40, Qt.KeepAspectRatio)

        original_stone = QPixmap('../asset/stone.png').scaled(40, 40, Qt.KeepAspectRatio)
        self.assets['stone'] = original_stone

        stone_on_switch = QPixmap(40, 40)
        stone_on_switch.fill(Qt.transparent)
        painter = QPainter(stone_on_switch)
        painter.drawPixmap(0, 0, original_stone)
        tint_color = QColor(255, 255, 0)
        tint_color.setAlpha(100)
        painter.fillRect(stone_on_switch.rect(), tint_color)
        painter.end()
        self.assets['stone_on_switch'] = stone_on_switch

    def load_map(self):
        # Stop any ongoing visualization if running
        if self.timer.isActive():
            self.timer.stop()
            
        # Reset status texts
        self.steps_label.setText('Steps: 0')
        self.cost_label.setText('Total Cost: 0')
        
        # Get the selected map file
        map_file = self.maps[self.map_dropdown.currentIndex()]
        
        # Read and parse the map file
        with open(map_file, 'r') as f:
            input_data = f.read()
        self.stone_weights, self.grid = _utils.parse_input(input_data)
        self.ares_pos, self.stones, self.switches = _utils.find_positions(self.grid)
        
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        
        # Setup map dimensions
        map_height = len(self.grid)
        map_width = max(len(row) for row in self.grid)
        
        # Load textures based on cell type
        for row in range(map_height):
            for col in range(map_width):
                cell = QLabel()
                cell.setFixedSize(40, 40)
                
                if col < len(self.grid[row]):  # Check to avoid index error for uneven rows
                    cell_type = self.grid[row][col]
                    if cell_type == '#':
                        cell.setPixmap(self.assets['wall'])  # Wall
                    elif cell_type == '.':
                        cell.setPixmap(self.assets['switch']) # Switch
                    elif cell_type == '@':
                        cell.setPixmap(self.assets['player']) # Player
                    elif cell_type == '+':
                        cell.setPixmap(self.assets['player']) # Player on switch
                    elif cell_type == '$':
                        cell.setPixmap(self.assets['stone']) # Stone
                    elif cell_type == '*':
                        cell.setPixmap(self.assets['stone_on_switch']) # Stone on switch
                    else:
                        cell.setPixmap(self.assets['blank']) # Empty cell
                else:
                    cell.setPixmap(self.assets['invalid_cell'])
                
                # Add cell to grid layout
                self.grid_layout.addWidget(cell, row, col)
        
        # Adjust window size based on map size
        self.setFixedSize(max(map_width * 40 + 100, 600), map_height * 40 + 150)
    
    def start_visualization(self):        
        algorithm = self.algorithm_dropdown.currentText()
        result = self.run_algorithm(algorithm)
        
        if result is None:
            QMessageBox.information(self, 'Error', 'No solution found.')
            return
        
        self.steps = 0
        self.total_weight = result['weight']
        self.path = result['path']
        
        self.steps_label.setText(f"Steps: {self.steps}")
        self.cost_label.setText(f"Total Cost: {self.total_weight}")
        
        self.path_index = 0
        self.timer.start(150)
        
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
        
    def next_step(self):
        if self.path_index >= len(self.path):
            self.timer.stop()  # Stop the timer when path is complete
            return

        move = self.path[self.path_index]
        self.execute_move(move)
        self.path_index += 1
        self.steps += 1
        
        # Update the stats after each step
        self.steps_label.setText(f'Steps: {self.steps}')
        self.cost_label.setText(f'Total Cost: {self.total_weight}')
        
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
            self.grid[stone_row][stone_col] = '*' if self.grid[stone_row][stone_col] == '.' else '$'
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
        if self.grid[row][col] == '#':
            cell.setPixmap(self.assets['wall'])  # Wall
        elif self.grid[row][col] == '.':
            cell.setPixmap(self.assets['switch']) # Switch
        elif player:
            cell.setPixmap(self.assets['player']) # Player
        elif stone:
            if self.grid[row][col] == '*':
                cell.setPixmap(self.assets['stone_on_switch']) # Stone on switch
            else:
                cell.setPixmap(self.assets['stone']) # Stone
        else:
            cell.setPixmap(self.assets['blank']) # Empty cell
 
    def reset_map(self):
        # Stop any ongoing visualization if running
        if self.timer.isActive():
            self.timer.stop()
        # Reset the visualization (clear the steps, cost, and reset map)
        self.steps_label.setText('Steps: 0')
        self.cost_label.setText('Total Cost: 0')
        self.path_index = 0
        self.steps = 0
        self.total_weight = 0
        self.load_map()
        # QMessageBox.information(self, 'Reset', 'Map has been reset.')

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    sokoban_visualizer = SokobanVisualizer()
    sokoban_visualizer.show()
    sys.exit(app.exec_())
