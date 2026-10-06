import sqlite3
from datetime import datetime
from PyQt6.QtWidgets import (QMainWindow, QLabel, QTableWidgetItem, 
                             QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, 
                             QWidget, QMessageBox, QTabWidget, QTableWidget, 
                             QHeaderView, QInputDialog, QFrame, QAbstractItemView)
from PyQt6.QtCore import Qt

class MainWindow(QMainWindow):
    def __init__(self, username, role):
        super().__init__()
        self.username = username
        self.role = role
        
        self.cart_data = [] 
        self.cart_total = 0.0
        self.selected_customer_id = None
        
        self.setWindowTitle(f"flwr - {self.role} Panel")
        self.setGeometry(100, 100, 1200, 800) 
        
        # FIXED STYLESHEET: Adjusted Header min-height and padding to stop text clipping
        self.setStyleSheet("""
            QMainWindow { background-color: #1a1a1a; font-family: 'Segoe UI', Arial, sans-serif; }
            QTabWidget::pane { border: none; background: #1a1a1a; }
            QTabBar::tab { background: #2b2b2b; color: #aaaaaa; padding: 12px 25px; font-size: 15px; border-top-left-radius: 8px; border-top-right-radius: 8px; margin-right: 2px; }
            QTabBar::tab:selected { background: #9b59b6; color: white; font-weight: bold; }
            QTabBar::tab:hover:!selected { background: #3a3a3a; color: white; }
            QLabel { color: #ffffff; }
            QLineEdit { background-color: #2b2b2b; color: white; border: 1px solid #444; border-radius: 6px; padding: 10px; font-size: 14px; }
            QLineEdit:focus { border: 1px solid #9b59b6; background-color: #333; }
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
            
            /* The fix for the chopped off header text */
            QHeaderView::section { background-color: #9b59b6; color: white; padding: 5px; border: none; font-weight: bold; font-size: 14px; min-height: 35px; }
        """)

        self.tabs = QTabWidget()
        self.setCentralWidget(self.tabs)

        if self.role == "Admin":
            self.setup_admin_tabs()
        else:
            self.setup_user_tabs()

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
        self.cart_table.verticalHeader().setVisible(False) # Kills the white bar
        
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
        
        self.inventory_table = QTableWidget(0, 6)
        self.inventory_table.setHorizontalHeaderLabels(["ID", "Barcode", "Name", "Stock", "Cost (JOD)", "Sell (JOD)"])
        self.inventory_table.setAlternatingRowColors(True)
        self.inventory_table.setShowGrid(False)
        self.inventory_table.verticalHeader().setVisible(False) # Kills the white bar
        
        header = self.inventory_table.horizontalHeader()
        header.setSectionResizeMode(2, QHeaderView.ResizeMode.Stretch) 
        main_layout.addWidget(self.inventory_table, 2)
        
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: #222222; border-radius: 12px; padding: 10px; }")
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)
        
        title_label = QLabel("Add New Product")
        title_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #9b59b6; border: none;")
        right_panel.addWidget(title_label)
        
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
        
        self.refresh_btn = QPushButton("Refresh Inventory")
        self.refresh_btn.setObjectName("secondaryBtn")
        self.refresh_btn.clicked.connect(self.load_inventory)
        right_panel.addWidget(self.refresh_btn)
        
        right_frame.setLayout(right_panel)
        main_layout.addWidget(right_frame, 1)
        
        self.tab_storage.setLayout(main_layout)
        self.load_inventory()

    def build_debt_viewer(self):
        self.tab_debt = QWidget()
        main_layout = QHBoxLayout()
        main_layout.setContentsMargins(20, 20, 20, 20)
        main_layout.setSpacing(20)

        # --- LEFT SIDE: Master Customer Table ---
        self.debt_customers_table = QTableWidget(0, 4)
        self.debt_customers_table.setHorizontalHeaderLabels(["ID", "Name", "Phone", "Total Debt (JOD)"])
        self.debt_customers_table.setAlternatingRowColors(True)
        self.debt_customers_table.setShowGrid(False)
        self.debt_customers_table.verticalHeader().setVisible(False) # Kills the white bar!
        
        self.debt_customers_table.setSelectionBehavior(QAbstractItemView.SelectionBehavior.SelectRows)
        self.debt_customers_table.setSelectionMode(QAbstractItemView.SelectionMode.SingleSelection)
        self.debt_customers_table.setColumnHidden(0, True) 

        header = self.debt_customers_table.horizontalHeader()
        header.setSectionResizeMode(1, QHeaderView.ResizeMode.Stretch) 
        # Force the last column to fit perfectly so words aren't eaten
        header.setSectionResizeMode(3, QHeaderView.ResizeMode.ResizeToContents) 
        main_layout.addWidget(self.debt_customers_table, 1)

        self.debt_customers_table.itemSelectionChanged.connect(self.on_customer_selected)

        # --- RIGHT SIDE: Transaction History & Payment ---
        right_frame = QFrame()
        right_frame.setStyleSheet("QFrame { background-color: #222222; border-radius: 12px; padding: 10px; }")
        right_panel = QVBoxLayout()
        right_panel.setSpacing(15)

        self.debt_target_label = QLabel("Select a customer from the list...")
        self.debt_target_label.setStyleSheet("font-size: 20px; font-weight: bold; color: #9b59b6; border: none;")
        right_panel.addWidget(self.debt_target_label)

        self.debt_history_table = QTableWidget(0, 3)
        self.debt_history_table.setHorizontalHeaderLabels(["Date & Time", "Cashier", "Amount (JOD)"])
        self.debt_history_table.setAlternatingRowColors(True)
        self.debt_history_table.setShowGrid(False)
        self.debt_history_table.verticalHeader().setVisible(False) # Kills the white bar!

        h_header = self.debt_history_table.horizontalHeader()
        h_header.setSectionResizeMode(0, QHeaderView.ResizeMode.Stretch) 
        # Ensure the amount column doesn't get chopped
        h_header.setSectionResizeMode(2, QHeaderView.ResizeMode.ResizeToContents) 
        right_panel.addWidget(self.debt_history_table)

        self.pay_debt_btn = QPushButton("Make Payment")
        self.pay_debt_btn.setObjectName("checkoutBtn") 
        self.pay_debt_btn.setEnabled(False) 
        self.pay_debt_btn.clicked.connect(self.make_debt_payment)
        right_panel.addWidget(self.pay_debt_btn)

        right_frame.setLayout(right_panel)
        main_layout.addWidget(right_frame, 2) 

        self.tab_debt.setLayout(main_layout)
        self.load_debt_customers()

    # --- NEW DEBT VIEWER LOGIC FUNCTIONS ---

    def load_debt_customers(self):
        self.debt_customers_table.setRowCount(0)
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, name, phone_number, total_debt FROM customers WHERE total_debt > 0")
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
            self.show_popup("Database Error", f"Failed to load customers: {e}", True)

    def on_customer_selected(self):
        selected_rows = self.debt_customers_table.selectedItems()
        if not selected_rows:
            return
            
        row = selected_rows[0].row()
        self.selected_customer_id = self.debt_customers_table.item(row, 0).text()
        customer_name = self.debt_customers_table.item(row, 1).text()
        total_owed = self.debt_customers_table.item(row, 3).text()

        self.debt_target_label.setText(f"{customer_name}'s History (Owes: {total_owed} JOD)")
        self.pay_debt_btn.setEnabled(True) 
        self.load_customer_history(self.selected_customer_id)

    def load_customer_history(self, customer_id):
        self.debt_history_table.setRowCount(0)
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            
            cursor.execute("""
                SELECT sales.timestamp, users.username, sales.total_amount 
                FROM sales 
                JOIN users ON sales.user_id = users.id 
                WHERE sales.customer_id = ? 
                ORDER BY sales.timestamp DESC
            """, (customer_id,))
            rows = cursor.fetchall()
            conn.close()

            for row_data in rows:
                row_pos = self.debt_history_table.rowCount()
                self.debt_history_table.insertRow(row_pos)
                
                # --- The Date Formatting Fix ---
                raw_timestamp = row_data[0]
                try:
                    # Convert '2026-10-06 11:19:00' into a readable object
                    dt_obj = datetime.strptime(raw_timestamp, "%Y-%m-%d %H:%M:%S")
                    # Format to '06 Oct 2026, 11:19 AM'
                    clean_date = dt_obj.strftime("%d %b %Y, %I:%M %p")
                except ValueError:
                    clean_date = raw_timestamp # Fallback just in case

                self.debt_history_table.setItem(row_pos, 0, QTableWidgetItem(clean_date))
                self.debt_history_table.setItem(row_pos, 1, QTableWidgetItem(str(row_data[1])))
                self.debt_history_table.setItem(row_pos, 2, QTableWidgetItem(f"{row_data[2]:.2f}"))

        except Exception as e:
            self.show_popup("Database Error", f"Failed to load history: {e}", True)

    def make_debt_payment(self):
        if not self.selected_customer_id:
            return
            
        amount, ok = QInputDialog.getDouble(self, "Process Payment", "Enter payment amount (JOD):", 0.00, 0.01, 10000.00, 2)
        
        if ok and amount > 0:
            try:
                conn = sqlite3.connect('store_database.db')
                cursor = conn.cursor()
                
                cursor.execute("""
                    UPDATE customers SET total_debt = total_debt - ? WHERE id = ?
                """, (amount, self.selected_customer_id))
                
                conn.commit()
                conn.close()

                self.show_popup("Payment Successful", f"Successfully deducted {amount:.2f} JOD from the account.")
                
                self.selected_customer_id = None
                self.debt_target_label.setText("Select a customer from the list...")
                self.debt_history_table.setRowCount(0)
                self.pay_debt_btn.setEnabled(False)
                self.load_debt_customers()

            except Exception as e:
                self.show_popup("Database Error", f"Failed to process payment: {e}", True)

    # --- PREVIOUS STORAGE AND CASH REGISTER LOGIC FUNCTIONS BELOW ---

    def load_inventory(self):
        self.inventory_table.setRowCount(0)
        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id, barcode, name, quantity_in_stock, cost_price, sell_price FROM products")
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
            self.show_popup("Database Error", f"Failed to load inventory: {e}", True)

    def save_new_product(self):
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
            cursor.execute('''
                INSERT INTO products (barcode, name, quantity_in_stock, cost_price, sell_price)
                VALUES (?, ?, ?, ?, ?)
            ''', (barcode, name, qty, cost, sell))
            conn.commit()
            conn.close()
            
            self.show_popup("Success", f"Product '{name}' added successfully!")
            self.prod_barcode.clear()
            self.prod_name.clear()
            self.prod_qty.clear()
            self.prod_cost.clear()
            self.prod_sell.clear()
            self.load_inventory()
            
        except Exception as e:
            self.show_popup("Database Error", f"Failed to add product: {e}", True)

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
        if not self.cart_data:
            self.show_popup("Empty Cart", "There are no items in the cart to sell.", True)
            return

        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO sales (total_amount, user_id) VALUES (?, ?)", (self.cart_total, user_id))
            sale_id = cursor.lastrowid 

            for item in self.cart_data:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity_sold, price_at_time_of_sale) 
                    VALUES (?, ?, ?, ?)
                """, (sale_id, item['id'], item['qty'], item['price']))
                cursor.execute("""
                    UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE id = ?
                """, (item['qty'], item['id']))

            conn.commit()
            conn.close()

            self.cart_table.setRowCount(0)
            self.cart_data.clear()
            self.update_total()
            self.load_inventory() 
            self.show_popup("Sale Complete", f"Success! Sale #{sale_id} logged.\nStock has been securely updated.")

        except Exception as e:
            self.show_popup("Database Error", f"Something went wrong: {e}", True)

    def complete_debt_sale(self):
        if not self.cart_data:
            self.show_popup("Empty Cart", "There are no items in the cart to sell.", True)
            return

        customer_name, ok = QInputDialog.getText(self, "Customer Debt", "Enter Customer Name:")
        if not ok or not customer_name.strip(): return
        customer_name = customer_name.strip()

        try:
            conn = sqlite3.connect('store_database.db')
            cursor = conn.cursor()
            cursor.execute("SELECT id FROM customers WHERE name = ?", (customer_name,))
            customer = cursor.fetchone()

            if customer:
                customer_id = customer[0]
                cursor.execute("UPDATE customers SET total_debt = total_debt + ? WHERE id = ?", (self.cart_total, customer_id))
            else:
                cursor.execute("INSERT INTO customers (name, total_debt) VALUES (?, ?)", (customer_name, self.cart_total))
                customer_id = cursor.lastrowid 

            cursor.execute("SELECT id FROM users WHERE username = ?", (self.username,))
            user_id = cursor.fetchone()[0]

            cursor.execute("INSERT INTO sales (total_amount, user_id, customer_id) VALUES (?, ?, ?)", 
                           (self.cart_total, user_id, customer_id))
            sale_id = cursor.lastrowid 

            for item in self.cart_data:
                cursor.execute("""
                    INSERT INTO sale_items (sale_id, product_id, quantity_sold, price_at_time_of_sale) 
                    VALUES (?, ?, ?, ?)
                """, (sale_id, item['id'], item['qty'], item['price']))
                cursor.execute("""
                    UPDATE products SET quantity_in_stock = quantity_in_stock - ? WHERE id = ?
                """, (item['qty'], item['id']))

            conn.commit()
            conn.close()

            self.cart_table.setRowCount(0)
            self.cart_data.clear()
            self.update_total()
            self.load_inventory()
            self.load_debt_customers() 
            
            self.show_popup("Debt Logged", f"Success! {self.cart_total:.2f} JOD has been added to {customer_name}'s tab.")

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
        if is_error:
            msg.setIcon(QMessageBox.Icon.Warning)
        else:
            msg.setIcon(QMessageBox.Icon.Information)
        msg.exec()