from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLineEdit, QPushButton, \
    QTableWidgetItem, QTableWidget, QListWidget, QCompleter, QListWidgetItem

from aodp.api import get_prices_for_items
from aodr.api import get_item_data, get_item_by_id, get_item_by_name
from data import Price
from data.constants.city_markets import CityMarkets
from data.constants.recipes.recipe import Item

DEBUG = False


class MainWindow(QMainWindow):
    def __init__(self):
        super().__init__()
        self.setWindowTitle("Albion Online Market Tool")

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Market Tab
        self.market_tab = QWidget()
        self.tabs.addTab(self.market_tab, "Market Prices")
        self.market_layout = QVBoxLayout()
        self.market_tab.setLayout(self.market_layout)

        items = get_item_data()
        item_names = [item.name for item in items if item is not None]
        test = {i.item_id: i.name for i in items if i is not None}

        self.market_item_input = QLineEdit(self)
        completer_items = QCompleter(item_names, self)
        # completer_items.setCompletionMode(QCompleter.CompletionMode.UnfilteredPopupCompletion)
        # self.market_item_input.setText("t2_fiber")
        self.market_item_input.setCompleter(completer_items)
        self.market_item_input.returnPressed.connect(self.add_item)
        self.market_layout.addWidget(self.market_item_input)

        self.selected_items_list = QListWidget(self)
        self.market_layout.addWidget(self.selected_items_list)

        self.market_city_input = QLineEdit(self)
        self.market_city_input.setPlaceholderText("Enter City")
        self.market_layout.addWidget(self.market_city_input)

        self.market_button = QPushButton("Fetch Market Data", self)
        self.market_button.clicked.connect(self.fetch_market_data)
        self.market_layout.addWidget(self.market_button)

        self.market_table = QTableWidget(0, 4, self)
        self.market_table.setHorizontalHeaderLabels(["Item ID", "City", "Lowest Sell Price", "Highest Buy Price"])
        # self.market_table.setSortingEnabled(True)
        self.market_layout.addWidget(self.market_table)

        # Create Crafting Tools tab
        self.crafting_tab = QWidget()
        self.tabs.addTab(self.crafting_tab, "Crafting Tools")
        self.crafting_layout = QVBoxLayout()
        self.crafting_tab.setLayout(self.crafting_layout)

        self.crafting_item_input = QLineEdit(self)
        self.crafting_item_input.setPlaceholderText("Enter Item ID")
        self.crafting_layout.addWidget(self.crafting_item_input)

        self.crafting_quantity_input = QLineEdit(self)
        self.crafting_quantity_input.setPlaceholderText("Enter Quantity")
        self.crafting_layout.addWidget(self.crafting_quantity_input)

        self.crafting_button = QPushButton("Fetch Crafting Data", self)
        self.crafting_button.clicked.connect(self.fetch_crafting_data)
        self.crafting_layout.addWidget(self.crafting_button)

        self.crafting_table = QTableWidget(0, 3, self)
        self.crafting_table.setHorizontalHeaderLabels(["Material", "Quantity", "Price"])
        self.crafting_layout.addWidget(self.crafting_table)

        self.centralWidget().adjustSize()

    def fetch_market_data(self):
        self.market_table.setSortingEnabled(False)
        # Placeholder function to fetch market data
        item_ids = []
        for index in range(self.selected_items_list.count()):
            d: Item = self.selected_items_list.item(index).data(Qt.UserRole)
            if d:
                item_ids.append(d.item_id)

        city = self.market_city_input.text()
        # Fetch data and populate the table
        prices: [Price] = get_prices_for_items(item_ids)
        known_prices: [Price] = list(filter(lambda p: CityMarkets.UNKNOWN is not p.city_market, prices))
        if DEBUG:
            print(f"known prices: {known_prices}")
        self.market_table.setRowCount(len(known_prices))
        for row, entry in enumerate(known_prices):
            self.market_table.setItem(row, 0, QTableWidgetItem(str(entry.item_id)))
            self.market_table.setItem(row, 1, QTableWidgetItem(str(entry.city_market.city_name)))
            self.market_table.setItem(row, 2, QTableWidgetItem(str(entry.sell_price_min)))
            self.market_table.setItem(row, 3, QTableWidgetItem(str(entry.buy_price_max)))
        # print('**************')
        # print(prices)

        # Print table contents for debugging
        for row in range(self.market_table.rowCount()):
            for column in range(self.market_table.columnCount()):
                item = self.market_table.item(row, column)
                if item:
                    print(f"Table item at ({row}, {column}): {item.text()}")
                else:
                    print(f"Table item at ({row}, {column}): None")
        self.market_table.setSortingEnabled(True)

    def fetch_crafting_data(self):
        # Placeholder function to fetch crafting data
        item_id = self.crafting_item_input.text()
        quantity = self.crafting_quantity_input.text()
        # Fetch data and populate the table
        # Example data
        data = [
            {"material": "Material 1", "quantity": 10, "price": 50},
            {"material": "Material 2", "quantity": 5, "price": 30}
        ]
        self.crafting_table.setRowCount(len(data))
        for row, entry in enumerate(data):
            self.crafting_table.setItem(row, 0, QTableWidgetItem(entry["material"]))
            self.crafting_table.setItem(row, 1, QTableWidgetItem(str(entry["quantity"])))
            self.crafting_table.setItem(row, 2, QTableWidgetItem(str(entry["price"])))

    def add_item(self):
        item_text = self.market_item_input.text()
        if item_text:
            item = QListWidgetItem(item_text)
            item.setData(Qt.UserRole, get_item_by_name(item_text))
            self.selected_items_list.addItem(item)
            self.market_item_input.clear()


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()