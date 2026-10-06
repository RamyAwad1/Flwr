import sqlite3
import random
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QLabel, QTableWidgetItem, 
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QMessageBox, QTabWidget, QTableWidget, 
                             QHeaderView, QInputDialog, QFrame, QAbstractItemView,
                             QDialog, QComboBox, QStackedWidget, QGridLayout)
from PyQt6.QtCore import Qt

class CustomerDialog(QDialog):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.setWindowTitle("Select or Add Customer")
        self.setFixedSize(400, 300)
        self.setStyleSheet("""
            QDialog { background-color: #1a1a1a; font-family: 'Segoe UI', Arial, sans-serif; }
            QLabel { color: white; font-size: 16px; font-weight: bold; }
            QComboBox { background-color: #2b2b2b; color: white; border: 1px solid #444; border-radius: 6px; padding: 10px; font-size: 14px; }
            QLineEdit { background-color: #2b2b2b; color: white; border: 1px solid #444; border-radius: 6px; padding: 10px; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #9b59b6; }
            QPushButton { background-color: #9b59b6; color: white; border: none; border-radius: 6px; padding: 10px; font-size: 14px; font-weight: bold; }
            QPushButton:hover { background-color: #8e44ad; }
            QPushButton#toggleBtn { background-color: transparent; color: #9b59b6; text-decoration: underline; }
            QPushButton#toggleBtn:hover { color: white; }
        """)

        self.layout = QVBoxLayout(self)
        self.is_new_customer = False
        self.selected_customer_id = None
        self.selected_customer_name = None

        self.stack = QStackedWidget()
        
        self.page_existing = QWidget()
        layout_existing = QVBoxLayout(self.page_existing)
        layout_existing.addWidget(QLabel("Select Existing Customer:"))
        self.combo_customers = QComboBox()
        self.load_customers_into_combo()
        layout_existing.addWidget(self.combo_customers)
        
        self.btn_switch_to_new = QPushButton("Or Add New Customer")
        self.btn_switch_to_new.setObjectName("toggleBtn")
        self.btn_switch_to_new.clicked.connect(self.switch_to_new)
        layout_existing.addWidget(self.btn_switch_to_new)
        layout_existing.addStretch()

        self.page_new = QWidget()
        layout_new = QVBoxLayout(self.page_new)
        layout_new.addWidget(QLabel("New Customer Details:"))
        self.input_new_name = QLineEdit()
        self.input_new_name.setPlaceholderText("Full Name (Required)")
        layout_new.addWidget(self.input_new_name)
        
        self.input_new_phone = QLineEdit()
        self.input_new_phone.setPlaceholderText("Phone Number (Optional)")
        layout_new.addWidget(self.input_new_phone)

        self.btn_switch_to_existing = QPushButton("Back to Existing Customers")
        self.btn_switch_to_existing.setObjectName("toggleBtn")
        self.btn_switch_to_existing.clicked.connect(self.switch_to_existing)
        layout_new.addWidget(self.btn_switch_to_existing)
        layout_new.addStretch()

        self.stack.addWidget(self.page_existing)
        self.stack.addWidget(self.page_new)
        self.layout.addWidget(self.stack)

        self.btn_confirm = QPushButton("Confirm")
        self.btn_confirm.clicked.connect(self.process_selection)
        self.layout.addWidget(self.btn_confirm)

    def load_customers_into_combo(self):
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, phone_number FROM customers ORDER BY name")
            self.customers_data = cursor.fetchall()
            conn.close()

            for cust in self.customers_data:
                display_text = f"{cust[1]}" + (f" ({cust[2]})" if cust[2] else "")
                self.combo_customers.addItem(display_text, userData=cust[0]) 
        except Exception as e:
            pass

    def switch_to_new(self):
        self.is_new_customer = True
        self.stack.setCurrentIndex(1)

    def switch_to_existing(self):
        self.is_new_customer = False
        self.stack.setCurrentIndex(0)

    def process_selection(self):
        if self.is_new_customer:
            name = self.input_new_name.text().strip()
            if not name:
                QMessageBox.warning(self, "Error", "Name is required for a new customer.")
                return
            self.new_phone = self.input_new_phone.text().strip()
            self.selected_customer_name = name
        else:
            if self.combo_customers.count() == 0:
                QMessageBox.warning(self, "Error", "No existing customers. Please add a new one.")
                return
            self.selected_customer_id = self.combo_customers.currentData()
            self.selected_customer_name = self.combo_customers.currentText().split(" (")[0]
        self.accept()

# --- MAIN WINDOW ---
class MainWindow(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        
        self.cart_data = [] 
        self.cart_total = 0.0
        self.selected_customer_id = None
        self.current_storage_category = None
        
        # Auto-upgrade database for payments and dynamic categories
        self._ensure_payment_table()
        self._ensure_category_system()
        
        self.setWindowTitle(f"flwr - {self.role} Panel")
        self.setGeometry(100, 100, 1200, 800) 
        
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; font-family: 'Segoe UI', Arial, sans-serif; }
            QTabWidget::pane { border: none; background: #1a1a1a; }
            QTabBar::tab { background: #2b2b2b; color: #aaaaaa; padding: 12px 25px; font-size: 15px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; }
            QTabBar::tab:selected { background: #9b59b6; color: white; font-weight: bold; }
            QTabBar::tab:hover:!selected { background: #3a3a3a; color: white; }
            QLabel { color: #ffffff; }
            QLineEdit, QComboBox { background-color: #2b2b2b; color: white; border: 1px solid #444; border-radius: 6px; padding: 10px; font-size: 14px; }
            QLineEdit:focus, QComboBox:focus { border: 1px solid #9b59b6; background-color: #333; }
            QPushButton { background-color: #9b59b6; color: white; border: none; border-radius: 6px; padding: 12px; font-size: 15px; font-weight: bold; }
            QPushButton:hover { background-color: #8e44ad; }
            QPushButton:disabled { background-color: #555555; color: #888888; }
            QPushButton#checkoutBtn { background-color: #27ae60; font-size: 18px; padding: 15px; } 
            QPushButton#checkoutBtn:hover { background-color: #2ecc71; }
            QPushButton#checkoutBtn:disabled { background-color: #1b4d2e; color: #888888; }
            QPushButton#debtBtn { background-color: #e74c3c; font-size: 18px; padding: 15px; } 
            QPushButton#debtBtn:hover { background-color: #c0392b; }
            QPushButton#secondaryBtn { background-color: #444444; }
            QPushButton#secondaryBtn:hover { background-color: #555555; }
            
            QTableWidget { background-color: #2b2b2b; color: white; font-size: 14px; border: none; border-radius: 8px; alternate-background-color: #222222; outline: none; }
            QTableWidget::item { padding: 5px; border-bottom: 1px solid #333; }
            QTableWidget::item:selected { background-color: #9b59b6; color: white; }
            QHeaderView::section { background-color: #9b59b6; color: white; padding: 5px; border: none; font-weight: bold; font-size: 14px; min-height: 35px; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        if self.role == "Admin":
            self.setup_admin_tabs()
        else:
            self.setup_user_tabs()

    def _ensure_payment_table(self):
        conn = sqlite3.connect('store_database.db')
        cursor = conn.cursor()
        cursor.execute('''CREATE TABLE IF NOT EXISTS debt_payments (
            id INTEGER PRIMARY KEY AUTOINCREMENT, customer_id INTEGER, user_id INTEGER,
            timestamp DATETIME DEFAULT CURRENT_TIMESTAMP, amount REAL,
            FOREIGN KEY(customer_id) REFERENCES customers(id), FOREIGN KEY(user_id) REFERENCES users(id))''')
        conn.commit()
        conn.close()

    def _ensure_category_system(self):
        conn = sqlite3.connect('store_database.db')
        cursor = conn.cursor()
        
        cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in cursor.fetchall()]
        if 'category' not in columns:
            cursor.execute("ALTER TABLE products ADD COLUMN category TEXT DEFAULT '📦 Uncategorized'")
            
        cursor.execute('''CREATE TABLE IF NOT EXISTS categories (
            id INTEGER PRIMARY KEY AUTOINCREMENT, name TEXT UNIQUE, color TEXT)''')
            
        cursor.execute("SELECT COUNT(*) FROM categories")
        if cursor.fetchone()[0] == 0:
            defaults = [
                ("⚡ Wires & Cables", "#f1c40f"),
                ("🔧 Tools", "#e67e22"),
                ("💡 Lighting", "#f39c12"),
                ("⚙️ Hardware", "#7f8c8d"),
                ("📦 Uncategorized", "#95a5a6")
            ]
            cursor.executemany("INSERT INTO categories (name, color) VALUES (?, ?)", defaults)
            
        conn.commit()
        conn.close()

    def setup_admin_tabs(self):
        self.tab_dashboard = QWidget()
        self.tab_dashboard.setLayout(QVBoxLayout())
        self.tab_dashboard.layout().addWidget(QLabel("Dashboard: Charts go here."))

        self.build_storage_management()
        self.build_debt_viewer()

        self.tab_sales = QWidget()
        self.tab_sales.setLayout(QVBoxLayout())
        self.tab_sales.layout().addWidget(QLabel("Sales History goes here."))

        self.tabs.addTab(self.tab_dashboard, "Dashboard")
        self.tabs.addTab(self.tab_storage, "Storage")
        self.tabs.addTab(self.tab_debt, "Customer Debt")
        self.tabs.addTab(self.tab_sales, "Sales History")

    def setup_user_tabs(self):
        self.build_cash_register()
        self.build_debt_viewer()
        self.build_storage_management()

        self.tabs.addTab(self.tab_register, "Cash Register")
        self.tabs.addTab(self.tab_debt, "Customer Debt")
        self.tabs.addTab(self.tab_storage, "Storage")

    # --- UI BUILDING FUNCTIONS ---

    def build_cash_register(self):
        self.tab_register = QWidget()
        main_layout = QHBoxLayout() 
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        self.cart_table = QTableWidget(0, 4) 
        self.cart_table.setHorizontalHeaderLabels(["Item Name", "Quantity", "Unit Price", "Subtotal"])
        self.cart_table.setAlternatingRowColors(True)
        self.cart_table.setShowGrid(False)
        self.cart_table.verticalHeader().setVisible(False) 
        
        header = self.cart_table.horizontalHeader()
        header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        main_layout.addWidget(self.cart_table, 2) 

        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: #222222; border-radius: 12px; padding: 10px; }")
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        add_label = QLabel("Add Item to Cart")
        add_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #9b59b6; border: none;")
        right_panel.addWidget(add_label)

        self.search_input = QLineEdit()
        self.search_input.setPlaceholderText("Enter Product Name or Barcode...")
        self.search_input.returnPressed.connect(self.add_item_to_cart)
        right_panel.addWidget(self.search_input)

        self.qty_input = QLineEdit()
        self.qty_input.setPlaceholderText("Quantity (Default: 1)")
        self.qty_input.returnPressed.connect(self.add_item_to_cart)
        right_panel.addWidget(self.qty_input)

        self.add_btn = QPushButton("Add to Cart")
        self.add_btn.clicked.connect(self.add_item_to_cart)
        right_panel.addWidget(self.add_btn)

        right_panel.addStretch() 

        self.total_label = QLabel("Total: 0.00 JOD")
        self.total_label.setStyleSheet("font-size: 36px; font-weight: bold; color: white; border: none;")
        self.total_label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        right_panel.addWidget(self.total_label)

        self.checkout_cash_btn = QPushButton("Complete Sale (Cash)")
        self.checkout_cash_btn.setObjectName("checkoutBtn")
        self.checkout_cash_btn.clicked.connect(self.complete_cash_sale)
        right_panel.addWidget(self.checkout_cash_btn)

        self.checkout_debt_btn = QPushButton("Add to Customer Debt")
        self.checkout_debt_btn.setObjectName("debtBtn")
        self.checkout_debt_btn.clicked.connect(self.complete_debt_sale)
        right_panel.addWidget(self.checkout_debt_btn)

        right_frame.setLayout(right_panel)
        main_layout.addWidget(right_frame, 1) 
        self.tab_register.setLayout(main_layout)

    def build_storage_management(self):
        self.tab_storage = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)
        
        # --- LEFT SIDE: The Stacked Interface (Categories -> Table) ---
        self.storage_stack = QStackedWidget()
        main_layout.addWidget(self.storage_stack, 2)

        # PAGE 1: Category Grid
        self.page_categories = QWidget()
        self.category_grid_layout = QGridLayout(self.page_categories)
        self.category_grid_layout.setSpacing(20)
        
        # PAGE 2: The Specific Inventory Table
        self.page_inventory = QWidget()
        inv_layout = QVBoxLayout(self.page_inventory)
        inv_layout.setContentsMargins(0,0,0,0)

        header_layout = QHBoxLayout()
        self.back_btn = QPushButton("← Back to Categories")
        self.back_btn.setObjectName("secondaryBtn")
        self.back_btn.clicked.connect(lambda: self.storage_stack.setCurrentIndex(0))
        header_layout.addWidget(self.back_btn)
        
        self.cat_title_label = QLabel("Category")
        self.cat_title_label.setStyleSheet("font-size: 24px; font-weight: bold; color: #9b59b6; margin-left: 20px;")
        header_layout.addWidget(self.cat_title_label)
        header_layout.addStretch()
        
        inv_layout.addLayout(header_layout)

        self.inventory_table = QTableWidget(0, 6)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Barcode", "Name", "Stock", "Cost (JOD)", "Sell (JOD)"])
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setShowGrid(False)
        self.inventory_table.verticalHeader().setVisible(False) 
        
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) 
        inv_layout.addWidget(self.inventory_table)

        self.storage_stack.addWidget(self.page_categories)
        self.storage_stack.addWidget(self.page_inventory)
        
        # --- RIGHT SIDE: Add New Product Form ---
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: #222222; border-radius: 12px; padding: 10px; }")
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        title_label = QLabel("Add New Product")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #9b59b6; border: none;")
        right_panel.addWidget(title_label)

        self.prod_category = QComboBox()
        right_panel.addWidget(self.prod_category)
        
        self.prod_barcode = QLineEdit()
        self.prod_barcode.setPlaceholderText("Barcode (Optional)")
        right_panel.addWidget(self.prod_barcode)
        
        self.prod_name = QLineEdit()
        self.prod_name.setPlaceholderText("Product Name (Required)")
        right_panel.addWidget(self.prod_name)
        
        self.prod_qty = QLineEdit()
        self.prod_qty.setPlaceholderText("Quantity in Stock")
        right_panel.addWidget(self.prod_qty)
        
        self.prod_cost = QLineEdit()
        self.prod_cost.setPlaceholderText("Cost Price (e.g. 1.50)")
        right_panel.addWidget(self.prod_cost)
        
        self.prod_sell = QLineEdit()
        self.prod_sell.setPlaceholderText("Selling Price (e.g. 3.00)")
        right_panel.addWidget(self.prod_sell)
        
        self.save_prod_btn = QPushButton("Save Product")
        self.save_prod_btn.clicked.connect(self.save_new_product)
        right_panel.addWidget(self.save_prod_btn)
        
        right_panel.addStretch()
        
        self.refresh_btn = QPushButton("Refresh Table")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.clicked.connect(self.load_inventory)
        right_panel.addWidget(self.refresh_btn)
        
        right_frame.setLayout(right_panel)
        main_layout.addWidget(right_frame, 1)
        
        self.tab_storage.setLayout(main_layout)
        
        # Load the dynamic UI
        self.load_categories_ui()

    def build_debt_viewer(self):
        self.tab_debt = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        self.debt_customers_table = QTableWidget(0, 4)
        self.debt_customers_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Total Debt (JOD)"])
        self.debt_customers_table.setAlternatingRowColors(True)
        self.debt_customers_table.setShowGrid(False)
        self.debt_customers_table.verticalHeader().setVisible(False) 
        
        self.debt_customers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.debt_customers_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.debt_customers_table.setColumnHidden(0, True) 

        header = self.debt_customers_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) 
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) 
        main_layout.addWidget(self.debt_customers_table, 1)

        self.debt_customers_table.itemSelectionChanged.connect(self.on_customer_selected)

        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: #222222; border-radius: 12px; padding: 10px; }")
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        self.debt_target_label = QLabel("Select a customer from the list...")
        self.debt_target_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #9b59b6; border: none;")
        right_panel.addWidget(self.debt_target_label)

        self.debt_history_table = QTableWidget(0, 4)
        self.debt_history_table.setHorizontalHeaderLabels(["Date & Time", "Type", "Cashier", "Amount (JOD)"])
        self.debt_history_table.setAlternatingRowColors(True)
        self.debt_history_table.setShowGrid(False)
        self.debt_history_table.verticalHeader().setVisible(False) 

        h_header = self.debt_history_table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        h_header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) 
        right_panel.addWidget(self.debt_history_table)

        self.pay_debt_btn = QPushButton("Process New Payment")
        self.pay_debt_btn.setObjectName("checkoutBtn") 
        self.pay_debt_btn.setEnabled(False) 
        self.pay_debt_btn.clicked.connect(self.make_debt_payment)
        right_panel.addWidget(self.pay_debt_btn)

        right_frame.setLayout(right_panel)
        main_layout.addWidget(right_frame, 2) 

        self.tab_debt.setLayout(main_layout)
        self.load_debt_customers()

    # --- DYNAMIC CATEGORY LOGIC ---
    
    def clear_layout(self, layout):
        while layout.count():
            child = layout.takeAt(0)
            if child.widget():
                child.widget().deleteLater()

    def load_categories_ui(self):
        self.clear_layout(self.category_grid_layout)
        self.prod_category.clear()
        
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT name, color FROM categories ORDER BY id")
            categories = cursor.fetchall()
            conn.close()

            row, col = 0, 0
            for cat_name, color in categories:
                self.prod_category.addItem(cat_name)
                
                btn = QPushButton(cat_name)
                btn.setStyleSheet(f"""
                    QPushButton {{
                        background-color: #222222; color: white; border: 2px solid {color};
                        border-radius: 12px; font-size: 22px; font-weight: bold; padding: 40px;
                    }}
                    QPushButton:hover {{ background-color: {color}; color: #111111; }}
                """)
                btn.clicked.connect(lambda checked, c=cat_name: self.open_storage_category(c))
                self.category_grid_layout.addWidget(btn, row, col)
                
                col += 1
                if col > 1: # 2 columns wide
                    col = 0
                    row += 1

            # NEW: Add Category Button
            add_btn = QPushButton("➕ Add Category")
            add_btn.setStyleSheet("""
                QPushButton { background-color: #2b2b2b; color: #9b59b6; border: 2px dashed #9b59b6;
                              border-radius: 12px; font-size: 22px; font-weight: bold; padding: 40px; }
                QPushButton:hover { background-color: #9b59b6; color: white; }
            """)
            add_btn.clicked.connect(self.prompt_add_category)
            self.category_grid_layout.addWidget(add_btn, row, col)
            
            col += 1
            if col > 1:
                col = 0
                row += 1

            # NEW: Remove Category Button
            rem_btn = QPushButton("🗑️ Remove Category")
            rem_btn.setStyleSheet("""
                QPushButton { background-color: #2b2b2b; color: #e74c3c; border: 2px dashed #e74c3c;
                              border-radius: 12px; font-size: 22px; font-weight: bold; padding: 40px; }
                QPushButton:hover { background-color: #e74c3c; color: white; }
            """)
            rem_btn.clicked.connect(self.prompt_remove_category)
            self.category_grid_layout.addWidget(rem_btn, row, col)
            
        except Exception as e:
            pass

    def prompt_add_category(self):
        name, ok = QInputDialog.getText(self, "New Category", "Enter category name (e.g., 🪛 Screws):")
        if ok and name.strip():
            name = name.strip()
            colors = ["#1abc9c", "#3498db", "#9b59b6", "#e74c3c", "#34495e", "#2ecc71", "#e67e22"]
            color = random.choice(colors)
            
            try:
                conn = sqlite3.connect('store_database.db')
                cursor = conn.cursor()
                cursor.execute("INSERT INTO categories (name, color) VALUES (?, ?)", (name, color))
                conn.commit()
                conn.close()
                self.load_categories_ui() 
            except sqlite3.IntegrityError:
                self.show_popup("Error", f"The category '{name}' already exists.", True)

    def prompt_remove_category(self):
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            
            # Prevent deletion of the default Uncategorized bucket
            cursor.execute("SELECT name FROM categories WHERE name != '📦 Uncategorized' ORDER BY name")
            categories = [row[0] for row in cursor.fetchall()]
            conn.close()

            if not categories:
                self.show_popup("Info", "There are no custom categories to remove.")
                return

            category_to_remove, ok = QInputDialog.getItem(
                self, "Remove Category", 
                "Select a category to delete:\n(Any products inside will be safely moved to '📦 Uncategorized')", 
                categories, 0, False
            )

            if ok and category_to_remove:
                # Add an extra layer of protection
                reply = QMessageBox.question(
                    self, 'Confirm Deletion',
                    f"Are you sure you want to permanently delete '{category_to_remove}'?\n\nAny products inside will be safely moved to '📦 Uncategorized'.",
                    QMessageBox.StandardButton.Yes | QMessageBox.StandardButton.No, 
                    QMessageBox.StandardButton.No
                )

                if reply == QMessageBox.StandardButton.Yes:
                    conn = sqlite3.connect('store_database.db')
                    cursor = conn.cursor()
                    
                    # 1. Safely move orphaned products
                    cursor.execute("UPDATE products SET category = '📦 Uncategorized' WHERE category = ?", (category_to_remove,))
                    
                    # 2. Delete the category
                    cursor.execute("DELETE FROM categories WHERE name = ?", (category_to_remove,))
                    
                    conn.commit()
                    conn.close()
                    
                    self.show_popup("Success", f"Category '{category_to_remove}' has been removed.")
                    self.load_categories_ui() 
        except Exception as e:
            self.show_popup("Database Error", f"Failed to remove category: {e}", True)

    def open_storage_category(self, category_name):
        self.current_storage_category = category_name
        self.cat_title_label.setText(f"Inventory: {category_name}")
        self.storage_stack.setCurrentIndex(1)
        self.load_inventory()

    # --- DEBT VIEWER LOGIC ---
    def load_debt_customers(self):
        self.debt_customers_table.setRowCount(0)
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, phone_number, total_debt FROM customers WHERE total_debt > 0 ORDER BY name")
            rows = cursor.fetchall()
            conn.close()

            for row_data in rows:
                row_pos = self.debt_customers_table.rowCount()
                self.debt_customers_table.insertRow(row_pos)
                
                self.debt_customers_table.setItem(row_pos, 0, QTableWidgetItem(str(row_data[0])))
                self.debt_customers_table.setItem(row_pos, 1, QTableWidgetItem(str(row_data[1])))
                phone = row_data[2] if row_data[2] else "N/A"
                self.debt_customers_table.setItem(row_pos, 2, QTableWidgetItem(phone))
                self.debt_customers_table.setItem(row_pos, 3, QTableWidgetItem(f"{row_data[3]:.2f}"))
        except Exception as e:
            pass

    def on_customer_selected(self):
        selected_rows = self.debt_customers_table.selectedItems()
        if not selected_rows: return
            
        row = selected_rows[0].row()
        self.selected_customer_id = self.debt_customers_table.item(row, 0).text()
        customer_name = self.debt_customers_table.item(row, 1).text()
        total_owed = self.debt_customers_table.item(row, 3).text()

        self.debt_target_label.setText(f"{customer_name}'s Ledger (Owes: {total_owed} JOD)")
        self.pay_debt_btn.setEnabled(True) 
        self.load_customer_history(self.selected_customer_id)

    def load_customer_history(self, customer_id):
        self.debt_history_table.setRowCount(0)
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("""
                SELECT timestamp, 'Purchase' as type, users.username, total_amount 
                FROM sales JOIN users ON sales.user_id = users.id 
                WHERE customer_id = ?
                UNION ALL
                SELECT timestamp, 'Payment' as type, users.username, amount 
                FROM debt_payments JOIN users ON debt_payments.user_id = users.id 
                WHERE customer_id = ?
                ORDER BY timestamp DESC
            """, (customer_id, customer_id))
            
            rows = cursor.fetchall()
            conn.close()

            for row_data in rows:
                row_pos = self.debt_history_table.rowCount()
                self.debt_history_table.insertRow(row_pos)
                
                raw_timestamp = row_data[0]
                try:
                    dt_obj = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S")
                    clean_date = dt_obj.strftime("%d %b %Y, %I:%M %p")
                except ValueError:
                    clean_date = raw_timestamp 

                self.debt_history_table.setItem(row_pos, 0, QTableWidgetItem(clean_date))
                
                type_item = QTableWidgetItem(str(row_data[1]))
                if row_data[1] == 'Payment':
                    type_item.setForeground(Qt.GlobalColor.green)
                    
                self.debt_history_table.setItem(row_pos, 1, type_item)
                self.debt_history_table.setItem(row_pos, 2, QTableWidgetItem(str(row_data[2])))
                self.debt_history_table.setItem(row_pos, 3, QTableWidgetItem(f"{row_data[3]:.2f}"))
        except Exception as e:
            self.show_popup("Database Error", f"Failed to load history: {e}", True)

    def make_debt_payment(self):
        if not self.selected_customer_id: return
            
        amount, ok = QInputDialog.getDouble(self, "Process Payment", "Enter payment amount (JOD):", 0.00, 0.01, 10000.00, 2)
        
        if ok and amount > 0:
            try:
                conn = sqlite3.connect('store_database.db')
                cursor = conn.cursor()
                cursor.execute("UPDATE customers SET total_debt = total_debt - ? WHERE id = ?", (amount, self.selected_customer_id))
                cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
                user_id = cursor.fetchone()[0]
                cursor.execute("INSERT INTO debt_payments (customer_id, user_id, amount) VALUES (?, ?, ?)", 
                               (self.selected_customer_id, user_id, amount))
                conn.commit()
                conn.close()

                self.show_popup("Payment Successful", f"Successfully recorded a payment of {amount:.2f} JOD.")
                self.selected_customer_id = None
                self.debt_target_label.setText("Select a customer from the list...")
                self.debt_history_table.setRowCount(0)
                self.pay_debt_btn.setEnabled(False)
                self.load_debt_customers()
            except Exception as e:
                self.show_popup("Database Error", f"Failed to process payment: {e}", True)

    # --- STORAGE LOGIC ---
    def load_inventory(self):
        if not self.current_storage_category:
            return 
            
        self.inventory_table.setRowCount(0)
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, barcode, name, quantity_in_stock, cost_price, sell_price FROM products WHERE category = ?", 
                           (self.current_storage_category,))
            rows = cursor.fetchall()
            conn.close()
            
            for row_data in rows:
                row_pos = self.inventory_table.rowCount()
                self.inventory_table.insertRow(row_pos)
                for col_idx, data in enumerate(row_data):
                    if col_idx in [4, 5]:
                        item = QTableWidgetItem(f"{data:.2f}")
                    else:
                        val = data if data is not None else ""
                        item = QTableWidgetItem(str(val))
                    self.inventory_table.setItem(row_pos, col_idx, item)
        except Exception as e:
            pass

    def save_new_product(self):
        category = self.prod_category.currentText()
        barcode = self.prod_barcode.text().strip() or None
        name = self.prod_name.text().strip()
        qty_text = self.prod_qty.text().strip()
        cost_text = self.prod_cost.text().strip()
        sell_text = self.prod_sell.text().strip()
        
        if not name or not qty_text or not cost_text or not sell_text:
            self.show_popup("Error", "Please fill in all required fields.", True)
            return
            
        try:
            qty = int(qty_text)
            cost = float(cost_text)
            sell = float(sell_text)
        except ValueError:
            self.show_popup("Error", "Quantity must be a whole number.\nPrices must be standard numbers (e.g., 2.50).", True)
            return
            
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute('''INSERT INTO products (barcode, name, quantity_in_stock, cost_price, sell_price, category)
                              VALUES (?, ?, ?, ?, ?, ?)''', (barcode, name, qty, cost, sell, category))
            conn.commit()
            conn.close()
            
            self.show_popup("Success", f"Product '{name}' added to {category}!")
            self.prod_barcode.clear(); self.prod_name.clear(); self.prod_qty.clear(); self.prod_cost.clear(); self.prod_sell.clear()
            
            if self.storage_stack.currentIndex() == 1 and self.current_storage_category == category:
                self.load_inventory()
        except Exception as e:
            self.show_popup("Database Error", f"Failed to add product: {e}", True)

    # --- CASH REGISTER LOGIC ---
    def add_item_to_cart(self):
        search_term = self.search_input.text().strip()
        qty_text = self.qty_input.text().strip()
        
        if not search_term: return
            
        try:
            qty = int(qty_text) if qty_text else 1
            if qty <= 0: raise ValueError
        except ValueError:
            self.show_popup("Error", "Quantity must be a valid positive number.", True)
            return
            
        conn = sqlite3.connect('store_database.db')
        cursor = conn.cursor()
        cursor.execute("SELECT id, name, sell_price, quantity_in_stock FROM products WHERE name = ? OR barcode = ?", (search_term, search_term))
        product = cursor.fetchone()
        conn.close()
        
        if product:
            prod_id, name, price, stock = product
            if qty > stock:
                self.show_popup("Stock Warning", f"You only have {stock} of '{name}' left in stock!", True)
                return
                
            subtotal = price * qty
            self.cart_data.append({'id': prod_id, 'name': name, 'qty': qty, 'price': price, 'subtotal': subtotal})
            
            row_pos = self.cart_table.rowCount()
            self.cart_table.insertRow(row_pos)
            self.cart_table.setItem(row_pos, 0, QTableWidgetItem(name))
            self.cart_table.setItem(row_pos, 1, QTableWidgetItem(str(qty)))
            self.cart_table.setItem(row_pos, 2, QTableWidgetItem(f"{price:.2f}"))
            self.cart_table.setItem(row_pos, 3, QTableWidgetItem(f"{subtotal:.2f}"))
            
            self.update_total()
            self.search_input.clear()
            self.qty_input.clear()
            self.search_input.setFocus() 
        else:
            self.show_popup("Not Found", f"No product found matching '{search_term}'.", True)

    def update_total(self):
        self.cart_total = sum(item['subtotal'] for item in self.cart_data)
        self.total_label.setText(f"Total: {self.cart_total:.2f} JOD")

    def complete_cash_sale(self):
        if not self.cart_data: return

        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO sales (total_amount, user_id) VALUES (?, ?)", (self.cart_total, user_id))
            sale_id = cursor.lastrowid 

            for item in self.cart_data:
                cursor.execute("INSERT INTO sale_items (sale_id, product_id, quantity_sold, price_at_time_of_sale) VALUES (?, ?, ?, ?)", 
                               (sale_id, item['id'], item['qty'], item['price']))
                cursor.execute("UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE id = ?", (item['qty'], item['id']))

            conn.commit()
            conn.close()

            self.cart_table.setRowCount(0)
            self.cart_data.clear()
            self.update_total()
            
            if self.storage_stack.currentIndex() == 1:
                self.load_inventory() 
                
            self.show_popup("Sale Complete", f"Success! Sale #{sale_id} logged.\nStock securely updated.")

        except Exception as e:
            pass

    def complete_debt_sale(self):
        if not self.cart_data:
            self.show_popup("Empty Cart", "There are no items in the cart to sell.", True)
            return

        dialog = CustomerDialog(self)
        if dialog.exec():
            is_new = dialog.is_new_customer
            customer_name = dialog.selected_customer_name
            customer_id = dialog.selected_customer_id

            try:
                conn = sqlite3.connect('store_database.db')
                cursor = conn.cursor()

                if is_new:
                    phone = dialog.new_phone
                    cursor.execute("INSERT INTO customers (name, phone_number, total_debt) VALUES (?, ?, ?)", 
                                   (customer_name, phone, self.cart_total))
                    customer_id = cursor.lastrowid 
                else:
                    cursor.execute("UPDATE customers SET total_debt = total_debt + ? WHERE id = ?", (self.cart_total, customer_id))

                cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
                user_id = cursor.fetchone()[0]

                cursor.execute("INSERT INTO sales (total_amount, user_id, customer_id) VALUES (?, ?, ?)", 
                               (self.cart_total, user_id, customer_id))
                sale_id = cursor.lastrowid 

                for item in self.cart_data:
                    cursor.execute("INSERT INTO sale_items (sale_id, product_id, quantity_sold, price_at_time_of_sale) VALUES (?, ?, ?, ?)", 
                                   (sale_id, item['id'], item['qty'], item['price']))
                    cursor.execute("UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE id = ?", (item['qty'], item['id']))

                conn.commit()
                conn.close()

                self.cart_table.setRowCount(0)
                self.cart_data.clear()
                self.update_total()
                self.load_debt_customers() 
                
                if self.storage_stack.currentIndex() == 1:
                    self.load_inventory()
                
                self.show_popup("Debt Logged", f"Success! {self.cart_total:.2f} JOD added to {customer_name}'s tab.")

            except Exception as e:
                self.show_popup("Database Error", f"Something went wrong: {e}", True)

    def show_popup(self, title, message, is_error=False):
        msg = QMessageBox(self)
        msg.setWindowTitle(title)
        msg.setText(message)
        msg.setStyleSheet("""
            QMessageBox { background-color: #2b2b2b; color: white; font-family: 'Segoe UI', sans-serif;}
            QLabel { color: white; min-width: 200px; font-size: 14px; }
            QPushButton { background-color: #9b59b6; color: white; border-radius: 4px; padding: 5px 15px; }
        """)
        if is_error: msg.setIcon(QMessageBox.Icon.Warning)
        else: msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()