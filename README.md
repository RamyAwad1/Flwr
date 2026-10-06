# Flwr - Point of Sale System

A sleek, offline-first Point of Sale and Inventory Management desktop application tailored for retail stores. Built with Python, PyQt6, and SQLite.

## Features
- **Role-Based Access:** Distinct interfaces for Admins and Workers.
- **Modern Cash Register:** Real-time cart calculation and stock validation.
- **Storage Management:** Add, update, and track inventory seamlessly.
- **Customer Debt Tracking:** Tie specific transactions to customer accounts.
- **Offline First:** All data is securely stored locally via SQLite.
- **Bilingual Interface:** Supports English and Arabic (RTL layout) toggling.

## Tech Stack
- **Language:** Python 3.x
- **GUI Framework:** PyQt6
- **Database:** SQLite3

## Installation
1. Clone the repository.
2. Install the required dependencies: `pip install PyQt6`
3. Run the database setup script to initialize your local storage: `python database_setup.py`
4. Create an initial admin user: `python create_admin.py`
5. Launch the application: `python main.py`
