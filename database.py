"""
Database management module for Amar Hisab Billing Software.
Handles SQLite operations for clients, daily billing entries, and invoices.
"""

import sqlite3
import os
from typing import Optional, Dict, Any, List, Tuple

DB_NAME = "amar_hisab.db"


def get_db_path() -> str:
    """Returns absolute path to the database file."""
    base_dir = os.path.dirname(os.path.abspath(__file__))
    return os.path.join(base_dir, DB_NAME)


def get_connection():
    """Create and return a database connection."""
    conn = sqlite3.connect(get_db_path())
    conn.execute("PRAGMA foreign_keys = ON;")
    conn.row_factory = sqlite3.Row
    return conn


def init_db():
    """Initialize database tables and run schema migrations if needed."""
    with get_connection() as conn:
        cursor = conn.cursor()

        # 1. Clients Table (Includes due_balance for running ledger)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS clients (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL,
                whatsapp TEXT NOT NULL UNIQUE,
                address TEXT,
                due_balance REAL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                updated_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
            )
        """)

        # Migration: Ensure due_balance exists in clients if table already existed
        try:
            cursor.execute("ALTER TABLE clients ADD COLUMN due_balance REAL DEFAULT 0.0")
        except sqlite3.OperationalError:
            pass

        # 2. Daily Entries Table (Accurate ledger calculation per row)
        # Total Amount = (B&W + Color) * rate
        # Net Amount = Total - deposit
        # New Due = previous_due + net_amount
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS daily_entries (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                client_id INTEGER,
                client_name TEXT,
                whatsapp TEXT,
                entry_date TEXT NOT NULL,
                bw_pages INTEGER DEFAULT 0,
                color_pages INTEGER DEFAULT 0,
                total_pages INTEGER DEFAULT 0,
                rate REAL NOT NULL DEFAULT 0.0,
                total_amount REAL NOT NULL DEFAULT 0.0,
                deposit REAL NOT NULL DEFAULT 0.0,
                net_amount REAL NOT NULL DEFAULT 0.0,
                previous_due REAL NOT NULL DEFAULT 0.0,
                new_due REAL NOT NULL DEFAULT 0.0,
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL
            )
        """)

        # 3. Invoices Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoices (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_no TEXT NOT NULL UNIQUE,
                client_id INTEGER,
                subtotal REAL DEFAULT 0.0,
                discount REAL DEFAULT 0.0,
                net_total REAL DEFAULT 0.0,
                payment_status TEXT DEFAULT 'Paid',
                created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                FOREIGN KEY (client_id) REFERENCES clients (id) ON DELETE SET NULL
            )
        """)

        # 4. Invoice Items Table
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS invoice_items (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                invoice_id INTEGER NOT NULL,
                entry_date TEXT,
                bw_pages INTEGER DEFAULT 0,
                color_pages INTEGER DEFAULT 0,
                total_pages INTEGER DEFAULT 0,
                rate REAL NOT NULL DEFAULT 0.0,
                total_price REAL NOT NULL DEFAULT 0.0,
                deposit REAL NOT NULL DEFAULT 0.0,
                due_amount REAL NOT NULL DEFAULT 0.0,
                FOREIGN KEY (invoice_id) REFERENCES invoices (id) ON DELETE CASCADE
            )
        """)

        conn.commit()


def save_or_update_client(name: str, whatsapp: str, address: str = "") -> Tuple[int, bool]:
    """
    Saves a new client or updates existing client by WhatsApp number.
    Returns (client_id, is_new_client)
    """
    name = name.strip()
    whatsapp = whatsapp.strip()
    address = address.strip()

    if not name or not whatsapp:
        raise ValueError("নাম এবং WhatsApp নম্বর অবশ্যই দিতে হবে।")

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT id FROM clients WHERE whatsapp = ?", (whatsapp,))
        row = cursor.fetchone()

        if row:
            client_id = row["id"]
            cursor.execute("""
                UPDATE clients
                SET name = ?, address = ?, updated_at = CURRENT_TIMESTAMP
                WHERE id = ?
            """, (name, address, client_id))
            conn.commit()
            return client_id, False
        else:
            cursor.execute("""
                INSERT INTO clients (name, whatsapp, address, due_balance)
                VALUES (?, ?, ?, 0.0)
            """, (name, whatsapp, address))
            conn.commit()
            return cursor.lastrowid, True


def find_client_by_whatsapp(whatsapp: str) -> Optional[Dict[str, Any]]:
    """Look up a client by WhatsApp phone number."""
    whatsapp = whatsapp.strip()
    if not whatsapp:
        return None

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE whatsapp = ?", (whatsapp,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_client_by_id(client_id: int) -> Optional[Dict[str, Any]]:
    """Look up a client by ID."""
    if not client_id:
        return None
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        if row:
            return dict(row)
        return None


def get_client_due(client_id: Optional[int]) -> float:
    """
    Finds the client's current accumulated Due Amount from SQLite database.
    Returns 0.0 if client_id is None or client not found.
    """
    if not client_id:
        return 0.0

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT due_balance FROM clients WHERE id = ?", (client_id,))
        row = cursor.fetchone()
        if row and row["due_balance"] is not None:
            return float(row["due_balance"])
        return 0.0


def update_client_due(client_id: int, new_due: float):
    """Update a client's running due balance in SQLite database."""
    if not client_id:
        return

    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            UPDATE clients
            SET due_balance = ?, updated_at = CURRENT_TIMESTAMP
            WHERE id = ?
        """, (float(new_due), client_id))
        conn.commit()


def save_entry_record(client_id: Optional[int], client_name: str, whatsapp: str,
                      entry_date: str, bw_pages: int, color_pages: int,
                      rate: float, deposit: float) -> Dict[str, Any]:
    """
    Calculates and saves an entry record to database:
    1. Total Amount = (B&W + Color) * rate
    2. Net Amount = Total Amount - deposit
    3. Finds previous Due Amount from database for this client
    4. New Due Amount = previous_due + net_amount
    5. Saves entry in database and updates client's due balance.
    """
    # 1. Total Amount = (B&W + Color) * rate
    total_pages = bw_pages + color_pages
    total_amount = (total_pages * rate) if total_pages > 0 else rate

    # 2. Net Amount = Total - deposit
    net_amount = total_amount - deposit

    # 3. Previous Due from database
    previous_due = 0.0
    if client_id:
        previous_due = get_client_due(client_id)

    # 4. New Due Amount = previous_due + net_amount
    new_due = previous_due + net_amount

    # 5. Update client due in database
    if client_id:
        update_client_due(client_id, new_due)

    # 6. Save entry row into daily_entries table
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO daily_entries (
                client_id, client_name, whatsapp, entry_date,
                bw_pages, color_pages, total_pages, rate,
                total_amount, deposit, net_amount,
                previous_due, new_due
            )
            VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        """, (
            client_id, client_name, whatsapp, entry_date,
            bw_pages, color_pages, total_pages, rate,
            total_amount, deposit, net_amount,
            previous_due, new_due
        ))
        entry_id = cursor.lastrowid
        conn.commit()

    return {
        "id": entry_id,
        "client_id": client_id,
        "client_name": client_name,
        "whatsapp": whatsapp,
        "entry_date": entry_date,
        "bw_pages": bw_pages,
        "color_pages": color_pages,
        "total_pages": total_pages,
        "rate": rate,
        "total_amount": total_amount,
        "total_price": total_amount,
        "deposit": deposit,
        "net_amount": net_amount,
        "previous_due": previous_due,
        "new_due": new_due,
        "due_amount": new_due
    }


def get_client_entries(client_id: int) -> List[Dict[str, Any]]:
    """Retrieve all entries for a specific client."""
    if not client_id:
        return []
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM daily_entries WHERE client_id = ? ORDER BY id DESC", (client_id,))
        return [dict(row) for row in cursor.fetchall()]


def get_all_clients() -> List[Dict[str, Any]]:
    """Retrieve all clients ordered by recent updates."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM clients ORDER BY id DESC")
        return [dict(row) for row in cursor.fetchall()]


def save_invoice(invoice_no: str, client_id: Optional[int], subtotal: float,
                 discount: float, net_total: float, items: List[Dict[str, Any]],
                 payment_status: str = "Paid") -> int:
    """Save complete invoice along with line items."""
    with get_connection() as conn:
        cursor = conn.cursor()
        cursor.execute("""
            INSERT INTO invoices (invoice_no, client_id, subtotal, discount, net_total, payment_status)
            VALUES (?, ?, ?, ?, ?, ?)
        """, (invoice_no, client_id, subtotal, discount, net_total, payment_status))
        invoice_id = cursor.lastrowid

        for item in items:
            cursor.execute("""
                INSERT INTO invoice_items (
                    invoice_id, entry_date, bw_pages, color_pages, total_pages,
                    rate, total_price, deposit, due_amount
                )
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
            """, (
                invoice_id,
                item.get("entry_date", ""),
                int(item.get("bw_pages", 0)),
                int(item.get("color_pages", 0)),
                int(item.get("total_pages", 0)),
                float(item.get("rate", 0.0)),
                float(item.get("total_amount", item.get("total_price", 0.0))),
                float(item.get("deposit", 0.0)),
                float(item.get("new_due", item.get("due_amount", 0.0)))
            ))

        conn.commit()
        return invoice_id
