from collections import defaultdict

from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtWidgets import QApplication, QMainWindow, QWidget, QVBoxLayout, QTabWidget, QLineEdit, QPushButton, \
    QTableWidgetItem, QTableWidget, QListWidget, QCompleter, QListWidgetItem, QHBoxLayout, QLabel, QScrollArea

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
        self.setMinimumHeight(400)
        self.setMinimumWidth(600)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        # Create Market Tab
        self.market_tab = QTabWidget()
        self.tabs.addTab(self.market_tab, "Market")
        self.market_layout = QVBoxLayout()
        self.market_tab.setLayout(self.market_layout)

        self.prices_tab = QTabWidget()
        self.market_tab.addTab(self.prices_tab, "Prices")
        self.prices_layout = QVBoxLayout()
        self.prices_tab.setLayout(self.prices_layout)

        self.mt_trade_routes = QWidget()
        self.market_tab.addTab(self.mt_trade_routes, "Trade Routes")
        self.trade_routes_layout = QVBoxLayout()
        self.mt_trade_routes.setLayout(self.trade_routes_layout)

        self.tr_info = QLabel('This is a placeholder for some stuff')
        self.trade_routes_layout.addWidget(self.tr_info)

        items = get_item_data()
        item_names = [item.name for item in items if item is not None]
        test = {i.item_id: i.name for i in items if i is not None}

        self.market_item_input = QLineEdit(self)
        completer_items = QCompleter(item_names, self)
        completer_items.activated.connect(self.add_clicked_item)
        completer_items.setFilterMode(Qt.MatchContains)
        completer_items.setCaseSensitivity(Qt.CaseInsensitive)
        self.market_item_input.setCompleter(completer_items)
        self.prices_layout.addWidget(self.market_item_input)

        self.selected_items_list = QListWidget(self)
        self.selected_items_list.setMaximumHeight(100)
        self.selected_items_list.itemClicked.connect(self.add_clicked_item)
        self.prices_layout.addWidget(self.selected_items_list)

        self.market_city_input = QLineEdit(self)
        self.market_city_input.setPlaceholderText("Enter City")
        self.prices_layout.addWidget(self.market_city_input)

        self.market_buttons_layout = QHBoxLayout()
        self.market_button = QPushButton("Fetch Market Data", self)
        self.market_button.clicked.connect(self.fetch_market_data)
        self.market_buttons_layout.addWidget(self.market_button)

        self.clear_search_list_button = QPushButton("Clear Search List", self)
        self.clear_search_list_button.clicked.connect(self.clear_search_list)
        self.market_buttons_layout.addWidget(self.clear_search_list_button)

        self.prices_layout.addLayout(self.market_buttons_layout)

        self.market_result_area = QScrollArea()
        self.market_result_widget = QWidget()
        self.market_result_layout = QVBoxLayout()
        self.market_result_widget.setLayout(self.market_result_layout)
        self.market_result_area.setWidget(self.market_result_widget)
        self.market_result_area.setWidgetResizable(True)
        self.prices_layout.addWidget(self.market_result_area)

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
        item_ids = [self.selected_items_list.item(index).data(Qt.UserRole).item_id
                    for index in range(self.selected_items_list.count())]
        city = self.market_city_input.text()

        # Fetch data and populate the table
        prices = get_prices_for_items(item_ids)
        known_prices = list(filter(lambda p: CityMarkets.UNKNOWN is not p.city_market and p.sell_price_min != 0 or p.buy_price_max != 0, prices))
        result_map = defaultdict(list)
        for p in known_prices:
            result_map[p.item_id].append(p)

        if DEBUG:
            print(f"known prices: {known_prices}")
            print(f"result map: {result_map}")

        for item_id, price_list in result_map.items():
            wrapper = QWidget()
            wrapper_layout = QVBoxLayout()
            wrapper.setLayout(wrapper_layout)
            label = QLabel(get_item_by_id(item_id).name)
            wrapper_layout.addWidget(label)
            market_table = QTableWidget(0, 3, self)
            market_table.setMaximumHeight(len(price_list) * 20)
            market_table.setHorizontalHeaderLabels(["City", "Lowest Sell Price", "Highest Buy Price"])
            market_table.setSortingEnabled(False)
            market_table.setRowCount(len(price_list))
            wrapper_layout.addWidget(market_table)
            for row, price in enumerate(price_list):
                market_table.setItem(row, 0, QTableWidgetItem(str(price.city_market.city_name)))
                market_table.setItem(row, 1, QTableWidgetItem(str(price.sell_price_min)))
                market_table.setItem(row, 2, QTableWidgetItem(str(price.buy_price_max)))
            market_table.setSortingEnabled(True)
            self.market_result_layout.addWidget(wrapper)

        if DEBUG:
            for row in range(market_table.rowCount()):
                for column in range(market_table.columnCount()):
                    item = market_table.item(row, column)
                    if item:
                        print(f"Table item at ({row}, {column}): {item.text()}")
                    else:
                        print(f"Table item at ({row}, {column}): None")

    def clear_search_list(self):
        self.selected_items_list.clear()

    def fetch_crafting_data(self):
        item_id = self.crafting_item_input.text()
        quantity = self.crafting_quantity_input.text()
        data = [
            {"material": "Material 1", "quantity": 10, "price": 50},
            {"material": "Material 2", "quantity": 5, "price": 30}
        ]
        self.crafting_table.setRowCount(len(data))
        for row, entry in enumerate(data):
            self.crafting_table.setItem(row, 0, QTableWidgetItem(entry["material"]))
            self.crafting_table.setItem(row, 1, QTableWidgetItem(str(entry["quantity"])))
            self.crafting_table.setItem(row, 2, QTableWidgetItem(str(entry["price"])))

    def add_clicked_item(self, item: str):
        new_item = QListWidgetItem(item)
        new_item.setData(Qt.UserRole, get_item_by_name(item))
        self.selected_items_list.addItem(new_item)
        QTimer.singleShot(0, self.market_item_input.clear)


app = QApplication([])
window = MainWindow()
window.show()
app.exec_()
