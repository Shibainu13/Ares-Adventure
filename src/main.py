
import sys
from PyQt5.QtWidgets import (
    QApplication, QWidget, QComboBox, QPushButton, QLabel,
    QVBoxLayout, QHBoxLayout, QGridLayout, QMessageBox
)
from PyQt5.QtCore import Qt
import search_algorithms._utils as _utils
import search_algorithms.dfs as DFS
import search_algorithms.bfs as BFS
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
        
        # Add top layout to main layout
        main_layout.addLayout(top_layout)
        
        # Grid Layout for Map
        self.grid_layout = QGridLayout()
        self.grid_layout.setSpacing(1)
        main_layout.addLayout(self.grid_layout)
        
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
        
        # Load Initial Map
        self.load_map()
    
    def load_map(self):
        # Get the selected map file
        map_file = self.maps[self.map_dropdown.currentIndex()]
        
        # Read and parse the map file
        with open(map_file, 'r') as f:
            input_data = f.read()
        stone_weights, grid = _utils.parse_input(input_data)
        ares_pos, stones, switches = _utils.find_positions(grid)
        
        # Clear the grid layout
        for i in reversed(range(self.grid_layout.count())):
            widget_to_remove = self.grid_layout.itemAt(i).widget()
            if widget_to_remove is not None:
                widget_to_remove.setParent(None)
        
        # Setup map dimensions
        map_height = len(grid)
        map_width = max(len(row) for row in grid)
        
        # Load textures based on cell type
        for row in range(map_height):
            for col in range(map_width):
                cell = QLabel()
                cell.setFixedSize(40, 40)
                
                if col < len(grid[row]):  # Check to avoid index error for uneven rows
                    cell_type = grid[row][col]
                    if cell_type == '#':
                        cell.setStyleSheet("background-color: gray; border: 1px solid black;")  # Wall
                    elif cell_type == '.':
                        cell.setStyleSheet("background-color: lightgreen; border: 1px solid black;")  # Switch
                    elif cell_type == '@':
                        cell.setStyleSheet("background-color: lightblue; border: 1px solid black;")  # Player
                    elif cell_type == '+':
                        cell.setStyleSheet("background-color: lightblue; border: 1px solid black;")  # Player on Switch
                    elif cell_type == '$':
                        cell.setStyleSheet("background-color: yellow; border: 1px solid black;")  # Stone
                    elif cell_type == '*':
                        cell.setStyleSheet("background-color: orange; border: 1px solid black;")  # Stone on Switch
                    else:
                        cell.setStyleSheet("background-color: white; border: 1px solid black;")  # Blank cell
                else:
                    cell.setStyleSheet("background-color: gray; border: 1px solid black;")   # Fill extra cells as wall
                
                # Add cell to grid layout
                self.grid_layout.addWidget(cell, row, col)
        
        # Adjust window size based on map size
        self.setFixedSize(map_width * 40 + 100, map_height * 40 + 150)
    
    def start_visualization(self):
        # Placeholder logic for starting the visualization
        QMessageBox.information(self, 'Start', 'Starting visualization...')
        # Implement the algorithm visualization logic here
        # Update steps_label and cost_label as the algorithm proceeds
    
    def reset_map(self):
        # Reset the visualization (clear the steps, cost, and reset map)
        self.steps_label.setText('Steps: 0')
        self.cost_label.setText('Total Cost: 0')
        self.load_map()
        QMessageBox.information(self, 'Reset', 'Map has been reset.')

# Run the application
if __name__ == '__main__':
    app = QApplication(sys.argv)
    sokoban_visualizer = SokobanVisualizer()
    sokoban_visualizer.show()
    sys.exit(app.exec_())
