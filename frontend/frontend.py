import sys
import requests
import matplotlib.pyplot as plt
from PyQt5.QtWidgets import (
    QApplication, QWidget, QVBoxLayout, QPushButton, QLabel, QMessageBox, 
    QLineEdit, QTextEdit, QListWidget, QTabWidget, QHBoxLayout, QGridLayout,
    QFrame, QSplitter, QComboBox, QScrollArea
)
from PyQt5.QtGui import QFont, QPalette, QColor, QIcon
from PyQt5.QtCore import Qt, QSize
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import matplotlib as mpl

# Set matplotlib to use dark background for all plots
plt.style.use('dark_background')
mpl.rcParams['text.color'] = 'white'
mpl.rcParams['axes.labelcolor'] = 'white'
mpl.rcParams['xtick.color'] = 'white'
mpl.rcParams['ytick.color'] = 'white'

class RoundedFrame(QFrame):
    """Custom rounded frame with subtle gradient"""
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFrameShape(QFrame.StyledPanel)
        self.setStyleSheet("""
            RoundedFrame {
                background-color: qlineargradient(x1:0, y1:0, x2:0, y2:1,
                                                  stop:0 #1E1E2E, stop:1 #181825);
                border-radius: 10px;
                border: 1px solid #333344;
                padding: 10px;
            }
        """)

class FinanceDashboard(QWidget):
    def __init__(self, user_id):
        super().__init__()
        self.user_id = user_id
        # Color palette - modern vibrant accents on dark background
        self.colors = {
            'bg_dark': '#0F0F17',
            'bg_card': '#1E1E2E',
            'accent1': '#F28C28',  # Vibrant orange
            'accent2': '#7B68EE',  # Medium slate blue
            'accent3': '#1ED760',  # Spotify green
            'accent4': '#E84393',  # Pink
            'text': '#E2E2E2',
            'text_dim': '#A0A0A0'
        }
        self.category_colors = ['#F28C28', '#7B68EE', '#1ED760', '#E84393', '#36D7B7', '#FF6B6B', '#FFD93D']
        self.initUI()

    def initUI(self):
        """Initialize UI with enhanced dark mode and better visuals"""
        self.setWindowTitle("💰 Finance Dashboard Pro")
        self.setGeometry(150, 80, 1280, 800)  # Slightly larger for better spacing
        
        # Apply enhanced dark mode with more color accents
        self.setStyleSheet(f"""
            QWidget {{ 
                background-color: {self.colors['bg_dark']}; 
                color: {self.colors['text']}; 
                font-size: 14px; 
                font-family: 'Segoe UI', 'Helvetica', sans-serif;
            }}
            QPushButton {{ 
                background-color: {self.colors['bg_card']}; 
                border-radius: 6px; 
                padding: 12px; 
                color: {self.colors['text']}; 
                font-weight: bold; 
                border: 1px solid #333344;
            }}
            QPushButton:hover {{ 
                background-color: #333344; 
                border: 1px solid {self.colors['accent2']};
            }}
            QLineEdit, QTextEdit, QListWidget, QComboBox {{ 
                background-color: #16161e; 
                border: 1px solid #333344; 
                border-radius: 6px; 
                padding: 10px; 
                color: {self.colors['text']}; 
            }}
            QLineEdit:focus, QTextEdit:focus {{ 
                border: 1px solid {self.colors['accent2']}; 
            }}
            QTabWidget::pane {{ 
                border: 1px solid #333344; 
                border-radius: 6px;
            }}
            QTabBar::tab {{ 
                background: #181825; 
                padding: 12px 20px; 
                color: {self.colors['text_dim']}; 
                margin-right: 2px; 
                border-top-left-radius: 6px; 
                border-top-right-radius: 6px;
            }}
            QTabBar::tab:selected {{ 
                background: {self.colors['bg_card']}; 
                color: {self.colors['text']}; 
                border-bottom: 2px solid {self.colors['accent2']};
            }}
            QTabBar::tab:hover:!selected {{ 
                background: #222235;
            }}
            QListWidget {{ 
                border-radius: 8px; 
                padding: 5px; 
                outline: none;
            }}
            QListWidget::item {{ 
                border-bottom: 1px solid #222235; 
                padding: 8px; 
                margin: 2px 0px;
            }}
            QListWidget::item:selected {{ 
                background-color: #2d2d44; 
                border-radius: 6px;
            }}
            QScrollBar:vertical {{ 
                border: none;
                background: {self.colors['bg_dark']};
                width: 10px;
                margin: 0px;
            }}
            QScrollBar::handle:vertical {{
                background: #333344;
                min-height: 25px;
                border-radius: 5px;
            }}
            QScrollBar::add-line:vertical, QScrollBar::sub-line:vertical {{
                height: 0px;
            }}
        """)

        main_layout = QVBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(15)

        # Header section with dashboard title
        header = QHBoxLayout()
        title_label = QLabel("Financial Dashboard")
        title_label.setStyleSheet(f"font-size: 22px; font-weight: bold; color: {self.colors['text']};")
        header.addWidget(title_label)
        
        # Add user info on the right
        user_info = QLabel(f"User ID: {self.user_id} | 💰")
        user_info.setStyleSheet(f"font-size: 14px; color: {self.colors['text_dim']};")
        user_info.setAlignment(Qt.AlignRight | Qt.AlignVCenter)
        header.addWidget(user_info)
        
        main_layout.addLayout(header)
        
        # Separator line
        separator = QFrame()
        separator.setFrameShape(QFrame.HLine)
        separator.setStyleSheet(f"background-color: #333344; margin-bottom: 10px;")
        main_layout.addWidget(separator)

        # **Navigation Tabs**
        self.tabs = QTabWidget(self)
        self.tabs.setStyleSheet("QTabWidget::pane { margin-top: -1px; }")
        self.expense_tab = QWidget()
        self.visualization_tab = QWidget()

        self.tabs.addTab(self.expense_tab, "📜 Expenses Manager")
        self.tabs.addTab(self.visualization_tab, "📊 Analytics Dashboard")

        main_layout.addWidget(self.tabs)

        # **Initialize Tabs**
        self.initExpenseTab()
        self.initVisualizationTab()

        self.setLayout(main_layout)

        # **Connect tab switch event**
        self.tabs.currentChanged.connect(self.refreshVisualizationTab)

    def initExpenseTab(self):
        """Setup the enhanced Expenses Tab"""
        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)

        # Input section in a card-like container
        input_frame = RoundedFrame()
        input_layout = QVBoxLayout(input_frame)
        
        input_title = QLabel("Add New Expense")
        input_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.colors['accent1']};")
        input_layout.addWidget(input_title)

        # Input grid for better organization
        input_grid = QGridLayout()
        input_grid.setColumnStretch(1, 1)  # Make the second column expandable
        
        # Amount with currency symbol
        amount_label = QLabel("Amount:")
        amount_label.setStyleSheet(f"color: {self.colors['text_dim']};")
        input_grid.addWidget(amount_label, 0, 0)
        
        amount_layout = QHBoxLayout()
        currency_label = QLabel("₹")
        currency_label.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.colors['accent1']};")
        amount_layout.addWidget(currency_label)
        
        self.amount_input = QLineEdit()
        self.amount_input.setPlaceholderText("Enter amount")
        amount_layout.addWidget(self.amount_input)
        input_grid.addLayout(amount_layout, 0, 1)
        
        # Category with predefined options
        category_label = QLabel("Category:")
        category_label.setStyleSheet(f"color: {self.colors['text_dim']};")
        input_grid.addWidget(category_label, 1, 0)
        
        self.category_input = QComboBox()
        self.category_input.setEditable(True)
        self.category_input.addItems(["Food", "Transport", "Entertainment", "Shopping", "Bills", "Health", "Other"])
        self.category_input.setPlaceholderText("Select or enter category")
        input_grid.addWidget(self.category_input, 1, 1)
        
        # Description
        desc_label = QLabel("Description:")
        desc_label.setStyleSheet(f"color: {self.colors['text_dim']};")
        input_grid.addWidget(desc_label, 2, 0, Qt.AlignTop)
        
        self.description_input = QTextEdit()
        self.description_input.setPlaceholderText("Enter description (optional)")
        self.description_input.setMaximumHeight(80)
        input_grid.addWidget(self.description_input, 2, 1)
        
        input_layout.addLayout(input_grid)
        
        # Action buttons with accent colors
        button_layout = QHBoxLayout()
        
        self.add_expense_btn = QPushButton("✅ Add Expense")
        self.add_expense_btn.setStyleSheet(f"""
            QPushButton {{
                background-color: {self.colors['accent3']};
                color: #000000;
                font-weight: bold;
            }}
            QPushButton:hover {{
                background-color: #1bc456;
            }}
        """)
        self.add_expense_btn.clicked.connect(self.add_expense)
        button_layout.addWidget(self.add_expense_btn)
        
        self.view_expenses_btn = QPushButton("🔄 Refresh List")
        self.view_expenses_btn.clicked.connect(self.view_expenses)
        button_layout.addWidget(self.view_expenses_btn)
        
        input_layout.addLayout(button_layout)
        tab_layout.addWidget(input_frame)
        
        # Expense list section in a card-like container
        list_frame = RoundedFrame()
        list_layout = QVBoxLayout(list_frame)
        
        list_header = QHBoxLayout()
        list_title = QLabel("Recent Expenses")
        list_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.colors['accent2']};")
        list_header.addWidget(list_title)
        
        self.expense_count = QLabel("0 items")
        self.expense_count.setStyleSheet(f"color: {self.colors['text_dim']};")
        self.expense_count.setAlignment(Qt.AlignRight)
        list_header.addWidget(self.expense_count)
        
        list_layout.addLayout(list_header)
        
        self.expense_list = QListWidget()
        self.expense_list.setAlternatingRowColors(True)
        self.expense_list.setStyleSheet(f"""
            QListWidget {{
                alternate-background-color: #1a1a2a;
            }}
        """)
        list_layout.addWidget(self.expense_list)
        
        tab_layout.addWidget(list_frame)
        tab_layout.setStretch(1, 1)  # Make the list section expandable
        
        self.expense_tab.setLayout(tab_layout)

    def initVisualizationTab(self):
        """Setup the enhanced Visualization Tab"""
        tab_layout = QVBoxLayout()
        tab_layout.setContentsMargins(15, 15, 15, 15)
        tab_layout.setSpacing(15)
        
        # Charts section
        charts_title = QLabel("Expense Analytics")
        charts_title.setStyleSheet(f"font-size: 16px; font-weight: bold; color: {self.colors['accent2']};")
        tab_layout.addWidget(charts_title)
        
        # Two charts side by side
        charts_layout = QHBoxLayout()
        
        # Bar chart in a card
        bar_frame = RoundedFrame()
        bar_layout = QVBoxLayout(bar_frame)
        
        bar_title = QLabel("Expense by Category")
        bar_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {self.colors['accent1']};")
        bar_layout.addWidget(bar_title)
        
        self.bar_canvas = FigureCanvas(Figure(figsize=(5, 4), facecolor='#1E1E2E'))
        bar_layout.addWidget(self.bar_canvas)
        charts_layout.addWidget(bar_frame)
        
        # Pie chart in a card
        pie_frame = RoundedFrame()
        pie_layout = QVBoxLayout(pie_frame)
        
        pie_title = QLabel("Expense Distribution")
        pie_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {self.colors['accent4']};")
        pie_layout.addWidget(pie_title)
        
        self.pie_canvas = FigureCanvas(Figure(figsize=(5, 4), facecolor='#1E1E2E'))
        pie_layout.addWidget(self.pie_canvas)
        charts_layout.addWidget(pie_frame)
        
        tab_layout.addLayout(charts_layout)
        
        # Summary section
        summary_frame = RoundedFrame()
        summary_layout = QVBoxLayout(summary_frame)
        
        summary_title = QLabel("Expense Summary")
        summary_title.setStyleSheet(f"font-size: 14px; font-weight: bold; color: {self.colors['accent3']};")
        summary_layout.addWidget(summary_title)
        
        summary_grid = QGridLayout()
        
        # Total spent label
        self.total_spent_label = QLabel("Total Spent: ₹0")
        self.total_spent_label.setStyleSheet(f"font-size: 16px; font-weight: bold;")
        summary_grid.addWidget(self.total_spent_label, 0, 0)
        
        # Biggest category label
        self.biggest_category_label = QLabel("Biggest Category: N/A")
        summary_grid.addWidget(self.biggest_category_label, 0, 1)
        
        # Additional summaries could be added here
        summary_layout.addLayout(summary_grid)
        
        # Action buttons for visualization options
        buttons_layout = QHBoxLayout()
        
        self.refresh_btn = QPushButton("🔄 Refresh Data")
        self.refresh_btn.clicked.connect(self.refreshVisualizationTab)
        buttons_layout.addWidget(self.refresh_btn)
        
        self.export_btn = QPushButton("📊 Export Chart")
        self.export_btn.clicked.connect(self.export_chart)
        buttons_layout.addWidget(self.export_btn)
        
        summary_layout.addLayout(buttons_layout)
        tab_layout.addWidget(summary_frame)
        
        self.visualization_tab.setLayout(tab_layout)

    def refreshVisualizationTab(self):
        """Refresh charts when switching to the visualization tab"""
        if self.tabs.currentIndex() == 1 or self.sender() == self.refresh_btn:  # Check if Visualization tab is active or refresh button clicked
            self.fetch_and_update_charts()

    def add_expense(self):
        """Send new expense data to backend & clear inputs after submission"""
        url = "http://127.0.0.1:5000/expenses"
        data = {
            "user_id": self.user_id,
            "date": "2024-03-09",
            "category": self.category_input.currentText().strip(),
            "amount": self.amount_input.text().strip(),
            "description": self.description_input.toPlainText().strip()
        }

        if not data["category"] or not data["amount"]:
            QMessageBox.warning(self, "⚠️ Warning", "Please fill in all required fields!")
            return

        try:
            data["amount"] = float(data["amount"])
        except ValueError:
            QMessageBox.warning(self, "⚠️ Warning", "Amount must be a number!")
            return

        response = requests.post(url, json=data)

        if response.status_code == 201:
            QMessageBox.information(self, "✅ Success", "Expense added successfully!")
            self.amount_input.clear()
            self.category_input.setCurrentIndex(-1)
            self.description_input.clear()
            self.view_expenses()
            # Refresh charts if on visualization tab
            if self.tabs.currentIndex() == 1:
                self.fetch_and_update_charts()
        else:
            QMessageBox.warning(self, "❌ Error", "Failed to add expense.")

    def view_expenses(self):
        """Fetch and display expenses from backend with enhanced formatting"""
        url = f"http://127.0.0.1:5000/expenses/{self.user_id}"
        response = requests.get(url)

        if response.status_code == 200:
            self.expense_list.clear()
            expenses = response.json()["expenses"]
            
            # Update expense count
            self.expense_count.setText(f"{len(expenses)} items")
            
            for exp in expenses:
                category = exp['category']
                # Create color indicator based on category
                color_indicator = "⬤ "  # Unicode circle
                
                # Create formatted item with better spacing and layout
                item_text = f"{color_indicator}{category} | ₹{exp['amount']:.2f}\n"
                item_text += f"     📅 {exp['date']} | ✏️ {exp['description']}"
                
                list_item = self.expense_list.addItem(item_text)
                
                # Set different colors for different categories
                category_hash = hash(category) % len(self.category_colors)
                item = self.expense_list.item(self.expense_list.count() - 1)
                item.setForeground(QColor(self.category_colors[category_hash]))
        else:
            QMessageBox.warning(self, "❌ Error", "Failed to fetch expenses.")

    def fetch_and_update_charts(self):
        """Fetch expense data and update all charts"""
        url = f"http://127.0.0.1:5000/visualize/{self.user_id}"
        response = requests.get(url)

        if response.status_code == 200:
            data = response.json()
            categories = data["categories"]
            amounts = data["amounts"]
            
            # Calculate total spent
            total = sum(amounts)
            self.total_spent_label.setText(f"Total Spent: ₹{total:.2f}")
            
            # Find biggest category
            if categories and amounts:
                max_index = amounts.index(max(amounts))
                self.biggest_category_label.setText(f"Biggest Category: {categories[max_index]} (₹{amounts[max_index]:.2f})")
            
            # Update Bar Chart
            self.update_bar_chart(categories, amounts)
            
            # Update Pie Chart
            self.update_pie_chart(categories, amounts)
        else:
            QMessageBox.warning(self, "❌ Error", "Failed to fetch data.")

    def update_bar_chart(self, categories, amounts):
        """Update the bar chart with the given data"""
        self.bar_canvas.figure.clear()
        ax_bar = self.bar_canvas.figure.add_subplot(111)
        
        # Generate color map from our palette
        bar_colors = [self.category_colors[i % len(self.category_colors)] for i in range(len(categories))]
        
        # Create the bars with better styling
        bars = ax_bar.bar(categories, amounts, color=bar_colors, width=0.6)
        
        # Add value labels on top of bars
        for bar in bars:
            height = bar.get_height()
            ax_bar.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                    f'₹{height:.0f}', ha='center', va='bottom', color='white', fontsize=9)
        
        # Style the chart
        ax_bar.set_title("Expense by Category", fontsize=12, pad=10)
        ax_bar.set_xlabel("Category", fontsize=10, labelpad=10)
        ax_bar.set_ylabel("Amount (₹)", fontsize=10, labelpad=10)
        ax_bar.spines['top'].set_visible(False)
        ax_bar.spines['right'].set_visible(False)
        ax_bar.spines['bottom'].set_color('#555555')
        ax_bar.spines['left'].set_color('#555555')
        ax_bar.tick_params(colors='#aaaaaa', labelsize=9)
        ax_bar.set_facecolor('#1E1E2E')
        
        self.bar_canvas.figure.tight_layout()
        self.bar_canvas.draw()

    def update_pie_chart(self, categories, amounts):
        """Update the pie chart with the given data"""
        self.pie_canvas.figure.clear()
        ax_pie = self.pie_canvas.figure.add_subplot(111)
        
        # Generate colors from our palette
        pie_colors = [self.category_colors[i % len(self.category_colors)] for i in range(len(categories))]
        
        # Create a prettier pie chart
        wedges, texts, autotexts = ax_pie.pie(
            amounts, 
            labels=categories, 
            autopct='%1.1f%%', 
            startangle=90, 
            colors=pie_colors,
            shadow=False, 
            wedgeprops={'edgecolor': '#1E1E2E', 'linewidth': 1},
            textprops={'color': 'white', 'fontsize': 9}
        )
        
        # Style the percentage text
        for autotext in autotexts:
            autotext.set_fontsize(8)
            autotext.set_fontweight('bold')
        
        ax_pie.set_title("Expense Distribution", fontsize=12, pad=10)
        
        # Create some spacing around the pie
        ax_pie.set_facecolor('#1E1E2E')
        
        self.pie_canvas.figure.tight_layout()
        self.pie_canvas.draw()

    def export_chart(self):
        """Export the current charts as images"""
        # Save both charts with date timestamp
        import datetime
        timestamp = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
        
        try:
            # Save bar chart
            self.bar_canvas.figure.savefig(f"expense_bar_{timestamp}.png", 
                                           facecolor='#1E1E2E', 
                                           bbox_inches='tight', 
                                           dpi=300)
            
            # Save pie chart
            self.pie_canvas.figure.savefig(f"expense_pie_{timestamp}.png", 
                                           facecolor='#1E1E2E', 
                                           bbox_inches='tight', 
                                           dpi=300)
            
            QMessageBox.information(self, "✅ Success", 
                                 f"Charts exported successfully as:\n- expense_bar_{timestamp}.png\n- expense_pie_{timestamp}.png")
        except Exception as e:
            QMessageBox.warning(self, "❌ Error", f"Failed to export charts: {str(e)}")

if __name__ == '__main__':
    app = QApplication(sys.argv)
    app.setStyle('Fusion')  # Use Fusion style for better cross-platform appearance
    user_id = 1
    dashboard = FinanceDashboard(user_id)
    dashboard.show()
    dashboard.view_expenses()  # Load expenses on startup
    sys.exit(app.exec_())