"""
Amar Hisab - Professional Billing & Ledger Desktop Application
Built with Python Tkinter and SQLite

Features:
- Premium, Corporate Desktop UI/UX with Clean Slate Color Palette
- Strict Mathematical Engine:
    Total Amount = (B&W + Color) * Rate  (0 if Total Pages == 0)
    Net Amount   = Total Amount - Deposit
    New Due      = Previous Due + Net Amount
- SQLite Relational Ledger Persistence
- 100% Mouse-Free Keyboard Data Entry Flow
- Client Browser modal with instant Single-Click selection & ledger history loading
- Invoicing Engine: Printable HTML Bill, Professional PDF Bill (ReportLab), and WhatsApp Full Bill
- Rich High-Contrast Row Color Tags (Red for Due added, Green for Deposit, Slate for Zero)
- In-App Refresh Button (F5) & One-Click Desktop Shortcut Generator
"""

import sys
import os
import datetime
import subprocess
import webbrowser
import tkinter as tk
from tkinter import ttk, messagebox, filedialog

# Ensure UTF-8 output in Windows console if needed
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import database
import whatsapp_sender
import bill_generator


def create_desktop_shortcut() -> bool:
    """Create a Windows desktop shortcut for Amar Hisab pointing to Amar_Hisab.bat."""
    try:
        current_dir = os.path.dirname(os.path.abspath(__file__))
        bat_path = os.path.join(current_dir, "Amar_Hisab.bat")
        desktop_dir = os.path.join(os.environ.get("USERPROFILE", ""), "Desktop")
        if not os.path.exists(desktop_dir):
            return False

        shortcut_path = os.path.join(desktop_dir, "Amar Hisab.lnk")
        ps_script = (
            f'$ws = New-Object -ComObject WScript.Shell; '
            f'$s = $ws.CreateShortcut("{shortcut_path}"); '
            f'$s.TargetPath = "{bat_path}"; '
            f'$s.WorkingDirectory = "{current_dir}"; '
            f'$s.Description = "আমার হিসাব (Amar Hisab) - বিলিং সফটওয়্যার"; '
            f'$s.Save()'
        )
        subprocess.run(["powershell", "-NoProfile", "-Command", ps_script], check=True, capture_output=True)
        return True
    except Exception as e:
        print(f"Error creating shortcut: {e}")
        return False


class BillingApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("আমার হিসাব (Amar Hisab) - প্রফেশনাল বিলিং ও লেজার সফটওয়্যার")
        self.root.geometry("1140x800")
        self.root.minsize(980, 680)

        # Initialize Database
        database.init_db()

        # Application State
        self.items_list = []
        self.current_client_id = None
        self.current_client_name = ""
        self.current_client_whatsapp = ""
        self.current_client_address = ""
        self.current_client_previous_due = 0.0
        self.invoice_number = self.generate_invoice_no()

        # Setup Modern Theme & Styles
        self.setup_styles()

        # Build UI Sections
        self.create_header()
        self.create_main_container()
        self.create_top_client_section()
        self.create_middle_entry_section()
        self.create_bottom_table_section()
        self.create_status_bar()

        # Configure Flawless Keyboard Navigation
        self.setup_keyboard_navigation()

        # Initial Focus on Client Name for immediate mouse-free typing
        self.root.after(100, lambda: self.set_focus_and_select(self.entry_client_name))

    def generate_invoice_no(self) -> str:
        """Generate unique invoice number based on timestamp."""
        now = datetime.datetime.now()
        return f"INV-{now.strftime('%Y%m%d-%H%M%S')}"

    # ==============================================================
    # কর্পোরেট প্রফেশনাল থিম ও স্টাইলিং (Modern Corporate Design)
    # ==============================================================
    def setup_styles(self):
        """Configure modern, corporate styles for ttk widgets."""
        self.root.configure(bg="#f8fafc")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color Tokens
        self.COLOR_BG = "#f8fafc"            # Soft Slate-50 background
        self.COLOR_CARD = "#ffffff"          # Crisp White
        self.COLOR_BORDER = "#cbd5e1"        # Subtle Border
        self.COLOR_TEXT_MAIN = "#0f172a"     # Dark Slate-900
        self.COLOR_TEXT_MUTED = "#64748b"    # Slate-500
        self.COLOR_PRIMARY = "#2563eb"       # Royal Blue-600
        self.COLOR_PRIMARY_HOVER = "#1d4ed8" # Blue-700
        self.COLOR_SUCCESS = "#059669"       # Emerald-600
        self.COLOR_SUCCESS_HOVER = "#10b981" # Emerald-500
        self.COLOR_WHATSAPP = "#16a34a"      # WhatsApp Green
        self.COLOR_WHATSAPP_HOVER = "#22c55e"# Green-500
        self.COLOR_DANGER = "#dc2626"        # Crimson Red
        self.COLOR_DANGER_HOVER = "#ef4444"  # Red-500
        self.COLOR_SECONDARY = "#475569"     # Slate-600
        self.COLOR_SECONDARY_HOVER = "#64748b"
        self.COLOR_PURPLE = "#7c3aed"        # Modern Violet
        self.COLOR_PURPLE_HOVER = "#6d28d9"

        # Frame & LabelFrame Styles
        self.style.configure("Card.TLabelframe",
                             background=self.COLOR_CARD,
                             foreground=self.COLOR_PRIMARY,
                             font=("Segoe UI", 10, "bold"),
                             borderwidth=1,
                             relief="solid")
        self.style.configure("Card.TLabelframe.Label",
                             background=self.COLOR_CARD,
                             foreground="#1e3a8a",
                             font=("Segoe UI", 10, "bold"))

        # Field Labels
        self.style.configure("FieldLabel.TLabel",
                             background=self.COLOR_CARD,
                             foreground=self.COLOR_TEXT_MAIN,
                             font=("Segoe UI", 9, "bold"))

        # Primary Button (Royal Blue)
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_PRIMARY,
            foreground="#ffffff",
            padding=5,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("Primary.TButton",
                       background=[("active", self.COLOR_PRIMARY_HOVER), ("pressed", "#1e40af")])

        # Success Button (Emerald Green)
        self.style.configure(
            "Success.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_SUCCESS,
            foreground="#ffffff",
            padding=5,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("Success.TButton",
                       background=[("active", self.COLOR_SUCCESS_HOVER), ("pressed", "#047857")])

        # WhatsApp Button (WhatsApp Green)
        self.style.configure(
            "WhatsApp.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_WHATSAPP,
            foreground="#ffffff",
            padding=5,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("WhatsApp.TButton",
                       background=[("active", self.COLOR_WHATSAPP_HOVER), ("pressed", "#15803d")])

        # Purple / Invoicing Button
        self.style.configure(
            "Purple.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_PURPLE,
            foreground="#ffffff",
            padding=5,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("Purple.TButton",
                       background=[("active", self.COLOR_PURPLE_HOVER), ("pressed", "#5b21b6")])

        # Danger Button (Crimson Red)
        self.style.configure(
            "Danger.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_DANGER,
            foreground="#ffffff",
            padding=5,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("Danger.TButton",
                       background=[("active", self.COLOR_DANGER_HOVER), ("pressed", "#b91c1c")])

        # Secondary Button (Slate)
        self.style.configure(
            "Secondary.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_SECONDARY,
            foreground="#ffffff",
            padding=5,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("Secondary.TButton",
                       background=[("active", self.COLOR_SECONDARY_HOVER), ("pressed", "#334155")])

        # Treeview (Table) Styling
        self.style.configure(
            "Custom.Treeview",
            background="#ffffff",
            foreground="#0f172a",
            fieldbackground="#ffffff",
            rowheight=28,
            font=("Segoe UI", 9),
            borderwidth=1
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#1e293b",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            padding=5,
            relief="flat"
        )
        self.style.map("Custom.Treeview.Heading",
                       background=[("active", "#334155")])
        self.style.map("Custom.Treeview",
                       background=[("selected", "#bfdbfe")],
                       foreground=[("selected", "#1e3a8a")])

    def create_header(self):
        """Top Brand Header with corporate gradient look & invoice pill."""
        header_frame = tk.Frame(self.root, bg="#0f172a", height=60)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        # Bottom accent line (modern Blue border)
        accent_line = tk.Frame(header_frame, bg="#3b82f6", height=2)
        accent_line.pack(side=tk.BOTTOM, fill=tk.X)

        # Left Title Box
        title_box = tk.Frame(header_frame, bg="#0f172a")
        title_box.pack(side=tk.LEFT, padx=16, pady=8)

        main_title = tk.Label(
            title_box,
            text="⚡ আমার হিসাব (Amar Hisab)",
            font=("Segoe UI", 15, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        )
        main_title.pack(anchor="w")

        subtitle = tk.Label(
            title_box,
            text="প্রফেশনাল ডিজিটাল বিলিং ও লেজার | Total = (B&W + Color) × দর | Net = Total - জমা",
            font=("Segoe UI", 8),
            fg="#94a3b8",
            bg="#0f172a"
        )
        subtitle.pack(anchor="w")

        # Right Info Box (Pill card)
        inv_box = tk.Frame(header_frame, bg="#1e293b", padx=12, pady=4, bd=1, relief="flat")
        inv_box.pack(side=tk.RIGHT, padx=16, pady=8)

        self.inv_lbl = tk.Label(
            inv_box,
            text=f"ইনভয়েস: {self.invoice_number}",
            font=("Segoe UI", 9, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        self.inv_lbl.pack(anchor="e")

        today_str = datetime.date.today().strftime("%d-%m-%Y")
        date_lbl = tk.Label(
            inv_box,
            text=f"তারিখ: {today_str} | [F5 রিফ্রেশ]",
            font=("Segoe UI", 8),
            fg="#cbd5e1",
            bg="#1e293b"
        )
        date_lbl.pack(anchor="e")

    def create_main_container(self):
        """Main Content Area containing all 3 core sections."""
        self.main_container = tk.Frame(self.root, bg="#f8fafc")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=12, pady=6)

    # ==============================================================
    # ১. শীর্ষ অংশ: ক্লায়েন্ট তথ্য ও WhatsApp বকেয়া যোগাযোগ
    # ==============================================================
    def create_top_client_section(self):
        """
        Top Section: 2-Row Compact Grid to eliminate screen overflow.
        Row 0: Name, WhatsApp, Search, Address, Save Client, In-App Refresh (F5)
        Row 1: All Clients (Modal), Previous Due Badge, WhatsApp Reminder, Status Badge, Desktop Shortcut
        """
        client_frame = ttk.LabelFrame(
            self.main_container,
            text="👤 ১. ক্লায়েন্টের তথ্য ও যোগাযোগ (Client Details & Actions)",
            style="Card.TLabelframe"
        )
        client_frame.pack(fill=tk.X, pady=(0, 6))

        inner = tk.Frame(client_frame, bg=self.COLOR_CARD)
        inner.pack(fill=tk.X, padx=8, pady=4)

        # ── ROW 0: Inputs & Primary Action Buttons ────────────────
        row0 = tk.Frame(inner, bg=self.COLOR_CARD)
        row0.pack(fill=tk.X, pady=2)

        # Client Name
        ttk.Label(row0, text="গ্রাহকের নাম: *", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_client_name = ttk.Entry(row0, width=17, font=("Segoe UI", 9))
        self.entry_client_name.pack(side=tk.LEFT, padx=(0, 8))

        # WhatsApp Number
        ttk.Label(row0, text="WhatsApp নম্বর: *", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_client_whatsapp = ttk.Entry(row0, width=14, font=("Segoe UI", 9))
        self.entry_client_whatsapp.pack(side=tk.LEFT, padx=(0, 4))

        # Search / Autofill
        btn_search = ttk.Button(
            row0,
            text="🔍 খুঁজুন",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.search_or_autofill_client
        )
        btn_search.pack(side=tk.LEFT, padx=(0, 8))

        # Client Address
        ttk.Label(row0, text="ঠিকানা:", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_client_address = ttk.Entry(row0, width=15, font=("Segoe UI", 9))
        self.entry_client_address.pack(side=tk.LEFT, padx=(0, 8))

        # Save Client Button
        btn_save_client = ttk.Button(
            row0,
            text="💾 ক্লায়েন্ট সেভ",
            style="Success.TButton",
            cursor="hand2",
            command=self.save_client_action
        )
        btn_save_client.pack(side=tk.LEFT, padx=(0, 6))

        # IN-APP REFRESH BUTTON (Requirement 6)
        btn_refresh = ttk.Button(
            row0,
            text="🔄 রিফ্রেশ (F5)",
            style="Primary.TButton",
            cursor="hand2",
            command=self.refresh_all_action
        )
        btn_refresh.pack(side=tk.LEFT, padx=(0, 4))

        # ── ROW 1: Client Browser, Due Badge, WhatsApp, Desktop Shortcut ────
        row1 = tk.Frame(inner, bg=self.COLOR_CARD)
        row1.pack(fill=tk.X, pady=(4, 2))

        # ALL CLIENTS MODAL BUTTON (Requirement 2)
        btn_all_clients = ttk.Button(
            row1,
            text="👥 সব ক্লায়েন্ট তালিকা",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.open_client_browser
        )
        btn_all_clients.pack(side=tk.LEFT, padx=(0, 8))

        # Previous Due Badge
        due_badge_frame = tk.Frame(row1, bg="#fee2e2", padx=8, pady=2, bd=1, relief="solid")
        due_badge_frame.pack(side=tk.LEFT, padx=(0, 8))

        tk.Label(
            due_badge_frame,
            text="আগের বাকি (Due):",
            font=("Segoe UI", 9, "bold"),
            bg="#fee2e2",
            fg="#991b1b"
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.lbl_client_previous_due = tk.Label(
            due_badge_frame,
            text="৳ 0.00",
            font=("Segoe UI", 10, "bold"),
            bg="#fee2e2",
            fg="#dc2626"
        )
        self.lbl_client_previous_due.pack(side=tk.LEFT)

        # WhatsApp Reminder Button
        self.btn_whatsapp_top = ttk.Button(
            row1,
            text="💬 WhatsApp-এ বকেয়া পাঠান",
            style="WhatsApp.TButton",
            cursor="hand2",
            command=self.send_whatsapp_reminder
        )
        self.btn_whatsapp_top.pack(side=tk.LEFT, padx=(0, 8))

        # Client Status Badge
        self.lbl_client_status = tk.Label(
            row1,
            text="নতুন ক্লায়েন্ট",
            font=("Segoe UI", 9, "bold"),
            fg="#475569",
            bg="#f1f5f9",
            padx=8,
            pady=3,
            relief="solid",
            bd=1
        )
        self.lbl_client_status.pack(side=tk.LEFT, padx=(0, 8))

        # DESKTOP SHORTCUT BUTTON (Requirement 5)
        btn_shortcut = ttk.Button(
            row1,
            text="🖥️ ডেস্কটপে শর্টকাট",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.create_desktop_shortcut_action
        )
        btn_shortcut.pack(side=tk.RIGHT, padx=4)

    # ==============================================================
    # ২. মাঝের অংশ: ডেটা এন্ট্রি ফর্ম ও নিখুঁত হিসাব
    # ==============================================================
    def create_middle_entry_section(self):
        """
        Middle Section: Compact 2-Row Layout.
        Row 0: 5 Entry fields (তারিখ, B&W, Color, দর, জমা)
        Row 1: Live Calculations (Total, Net, New Due) + Save (Enter) + Reset (Esc)
        """
        entry_frame = ttk.LabelFrame(
            self.main_container,
            text="📝 ২. ডেটা এন্ট্রি ফর্ম [Total = (B&W + Color) × দর | Net = Total - জমা | New Due = আগের বাকি + Net]",
            style="Card.TLabelframe"
        )
        entry_frame.pack(fill=tk.X, pady=(0, 6))

        inner = tk.Frame(entry_frame, bg=self.COLOR_CARD)
        inner.pack(fill=tk.X, padx=8, pady=4)

        # ── ROW 0: The 5 Input Fields ─────────────────────────────
        row0 = tk.Frame(inner, bg=self.COLOR_CARD)
        row0.pack(fill=tk.X, pady=2)

        # Field 1: ১. তারিখ (Date)
        ttk.Label(row0, text="১. তারিখ:", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_date = ttk.Entry(row0, width=11, font=("Segoe UI", 9, "bold"))
        self.entry_date.pack(side=tk.LEFT, padx=(0, 10))
        today_default = datetime.date.today().strftime("%d-%m-%Y")
        self.entry_date.insert(0, today_default)

        # Field 2: ২. B&W পেজ (B&W Pages)
        ttk.Label(row0, text="২. B&W পেজ:", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_bw_pages = ttk.Entry(row0, width=8, font=("Segoe UI", 9, "bold"))
        self.entry_bw_pages.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_bw_pages.insert(0, "0")
        self.entry_bw_pages.bind("<KeyRelease>", self.update_live_calculations)

        # Field 3: ৩. Color পেজ (Color Pages)
        ttk.Label(row0, text="৩. Color পেজ:", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_color_pages = ttk.Entry(row0, width=8, font=("Segoe UI", 9, "bold"))
        self.entry_color_pages.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_color_pages.insert(0, "0")
        self.entry_color_pages.bind("<KeyRelease>", self.update_live_calculations)

        # Field 4: ৪. দর (Rate)
        ttk.Label(row0, text="৪. দর (৳):", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_rate = ttk.Entry(row0, width=8, font=("Segoe UI", 9, "bold"))
        self.entry_rate.pack(side=tk.LEFT, padx=(0, 10))
        self.entry_rate.insert(0, "2.00")
        self.entry_rate.bind("<KeyRelease>", self.update_live_calculations)

        # Field 5: ৫. জমা (Deposit)
        ttk.Label(row0, text="৫. জমা (৳):", style="FieldLabel.TLabel").pack(side=tk.LEFT, padx=(0, 4))
        self.entry_deposit = ttk.Entry(row0, width=9, font=("Segoe UI", 9, "bold"))
        self.entry_deposit.pack(side=tk.LEFT, padx=(0, 8))
        self.entry_deposit.insert(0, "0")
        self.entry_deposit.bind("<KeyRelease>", self.update_live_calculations)

        # ── ROW 1: Live Calculations Preview & Action Buttons ─────
        row1 = tk.Frame(inner, bg=self.COLOR_CARD)
        row1.pack(fill=tk.X, pady=(4, 2))

        # Live calculation preview badges
        preview_box = tk.Frame(row1, bg="#f8fafc", padx=10, pady=3, bd=1, relief="solid")
        preview_box.pack(side=tk.LEFT, padx=(0, 12))

        # Total Amount Preview
        tk.Label(preview_box, text="Total:", font=("Segoe UI", 8, "bold"), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_preview_total = tk.Label(preview_box, text="৳ 0.00", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#2563eb")
        self.lbl_preview_total.pack(side=tk.LEFT, padx=(0, 10))

        # Net Amount Preview
        tk.Label(preview_box, text="Net:", font=("Segoe UI", 8, "bold"), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_preview_net = tk.Label(preview_box, text="৳ 0.00", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#059669")
        self.lbl_preview_net.pack(side=tk.LEFT, padx=(0, 10))

        # New Due Preview
        tk.Label(preview_box, text="New Due:", font=("Segoe UI", 8, "bold"), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_preview_new_due = tk.Label(preview_box, text="৳ 0.00", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#dc2626")
        self.lbl_preview_new_due.pack(side=tk.LEFT)

        # Save Button (Enter)
        btn_add = ttk.Button(
            row1,
            text="💾 সেভ করুন (Enter)",
            style="Primary.TButton",
            cursor="hand2",
            command=self.save_entry_action
        )
        btn_add.pack(side=tk.LEFT, padx=(0, 8))

        # Reset Form Button (Esc)
        btn_clear_form = ttk.Button(
            row1,
            text="🔄 রিসেট (Esc)",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.clear_entry_form
        )
        btn_clear_form.pack(side=tk.LEFT)

    # ==============================================================
    # ৩. নিচের অংশ: টেবিল (Treeview) ও লেজার হিসাব ও বিল একশন
    # ==============================================================
    def create_bottom_table_section(self):
        """Bottom Section: Treeview table displaying ledger records & totals."""
        table_frame = ttk.LabelFrame(
            self.main_container,
            text="📋 ৩. বিলের আইটেম ও লেজার তালিকা (Ledger Table) - রো সিলেক্ট করে সরাসরি WhatsApp পাঠান",
            style="Card.TLabelframe"
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 4))

        table_container = tk.Frame(table_frame, bg=self.COLOR_CARD)
        table_container.pack(fill=tk.BOTH, expand=True, padx=6, pady=4)

        # Scrollbar and Treeview
        scroll_y = ttk.Scrollbar(table_container, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        columns = ("sl", "date", "bw", "color", "rate", "total_amount", "deposit", "net_amount", "prev_due", "new_due")
        self.tree = ttk.Treeview(
            table_container,
            columns=columns,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scroll_y.set
        )
        scroll_y.config(command=self.tree.yview)

        # Bind row selection to update WhatsApp / client context
        self.tree.bind("<<TreeviewSelect>>", self.on_treeview_row_select)

        # Headings & Column formatting
        self.tree.heading("sl", text="SL", anchor=tk.CENTER)
        self.tree.heading("date", text="তারিখ", anchor=tk.CENTER)
        self.tree.heading("bw", text="B&W পেজ", anchor=tk.CENTER)
        self.tree.heading("color", text="Color পেজ", anchor=tk.CENTER)
        self.tree.heading("rate", text="দর (৳)", anchor=tk.E)
        self.tree.heading("total_amount", text="Total Amount (৳)", anchor=tk.E)
        self.tree.heading("deposit", text="জমা (৳)", anchor=tk.E)
        self.tree.heading("net_amount", text="Net Amount (৳)", anchor=tk.E)
        self.tree.heading("prev_due", text="আগের বাকি (৳)", anchor=tk.E)
        self.tree.heading("new_due", text="নতুন Due (৳)", anchor=tk.E)

        self.tree.column("sl", width=40, anchor=tk.CENTER)
        self.tree.column("date", width=95, anchor=tk.CENTER)
        self.tree.column("bw", width=80, anchor=tk.CENTER)
        self.tree.column("color", width=80, anchor=tk.CENTER)
        self.tree.column("rate", width=75, anchor=tk.E)
        self.tree.column("total_amount", width=115, anchor=tk.E)
        self.tree.column("deposit", width=95, anchor=tk.E)
        self.tree.column("net_amount", width=115, anchor=tk.E)
        self.tree.column("prev_due", width=110, anchor=tk.E)
        self.tree.column("new_due", width=125, anchor=tk.E)

        # HIGH-CONTRAST ROW COLOR TAGS (Requirement 4)
        # 1. due_added (Net Amount > 0: বাকি যোগ হয়েছে) -> Soft Red/Rose background with Bold Dark Red
        self.tree.tag_configure("due_added", background="#fee2e2", foreground="#991b1b")
        # 2. payment_made (Net Amount < 0: জমা বেশি / পেমেন্ট পরিশোধ) -> Soft Mint Green background with Bold Dark Green
        self.tree.tag_configure("payment_made", background="#dcfce7", foreground="#14532d")
        # 3. zero_even / zero_odd (Net Amount == 0) -> Sleek subtle alternating slate
        self.tree.tag_configure("zero_even", background="#ffffff", foreground="#334155")
        self.tree.tag_configure("zero_odd", background="#f1f5f9", foreground="#334155")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # ── BILL ACTIONS & SUMMARY TOOLBAR (Requirement 3 & 4) ─────────
        action_toolbar = tk.Frame(table_frame, bg="#f8fafc", padx=8, pady=5, bd=1, relief="solid")
        action_toolbar.pack(fill=tk.X, padx=6, pady=(3, 3))

        # Left: Bill Generation Action Buttons (PDF, Print, WhatsApp Full, Delete, New Bill)
        left_actions = tk.Frame(action_toolbar, bg="#f8fafc")
        left_actions.pack(side=tk.LEFT)

        # Print / Browser Bill Button
        btn_print = ttk.Button(
            left_actions,
            text="🖨️ প্রিন্ট / ব্রাউজারে বিল",
            style="Purple.TButton",
            cursor="hand2",
            command=self.print_or_view_bill_action
        )
        btn_print.pack(side=tk.LEFT, padx=(0, 6))

        # PDF Bill Export Button
        btn_pdf = ttk.Button(
            left_actions,
            text="📄 পিডিএফ (PDF) বিল",
            style="Primary.TButton",
            cursor="hand2",
            command=self.export_pdf_bill_action
        )
        btn_pdf.pack(side=tk.LEFT, padx=(0, 6))

        # Full WhatsApp Bill Button
        btn_wa_full = ttk.Button(
            left_actions,
            text="📲 WhatsApp-এ পূর্ণ বিল",
            style="WhatsApp.TButton",
            cursor="hand2",
            command=self.send_full_bill_whatsapp_action
        )
        btn_wa_full.pack(side=tk.LEFT, padx=(0, 8))

        # Delete Selected Item
        btn_remove = ttk.Button(
            left_actions,
            text="🗑️ মুছুন (Del)",
            style="Danger.TButton",
            cursor="hand2",
            command=self.delete_selected_item
        )
        btn_remove.pack(side=tk.LEFT, padx=(0, 6))

        # New Bill Button
        btn_reset_bill = ttk.Button(
            left_actions,
            text="📄 নতুন বিল (Ctrl+N)",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.reset_entire_bill
        )
        btn_reset_bill.pack(side=tk.LEFT)

        # Right: Colored Summary Cards & Save Invoice Button
        right_totals = tk.Frame(action_toolbar, bg="#f8fafc")
        right_totals.pack(side=tk.RIGHT)

        # Card 1: Total Bill (Soft Blue)
        card_total = tk.Frame(right_totals, bg="#eff6ff", padx=6, pady=2, bd=1, relief="solid")
        card_total.pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(card_total, text="মোট বিল:", font=("Segoe UI", 8, "bold"), bg="#eff6ff", fg="#1e40af").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_subtotal = tk.Label(card_total, text="৳ 0.00", font=("Segoe UI", 9, "bold"), bg="#eff6ff", fg="#1d4ed8")
        self.lbl_subtotal.pack(side=tk.LEFT)

        # Card 2: Total Deposit (Soft Green)
        card_dep = tk.Frame(right_totals, bg="#f0fdf4", padx=6, pady=2, bd=1, relief="solid")
        card_dep.pack(side=tk.LEFT, padx=(0, 6))
        tk.Label(card_dep, text="মোট জমা:", font=("Segoe UI", 8, "bold"), bg="#f0fdf4", fg="#166534").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_total_deposit_stat = tk.Label(card_dep, text="৳ 0.00", font=("Segoe UI", 9, "bold"), bg="#f0fdf4", fg="#15803d")
        self.lbl_total_deposit_stat.pack(side=tk.LEFT)

        # Card 3: Latest Due (Soft Red)
        card_due = tk.Frame(right_totals, bg="#fef2f2", padx=6, pady=2, bd=1, relief="solid")
        card_due.pack(side=tk.LEFT, padx=(0, 8))
        tk.Label(card_due, text="সর্বশেষ Due:", font=("Segoe UI", 8, "bold"), bg="#fef2f2", fg="#991b1b").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_total_due_stat = tk.Label(card_due, text="৳ 0.00", font=("Segoe UI", 10, "bold"), bg="#fef2f2", fg="#dc2626")
        self.lbl_total_due_stat.pack(side=tk.LEFT)

        # Save Complete Invoice Snapshot
        btn_save_inv = ttk.Button(
            right_totals,
            text="💾 সংরক্ষণ (Ctrl+S)",
            style="Success.TButton",
            cursor="hand2",
            command=self.save_invoice_action
        )
        btn_save_inv.pack(side=tk.LEFT)

    def create_status_bar(self):
        """Bottom-most status bar for system telemetry."""
        status_bar = tk.Frame(self.root, bg="#e2e8f0", height=24)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_left = tk.Label(
            status_bar,
            text="🟢 ডাটাবেস প্রস্তুত (SQLite Connected: amar_hisab.db) | F5 চেপে যেকোনো সময় রিফ্রেশ করুন",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            fg="#047857"
        )
        self.status_left.pack(side=tk.LEFT, padx=10)

        self.status_right = tk.Label(
            status_bar,
            text="আইটেম: 0 টি",
            font=("Segoe UI", 8),
            bg="#e2e8f0",
            fg="#475569"
        )
        self.status_right.pack(side=tk.RIGHT, padx=10)

    # ==============================================================
    # নিখুঁত কার্সর মুভমেন্ট ও কীবোর্ড নেভিগেশন (100% Mouse-Free)
    # ==============================================================
    def set_focus_and_select(self, widget):
        """Focus a widget and select its entire text for fast replacement."""
        widget.focus_set()
        widget.selection_range(0, tk.END)
        widget.icursor(tk.END)

    def on_entry_focus_in(self, event):
        """When an entry gains focus, select all text for instant replacement."""
        widget = event.widget
        widget.after(10, lambda: widget.selection_range(0, tk.END))
        widget.after(10, lambda: widget.icursor(tk.END))

    def setup_keyboard_navigation(self):
        """
        Flawless cursor movement:
        1. Date -> (Enter/Tab) -> B&W Pages
        2. B&W Pages -> (Enter/Tab) -> Color Pages
        3. Color Pages -> (Enter/Tab) -> Rate
        4. Rate -> (Enter/Tab) -> Deposit
        5. Deposit -> (Enter) -> Automatically triggers Save and moves back to B&W Pages!
        No mouse required!
        """
        def make_nav(target_widget):
            def handler(event):
                self.set_focus_and_select(target_widget)
                return "break"
            return handler

        all_entries = [
            self.entry_client_name,
            self.entry_client_whatsapp,
            self.entry_client_address,
            self.entry_date,
            self.entry_bw_pages,
            self.entry_color_pages,
            self.entry_rate,
            self.entry_deposit
        ]
        for entry in all_entries:
            entry.bind("<FocusIn>", self.on_entry_focus_in)

        # Top section navigation
        self.entry_client_name.bind("<Return>", make_nav(self.entry_client_whatsapp))
        self.entry_client_name.bind("<Tab>", make_nav(self.entry_client_whatsapp))

        self.entry_client_whatsapp.bind("<Return>", lambda e: self.on_whatsapp_enter())
        self.entry_client_whatsapp.bind("<Tab>", make_nav(self.entry_date))

        self.entry_client_address.bind("<Return>", make_nav(self.entry_date))
        self.entry_client_address.bind("<Tab>", make_nav(self.entry_date))

        # ৫টি ডেটা এন্ট্রি ঘরের কার্সর মুভমেন্ট:
        # ১. তারিখ (Date)
        self.entry_date.bind("<Return>", make_nav(self.entry_bw_pages))
        self.entry_date.bind("<Tab>", make_nav(self.entry_bw_pages))
        self.entry_date.bind("<Shift-Tab>", make_nav(self.entry_client_whatsapp))

        # ২. B&W পেজ (B&W Pages)
        self.entry_bw_pages.bind("<Return>", make_nav(self.entry_color_pages))
        self.entry_bw_pages.bind("<Tab>", make_nav(self.entry_color_pages))
        self.entry_bw_pages.bind("<Shift-Tab>", make_nav(self.entry_date))

        # ৩. Color পেজ (Color Pages)
        self.entry_color_pages.bind("<Return>", make_nav(self.entry_rate))
        self.entry_color_pages.bind("<Tab>", make_nav(self.entry_rate))
        self.entry_color_pages.bind("<Shift-Tab>", make_nav(self.entry_bw_pages))

        # ৪. দর (Rate)
        self.entry_rate.bind("<Return>", make_nav(self.entry_deposit))
        self.entry_rate.bind("<Tab>", make_nav(self.entry_deposit))
        self.entry_rate.bind("<Shift-Tab>", make_nav(self.entry_color_pages))

        # ৫. জমা (Deposit)
        # ৫ নম্বর ঘরে (জমা) 'Enter' চাপলে যেন স্বয়ংক্রিয়ভাবে ডেটা সেভ হওয়ার ফাংশনটি কাজ করে!
        self.entry_deposit.bind("<Return>", lambda e: self.save_entry_from_keyboard())
        self.entry_deposit.bind("<Tab>", make_nav(self.entry_bw_pages))
        self.entry_deposit.bind("<Shift-Tab>", make_nav(self.entry_rate))

        # Global shortcuts for zero-mouse operations
        self.root.bind("<Control-s>", lambda e: self.save_invoice_action())
        self.root.bind("<Control-S>", lambda e: self.save_invoice_action())
        self.root.bind("<Control-n>", lambda e: self.reset_entire_bill())
        self.root.bind("<Control-N>", lambda e: self.reset_entire_bill())
        self.root.bind("<Control-w>", lambda e: self.send_whatsapp_reminder())
        self.root.bind("<Control-W>", lambda e: self.send_whatsapp_reminder())
        self.root.bind("<Control-p>", lambda e: self.print_or_view_bill_action())
        self.root.bind("<Control-P>", lambda e: self.print_or_view_bill_action())
        self.root.bind("<Delete>", lambda e: self.delete_selected_item())
        self.root.bind("<Escape>", lambda e: self.clear_entry_form())
        self.root.bind("<F5>", lambda e: self.refresh_all_action())

    def on_whatsapp_enter(self):
        """When Enter is pressed in WhatsApp box, lookup client and focus Date."""
        self.search_or_autofill_client(silent=True)
        self.set_focus_and_select(self.entry_date)
        return "break"

    def save_entry_from_keyboard(self):
        """Triggered specifically by pressing Enter on 5th field (জমা)."""
        self.save_entry_action(from_keyboard=True)
        return "break"

    # ==============================================================
    # নিখুঁত গাণিতিক হিসাব (Mathematical Engine - Fixed Logic)
    # ==============================================================
    def calculate_entry(self, bw_pages: int, color_pages: int, rate: float, deposit: float):
        """
        Calculates:
        1. Total Amount = (B&W + Color) * rate  (Strict: exactly 0 if total_pages is 0)
        2. Net Amount   = Total Amount - deposit
        3. previous_due = client's previous due from database
        4. new_due      = previous_due + net_amount
        """
        total_pages = bw_pages + color_pages
        # 1. Total Amount = total_pages * rate (0 when total_pages == 0)
        total_amount = total_pages * rate

        # 2. Net Amount = Total - deposit
        net_amount = total_amount - deposit

        # 3. Previous Due from client in database
        previous_due = self.current_client_previous_due
        if self.current_client_id:
            previous_due = database.get_client_due(self.current_client_id)

        # 4. New Due Amount = previous_due + net_amount
        new_due = previous_due + net_amount

        return total_pages, total_amount, net_amount, previous_due, new_due

    def parse_entry_values(self):
        """Safely parse inputs from the 5 entry boxes."""
        date_str = self.entry_date.get().strip() or datetime.date.today().strftime("%d-%m-%Y")

        try:
            bw_pages = int(self.entry_bw_pages.get().strip() or "0")
            if bw_pages < 0:
                raise ValueError
        except ValueError:
            bw_pages = 0

        try:
            color_pages = int(self.entry_color_pages.get().strip() or "0")
            if color_pages < 0:
                raise ValueError
        except ValueError:
            color_pages = 0

        try:
            rate = float(self.entry_rate.get().strip() or "0.0")
            if rate < 0:
                raise ValueError
        except ValueError:
            rate = 0.0

        try:
            deposit = float(self.entry_deposit.get().strip() or "0.0")
            if deposit < 0:
                raise ValueError
        except ValueError:
            deposit = 0.0

        total_pages, total_amount, net_amount, previous_due, new_due = self.calculate_entry(
            bw_pages, color_pages, rate, deposit
        )

        return date_str, bw_pages, color_pages, total_pages, rate, total_amount, deposit, net_amount, previous_due, new_due

    def update_live_calculations(self, event=None):
        """Live update for calculation badges while user types."""
        _, _, _, _, _, total_amount, deposit, net_amount, _, new_due = self.parse_entry_values()
        self.lbl_preview_total.config(text=f"৳ {total_amount:,.2f}")
        self.lbl_preview_net.config(text=f"৳ {net_amount:,.2f}")
        self.lbl_preview_new_due.config(text=f"৳ {new_due:,.2f}")

    def save_entry_action(self, from_keyboard: bool = False):
        """
        Executes Save Flow:
        1. Total Amount = total_pages * rate
        2. Net Amount   = Total - deposit
        3. Retrieves client's previous Due Amount from database
        4. Calculates New Due Amount = previous_due + net_amount
        5. Saves calculation to SQLite database
        6. Clears input fields
        7. Instantly returns cursor to Field 1 (B&W পেজ) for continuous mouse-free entry!
        """
        date_str = self.entry_date.get().strip()
        bw_str = self.entry_bw_pages.get().strip()
        col_str = self.entry_color_pages.get().strip()
        rate_str = self.entry_rate.get().strip()
        dep_str = self.entry_deposit.get().strip()

        # Validation
        if not date_str:
            date_str = datetime.date.today().strftime("%d-%m-%Y")
            self.entry_date.insert(0, date_str)

        try:
            bw_pages = int(bw_str or "0")
            if bw_pages < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("ভুল মান", "B&W পেজের সংখ্যা সঠিক পূর্ণসংখ্যা (>= 0) দিন।")
            self.set_focus_and_select(self.entry_bw_pages)
            return

        try:
            color_pages = int(col_str or "0")
            if color_pages < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("ভুল মান", "Color পেজের সংখ্যা সঠিক পূর্ণসংখ্যা (>= 0) দিন।")
            self.set_focus_and_select(self.entry_color_pages)
            return

        try:
            rate = float(rate_str or "0.0")
            if rate < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("ভুল মান", "দর (Rate) সঠিক সংখ্যা দিন।")
            self.set_focus_and_select(self.entry_rate)
            return

        try:
            deposit = float(dep_str or "0.0")
            if deposit < 0:
                raise ValueError
        except ValueError:
            messagebox.showwarning("ভুল মান", "জমার পরিমাণ সঠিক সংখ্যা দিন।")
            self.set_focus_and_select(self.entry_deposit)
            return

        total_pages = bw_pages + color_pages
        if total_pages == 0 and deposit == 0:
            messagebox.showwarning("খালি এন্ট্রি", "অনুগ্রহ করে পেজ সংখ্যা বা জমার পরিমাণ দিন।")
            self.set_focus_and_select(self.entry_bw_pages)
            return

        # Ensure Client is linked if name/phone is provided in top section
        client_name = self.entry_client_name.get().strip()
        whatsapp = self.entry_client_whatsapp.get().strip()
        if whatsapp and client_name and not self.current_client_id:
            try:
                cid, _ = database.save_or_update_client(
                    client_name, whatsapp, self.entry_client_address.get().strip()
                )
                self.current_client_id = cid
                self.current_client_name = client_name
                self.current_client_whatsapp = whatsapp
            except Exception:
                pass

        # Strict Mathematical Calculation:
        total_pages, total_amount, net_amount, previous_due, new_due = self.calculate_entry(
            bw_pages, color_pages, rate, deposit
        )

        # Save to Database
        saved_record = database.save_entry_record(
            client_id=self.current_client_id,
            client_name=self.current_client_name or client_name or "সাধারণ গ্রাহক",
            whatsapp=self.current_client_whatsapp or whatsapp or "",
            entry_date=date_str,
            bw_pages=bw_pages,
            color_pages=color_pages,
            rate=rate,
            deposit=deposit
        )

        # Update local client previous due tracker to the new due
        self.current_client_previous_due = new_due
        self.lbl_client_previous_due.config(text=f"৳ {new_due:,.2f}")
        if self.current_client_id:
            self.lbl_client_status.config(
                text=f"ক্লায়েন্ট ID: {self.current_client_id} | বাকি: ৳ {new_due:,.2f}",
                fg="#1e40af",
                bg="#dbeafe"
            )

        # Add to Treeview item list
        self.items_list.append(saved_record)
        self.refresh_treeview()

        # Telemetry update
        self.status_left.config(
            text=f"✅ সংরক্ষিত: Total=৳ {total_amount:,.2f} | Net=৳ {net_amount:,.2f} | New Due=৳ {new_due:,.2f}",
            fg="#047857"
        )

        # Reset Entry Fields
        self.clear_entry_form()

        # Return cursor automatically to Field 1 (B&W Pages) with selection
        # 100% Mouse-Free!
        self.set_focus_and_select(self.entry_bw_pages)

    def clear_entry_form(self):
        """Reset only the middle item entry form."""
        self.entry_bw_pages.delete(0, tk.END)
        self.entry_bw_pages.insert(0, "0")

        self.entry_color_pages.delete(0, tk.END)
        self.entry_color_pages.insert(0, "0")

        self.entry_deposit.delete(0, tk.END)
        self.entry_deposit.insert(0, "0")

        self.update_live_calculations()

    def refresh_treeview(self):
        """
        Re-render Treeview rows with high-contrast color matching:
        - due_added (Red) when net_amount > 0 (বাকি যোগ হয়েছে)
        - payment_made (Green) when net_amount < 0 (জমা/পরিশোধ করা হয়েছে)
        - zero_even / zero_odd (Slate) when net_amount == 0
        """
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, item in enumerate(self.items_list, start=1):
            net = float(item.get("net_amount", 0.0))
            if net > 0:
                tag = "due_added"
            elif net < 0:
                tag = "payment_made"
            else:
                tag = "zero_even" if idx % 2 == 0 else "zero_odd"

            self.tree.insert(
                "",
                tk.END,
                values=(
                    idx,
                    item.get("entry_date", ""),
                    item.get("bw_pages", 0),
                    item.get("color_pages", 0),
                    f"{float(item.get('rate', 0)):,.2f}",
                    f"{float(item.get('total_amount', 0)):,.2f}",
                    f"{float(item.get('deposit', 0)):,.2f}",
                    f"{net:+,.2f}",
                    f"{float(item.get('previous_due', 0)):,.2f}",
                    f"{float(item.get('new_due', 0)):,.2f}"
                ),
                tags=(tag,)
            )

        self.recalculate_totals()
        self.status_right.config(text=f"আইটেম: {len(self.items_list)} টি")

    def delete_selected_item(self):
        """Delete selected item from treeview."""
        selected_item = self.tree.selection()
        if not selected_item:
            messagebox.showinfo("নির্বাচন করুন", "টেবিল থেকে যে আইটেমটি মুছতে চান সেটি সিলেক্ট করুন।")
            return

        item_values = self.tree.item(selected_item[0])["values"]
        sl = int(item_values[0]) - 1

        if 0 <= sl < len(self.items_list):
            del self.items_list[sl]
            self.refresh_treeview()
            self.status_left.config(text="🗑️ আইটেম টেবিল থেকে মুছে ফেলা হয়েছে।", fg="#dc2626")

    def on_treeview_row_select(self, event=None):
        """
        When user clicks/selects any row in the Treeview table,
        auto-sync client context and due amount so WhatsApp message targets that row.
        """
        selected = self.tree.selection()
        if not selected:
            return

        item_vals = self.tree.item(selected[0])["values"]
        if not item_vals:
            return

        sl = int(item_vals[0]) - 1
        if 0 <= sl < len(self.items_list):
            record = self.items_list[sl]
            if record.get("client_name") and record["client_name"] != "সাধারণ গ্রাহক":
                self.entry_client_name.delete(0, tk.END)
                self.entry_client_name.insert(0, record["client_name"])
                self.current_client_name = record["client_name"]

            if record.get("whatsapp"):
                self.entry_client_whatsapp.delete(0, tk.END)
                self.entry_client_whatsapp.insert(0, record["whatsapp"])
                self.current_client_whatsapp = record["whatsapp"]

            if record.get("client_id"):
                self.current_client_id = record["client_id"]

            row_due = record.get("new_due", 0.0)
            self.lbl_client_previous_due.config(text=f"৳ {row_due:,.2f}")
            self.status_left.config(
                text=f"📌 সিলেক্টেড রো SL-{item_vals[0]}: বকেয়া ৳ {row_due:,.2f} | একশন নেওয়ার জন্য প্রস্তুত",
                fg="#1e40af"
            )

    def recalculate_totals(self):
        """Recalculate total bill, deposits, and latest due."""
        total_bill = sum(float(item.get("total_amount", 0.0)) for item in self.items_list)
        total_deposit = sum(float(item.get("deposit", 0.0)) for item in self.items_list)

        if self.items_list:
            latest_due = float(self.items_list[-1].get("new_due", 0.0))
        else:
            latest_due = self.current_client_previous_due

        self.lbl_subtotal.config(text=f"৳ {total_bill:,.2f}")
        self.lbl_total_deposit_stat.config(text=f"৳ {total_deposit:,.2f}")
        self.lbl_total_due_stat.config(text=f"৳ {latest_due:,.2f}")

    # ==============================================================
    # ৪. ক্লায়েন্ট ব্রাউজার মডাল (Single-Click Client Load - Req 2)
    # ==============================================================
    def open_client_browser(self):
        """
        Opens a modern Client Browser modal.
        SINGLE-CLICK directly on any client row IMMEDIATELY loads that client,
        their previous due, and their full daily entries ledger into the main view!
        """
        browser_win = tk.Toplevel(self.root)
        browser_win.title("👥 সংরক্ষিত ক্লায়েন্ট তালিকা (Client Browser)")
        browser_win.geometry("820x520")
        browser_win.minsize(700, 420)
        browser_win.configure(bg="#f8fafc")
        browser_win.transient(self.root)
        browser_win.grab_set()

        # Top Header & Live Filter Box
        top_bar = tk.Frame(browser_win, bg="#0f172a", padx=14, pady=10)
        top_bar.pack(fill=tk.X)

        tk.Label(
            top_bar,
            text="👥 সংরক্ষিত ক্লায়েন্ট তালিকা",
            font=("Segoe UI", 12, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        ).pack(side=tk.LEFT)

        tk.Label(
            top_bar,
            text="(যেকোনো ক্লায়েন্টের গায়ে একবার চাপ দিলেই তার সকল হিসাব লোড হয়ে যাবে)",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0f172a"
        ).pack(side=tk.LEFT, padx=10)

        # Filter / Search bar
        search_frame = tk.Frame(browser_win, bg="#ffffff", padx=14, pady=8, bd=1, relief="solid")
        search_frame.pack(fill=tk.X, padx=12, pady=(10, 6))

        tk.Label(
            search_frame,
            text="🔍 নাম বা নম্বর দিয়ে খুঁজুন:",
            font=("Segoe UI", 9, "bold"),
            bg="#ffffff",
            fg="#334155"
        ).pack(side=tk.LEFT, padx=(0, 6))

        search_var = tk.StringVar()
        search_entry = ttk.Entry(search_frame, textvariable=search_var, width=28, font=("Segoe UI", 10))
        search_entry.pack(side=tk.LEFT, padx=(0, 10))

        count_lbl = tk.Label(
            search_frame,
            text="মোট ক্লায়েন্ট: ০ জন",
            font=("Segoe UI", 9),
            bg="#ffffff",
            fg="#64748b"
        )
        count_lbl.pack(side=tk.RIGHT)

        # Clients Table
        table_box = tk.Frame(browser_win, bg="#ffffff")
        table_box.pack(fill=tk.BOTH, expand=True, padx=12, pady=(0, 8))

        scroll_y = ttk.Scrollbar(table_box, orient=tk.VERTICAL)
        scroll_y.pack(side=tk.RIGHT, fill=tk.Y)

        cols = ("id", "name", "whatsapp", "address", "due_balance")
        tree_clients = ttk.Treeview(
            table_box,
            columns=cols,
            show="headings",
            style="Custom.Treeview",
            yscrollcommand=scroll_y.set
        )
        scroll_y.config(command=tree_clients.yview)

        tree_clients.heading("id", text="ID", anchor=tk.CENTER)
        tree_clients.heading("name", text="গ্রাহকের নাম", anchor=tk.W)
        tree_clients.heading("whatsapp", text="WhatsApp নম্বর", anchor=tk.CENTER)
        tree_clients.heading("address", text="ঠিকানা", anchor=tk.W)
        tree_clients.heading("due_balance", text="বকেয়া ব্যালেন্স (Due ৳)", anchor=tk.E)

        tree_clients.column("id", width=50, anchor=tk.CENTER)
        tree_clients.column("name", width=190, anchor=tk.W)
        tree_clients.column("whatsapp", width=140, anchor=tk.CENTER)
        tree_clients.column("address", width=180, anchor=tk.W)
        tree_clients.column("due_balance", width=140, anchor=tk.E)

        tree_clients.tag_configure("even", background="#ffffff")
        tree_clients.tag_configure("odd", background="#f8fafc")
        tree_clients.tag_configure("due", background="#fee2e2", foreground="#991b1b")

        tree_clients.pack(fill=tk.BOTH, expand=True)

        all_clients_data = []

        def load_table(query=""):
            for row in tree_clients.get_children():
                tree_clients.delete(row)

            q = query.lower().strip()
            count = 0
            for idx, c in enumerate(all_clients_data):
                c_name = str(c.get("name", "")).lower()
                c_phone = str(c.get("whatsapp", "")).lower()
                if q and (q not in c_name and q not in c_phone):
                    continue

                count += 1
                due_val = float(c.get("due_balance", 0.0))
                tag = "due" if due_val > 0 else ("even" if idx % 2 == 0 else "odd")

                tree_clients.insert(
                    "",
                    tk.END,
                    values=(
                        c["id"],
                        c["name"],
                        c["whatsapp"],
                        c.get("address", "") or "—",
                        f"৳ {due_val:,.2f}"
                    ),
                    tags=(tag,)
                )
            count_lbl.config(text=f"প্রদর্শিত: {count} জন")

        def refresh_clients_data():
            nonlocal all_clients_data
            all_clients_data = database.get_all_clients()
            load_table(search_var.get())

        search_var.trace_add("write", lambda *args: load_table(search_var.get()))

        # Core Action: Select and Load Client into Main App
        def select_and_load_client(client_id):
            client = database.get_client_by_id(client_id)
            if not client:
                return

            self.current_client_id = client["id"]
            self.current_client_name = client["name"]
            self.current_client_whatsapp = client["whatsapp"]
            self.current_client_address = client.get("address", "") or ""

            # Load into inputs
            self.entry_client_name.delete(0, tk.END)
            self.entry_client_name.insert(0, client["name"])
            self.entry_client_whatsapp.delete(0, tk.END)
            self.entry_client_whatsapp.insert(0, client["whatsapp"])
            self.entry_client_address.delete(0, tk.END)
            self.entry_client_address.insert(0, self.current_client_address)

            # Sync previous due
            due_val = database.get_client_due(client["id"])
            self.current_client_previous_due = due_val
            self.lbl_client_previous_due.config(text=f"৳ {due_val:,.2f}")
            self.lbl_client_status.config(
                text=f"ক্লায়েন্ট ID: {client['id']} | বাকি: ৳ {due_val:,.2f}",
                fg="#1e40af",
                bg="#dbeafe"
            )

            # Load all past daily entries for this client into items_list
            entries = database.get_client_entries(client["id"])
            self.items_list = entries
            self.refresh_treeview()

            self.status_left.config(
                text=f"✅ ক্লায়েন্ট '{client['name']}' লোড হয়েছে! পূর্বের এন্ট্রি: {len(entries)} টি | বকেয়া: ৳ {due_val:,.2f}",
                fg="#047857"
            )

            browser_win.destroy()
            self.set_focus_and_select(self.entry_bw_pages)

        # ── REQUIREMENT 2 FIX: SINGLE CLICK EVENT BINDING ─────────
        def on_single_click(event):
            # Identify row clicked
            row_id = tree_clients.identify_row(event.y)
            if row_id:
                tree_clients.selection_set(row_id)
                vals = tree_clients.item(row_id, "values")
                if vals:
                    select_and_load_client(int(vals[0]))

        tree_clients.bind("<ButtonRelease-1>", on_single_click)
        tree_clients.bind("<Double-1>", on_single_click)
        tree_clients.bind("<Return>", lambda e: on_single_click(e))

        # Bottom Action Buttons
        bottom_bar = tk.Frame(browser_win, bg="#f8fafc", padx=12, pady=8)
        bottom_bar.pack(fill=tk.X)

        def on_btn_load_click():
            sel = tree_clients.selection()
            if not sel:
                messagebox.showinfo("নির্বাচন করুন", "অনুগ্রহ করে তালিকা থেকে একজন ক্লায়েন্ট সিলেক্ট করুন।")
                return
            vals = tree_clients.item(sel[0], "values")
            if vals:
                select_and_load_client(int(vals[0]))

        btn_load = ttk.Button(
            bottom_bar,
            text="✅ ক্লায়েন্ট ও লেজার লোড করুন",
            style="Success.TButton",
            cursor="hand2",
            command=on_btn_load_click
        )
        btn_load.pack(side=tk.LEFT, padx=(0, 8))

        btn_close = ttk.Button(
            bottom_bar,
            text="❌ বন্ধ করুন",
            style="Secondary.TButton",
            cursor="hand2",
            command=browser_win.destroy
        )
        btn_close.pack(side=tk.RIGHT)

        refresh_clients_data()
        search_entry.focus_set()

    # ==============================================================
    # ৫. বিল প্রস্তুত ও এক্সপোর্ট (Print, PDF, WhatsApp - Req 3)
    # ==============================================================
    def get_current_bill_context(self):
        """Helper to get current client info and item list for bill generation."""
        c_name = self.entry_client_name.get().strip() or self.current_client_name or "সাধারণ গ্রাহক"
        c_phone = self.entry_client_whatsapp.get().strip() or self.current_client_whatsapp or ""
        c_address = self.entry_client_address.get().strip() or self.current_client_address or ""
        items = list(self.items_list)
        return c_name, c_phone, c_address, items

    def print_or_view_bill_action(self):
        """
        Generates printable HTML bill and opens it directly in default browser.
        Browser triggers window.print() dialogue for instant printing or PDF save.
        """
        c_name, c_phone, c_address, items = self.get_current_bill_context()
        if not items:
            messagebox.showwarning("খালি বিল", "প্রিন্ট করার জন্য কোনো আইটেম যোগ করা নেই।")
            return

        try:
            fpath = bill_generator.open_html_bill_in_browser(c_name, c_phone, c_address, items)
            self.status_left.config(
                text=f"🖨️ প্রিন্ট ও ব্রাউজার ভিউ প্রস্তুত: {os.path.basename(fpath)}",
                fg="#047857"
            )
        except Exception as e:
            messagebox.showerror("ত্রুটি", f"বিল তৈরি করতে সমস্যা: {str(e)}")

    def export_pdf_bill_action(self):
        """
        Generates professional A4 PDF bill using ReportLab (if installed)
        or falls back to browser HTML bill for saving as PDF.
        """
        c_name, c_phone, c_address, items = self.get_current_bill_context()
        if not items:
            messagebox.showwarning("খালি বিল", "পিডিএফ তৈরি করার জন্য কোনো আইটেম যোগ করা নেই।")
            return

        try:
            pdf_path = bill_generator.generate_pdf_bill(c_name, c_phone, c_address, items)
            # Open the generated PDF automatically
            if sys.platform == "win32":
                os.startfile(pdf_path)
            else:
                webbrowser.open(f"file://{pdf_path}")

            self.status_left.config(
                text=f"📄 পিডিএফ বিল তৈরি সম্পন্ন: {os.path.basename(pdf_path)}",
                fg="#047857"
            )
            messagebox.showinfo(
                "পিডিএফ সফল",
                f"বিলটি সফলভাবে পিডিএফ আকারে সেভ ও ওপেন করা হয়েছে:\n{pdf_path}"
            )
        except Exception as e:
            # Fallback to browser print
            bill_generator.open_html_bill_in_browser(c_name, c_phone, c_address, items)
            messagebox.showinfo(
                "ব্রাউজারে পিডিএফ সেভ করুন",
                f"রিপোর্ট-ল্যাব সমস্যা: {str(e)}\nবিকল্প হিসেবে ব্রাউজারে বিল খোলা হয়েছে। সেখান থেকে 'Save as PDF' নির্বাচন করুন।"
            )

    def send_full_bill_whatsapp_action(self):
        """Opens WhatsApp Web with complete itemized bill breakdown."""
        c_name, c_phone, _, items = self.get_current_bill_context()
        if not c_phone:
            messagebox.showwarning("WhatsApp নম্বর নেই", "অনুগ্রহ করে ক্লায়েন্টের WhatsApp নম্বর দিন।")
            self.set_focus_and_select(self.entry_client_whatsapp)
            return

        if not items:
            messagebox.showwarning("খালি বিল", "বিলে পাঠানোর মতো কোনো আইটেম নেই।")
            return

        try:
            formatted = bill_generator.send_full_bill_whatsapp(c_phone, c_name, items)
            self.status_left.config(
                text=f"📲 WhatsApp-এ পূর্ণ বিল পাঠানো হচ্ছে ({formatted})...",
                fg="#047857"
            )
        except Exception as e:
            messagebox.showerror("WhatsApp ত্রুটি", str(e))

    # ==============================================================
    # ৬. WhatsApp বকেয়া রিমাইন্ডার (pywhatkit ইন্টিগ্রেশন)
    # ==============================================================
    def send_whatsapp_reminder(self):
        """
        Sends automated WhatsApp message with client's latest Due Amount
        using pywhatkit in a non-blocking background thread.
        """
        client_name = self.entry_client_name.get().strip() or self.current_client_name or "সম্মানিত গ্রাহক"
        whatsapp = self.entry_client_whatsapp.get().strip() or self.current_client_whatsapp

        # Prioritize selected Treeview row context if any
        selected_item = self.tree.selection()
        selected_row_due = None
        if selected_item:
            item_vals = self.tree.item(selected_item[0])["values"]
            sl = int(item_vals[0]) - 1
            if 0 <= sl < len(self.items_list):
                row_rec = self.items_list[sl]
                selected_row_due = row_rec.get("new_due")
                if row_rec.get("whatsapp"):
                    whatsapp = row_rec["whatsapp"]
                if row_rec.get("client_name"):
                    client_name = row_rec["client_name"]

        # Check if WhatsApp number is present
        if not whatsapp:
            messagebox.showwarning(
                "WhatsApp নম্বর নেই",
                "অনুগ্রহ করে ক্লায়েন্টের WhatsApp নম্বর প্রদান করুন বা টেবিল থেকে কোনো ক্লায়েন্ট সিলেক্ট করুন।"
            )
            self.set_focus_and_select(self.entry_client_whatsapp)
            return

        # Determine latest Due Amount
        if selected_row_due is not None:
            latest_due = float(selected_row_due)
        elif self.current_client_id:
            latest_due = database.get_client_due(self.current_client_id)
        elif self.items_list:
            latest_due = float(self.items_list[-1].get("new_due", 0.0))
        else:
            latest_due = self.current_client_previous_due

        formatted_phone = whatsapp_sender.format_phone_number(whatsapp)
        if not formatted_phone:
            messagebox.showwarning(
                "ভুল নম্বর",
                f"প্রদত্ত নম্বরটি সঠিক নয়: '{whatsapp}'\nসঠিক নম্বর দিন (যেমন: 01711223344)।"
            )
            self.set_focus_and_select(self.entry_client_whatsapp)
            return

        # Prepare message preview for confirmation
        msg_preview = whatsapp_sender.create_professional_due_message(
            client_name=client_name,
            due_amount=latest_due
        )

        confirm = messagebox.askyesno(
            "WhatsApp মেসেজ পাঠান",
            f"গ্রাহক: {client_name}\n"
            f"WhatsApp নম্বর: {formatted_phone}\n"
            f"সর্বশেষ বকেয়া (Due): ৳ {latest_due:,.2f}\n\n"
            f"মেসেজ প্রিভিউ:\n-----------------------------------\n"
            f"{msg_preview}\n-----------------------------------\n\n"
            f"আপনি কি এই রিমাইন্ডার মেসেজটি পাঠাতে চান?"
        )
        if not confirm:
            return

        # Update telemetry
        self.status_left.config(
            text=f"⏳ {client_name} ({formatted_phone})-কে WhatsApp মেসেজ পাঠানো হচ্ছে...",
            fg="#2563eb"
        )

        def on_success(msg):
            self.root.after(0, lambda: self.status_left.config(text=f"✅ {msg}", fg="#047857"))
            self.root.after(0, lambda: messagebox.showinfo("WhatsApp সফল", msg))

        def on_error(err):
            self.root.after(0, lambda: self.status_left.config(text=f"❌ {err}", fg="#dc2626"))
            self.root.after(0, lambda: messagebox.showerror("WhatsApp ত্রুটি", err))

        # Launch in background thread
        whatsapp_sender.send_whatsapp_message(
            phone=formatted_phone,
            client_name=client_name,
            due_amount=latest_due,
            on_success=on_success,
            on_error=on_error
        )

    # ==============================================================
    # ৭. ইন-অ্যাপ রিফ্রেশ বাটন (Requirement 6)
    # ==============================================================
    def refresh_all_action(self):
        """
        In-App Refresh triggered by Refresh Button or F5 key.
        Reloads current client's data from SQLite, recalculates totals,
        and provides instant visual feedback.
        """
        if self.current_client_id:
            # Re-fetch client information
            client = database.get_client_by_id(self.current_client_id)
            if client:
                self.current_client_name = client["name"]
                self.current_client_whatsapp = client["whatsapp"]
                self.current_client_address = client.get("address", "") or ""
                due_val = database.get_client_due(client["id"])
                self.current_client_previous_due = due_val

                self.lbl_client_previous_due.config(text=f"৳ {due_val:,.2f}")
                self.lbl_client_status.config(
                    text=f"ক্লায়েন্ট ID: {client['id']} | বাকি: ৳ {due_val:,.2f}",
                    fg="#1e40af",
                    bg="#dbeafe"
                )

                # Re-load client entries
                self.items_list = database.get_client_entries(client["id"])

        self.refresh_treeview()
        self.update_live_calculations()

        self.status_left.config(
            text="🔄 রিফ্রেশ সম্পন্ন! সকল ডাটা সর্বশেষ অবস্থায় আপডেট করা হয়েছে।",
            fg="#047857"
        )

    # ==============================================================
    # ৮. ডেস্কটপ শর্টকাট একশন (Requirement 5)
    # ==============================================================
    def create_desktop_shortcut_action(self):
        """Creates desktop shortcut for user upon clicking button."""
        ok = create_desktop_shortcut()
        if ok:
            messagebox.showinfo(
                "শর্টকাট তৈরি সফল",
                "পিসির ডেস্কটপে 'Amar Hisab' শর্টকাট সফলভাবে তৈরি করা হয়েছে!\n"
                "এখন ডেস্কটপ থেকেই সরাসরি অ্যাপ চালু করতে পারবেন।"
            )
            self.status_left.config(text="🖥️ ডেস্কটপে শর্টকাট সক্রিয় আছে।", fg="#047857")
        else:
            messagebox.showerror("ত্রুটি", "শর্টকাট তৈরি করতে ব্যর্থ হয়েছে।")

    # ==============================================================
    # ৯. ক্লায়েন্ট অনুসন্ধান ও সংরক্ষণ
    # ==============================================================
    def search_or_autofill_client(self, silent: bool = False):
        """Search client in SQLite by WhatsApp number and load Previous Due."""
        phone = self.entry_client_whatsapp.get().strip()
        if not phone:
            if not silent:
                messagebox.showwarning("সতর্কতা", "অনুগ্রহ করে WhatsApp নম্বর প্রদান করুন।")
                self.set_focus_and_select(self.entry_client_whatsapp)
            return

        client = database.find_client_by_whatsapp(phone)
        if client:
            self.current_client_id = client["id"]
            self.current_client_name = client["name"]
            self.current_client_whatsapp = client["whatsapp"]
            self.current_client_address = client.get("address", "") or ""

            # Load previous due from database
            due_val = database.get_client_due(client["id"])
            self.current_client_previous_due = due_val

            self.entry_client_name.delete(0, tk.END)
            self.entry_client_name.insert(0, client["name"])
            self.entry_client_address.delete(0, tk.END)
            self.entry_client_address.insert(0, self.current_client_address)

            self.lbl_client_previous_due.config(text=f"৳ {due_val:,.2f}")
            self.lbl_client_status.config(
                text=f"পুরাতন ক্লায়েন্ট (ID: {client['id']}) | বাকি: ৳ {due_val:,.2f}",
                fg="#1e40af",
                bg="#dbeafe"
            )
            self.update_live_calculations()

            # Load past ledger entries
            self.items_list = database.get_client_entries(client["id"])
            self.refresh_treeview()

            if not silent:
                messagebox.showinfo(
                    "ক্লায়েন্ট পাওয়া গেছে",
                    f"গ্রাহক: {client['name']}\nসর্বশেষ বকেয়া (Due): ৳ {due_val:,.2f}\nমোট আগের হিসাব: {len(self.items_list)} টি"
                )
            self.set_focus_and_select(self.entry_bw_pages)
        else:
            self.current_client_id = None
            self.current_client_previous_due = 0.0
            self.lbl_client_previous_due.config(text="৳ 0.00")
            self.lbl_client_status.config(
                text="নতুন ক্লায়েন্ট",
                fg="#059669",
                bg="#d1fae5"
            )
            self.update_live_calculations()
            if not silent:
                messagebox.showinfo("নতুন ক্লায়েন্ট", "এই নম্বরে কোনো ক্লায়েন্ট সংরক্ষিত নেই।")
            self.set_focus_and_select(self.entry_client_name)

    def save_client_action(self):
        """Save or update client into SQLite database and sync due."""
        name = self.entry_client_name.get().strip()
        whatsapp = self.entry_client_whatsapp.get().strip()
        address = self.entry_client_address.get().strip()

        if not name:
            messagebox.showwarning("প্রয়োজনীয় তথ্য", "গ্রাহকের নাম প্রদান করুন।")
            self.set_focus_and_select(self.entry_client_name)
            return

        if not whatsapp:
            messagebox.showwarning("প্রয়োজনীয় তথ্য", "WhatsApp নম্বর প্রদান করুন।")
            self.set_focus_and_select(self.entry_client_whatsapp)
            return

        try:
            client_id, is_new = database.save_or_update_client(name, whatsapp, address)
            self.current_client_id = client_id
            self.current_client_name = name
            self.current_client_whatsapp = whatsapp
            self.current_client_address = address

            due_val = database.get_client_due(client_id)
            self.current_client_previous_due = due_val
            self.lbl_client_previous_due.config(text=f"৳ {due_val:,.2f}")

            status_text = "সংরক্ষিত" if is_new else "আপডেট করা হয়েছে"
            self.lbl_client_status.config(
                text=f"সংরক্ষিত (ID: {client_id}) | বাকি: ৳ {due_val:,.2f}",
                fg="#047857",
                bg="#d1fae5"
            )
            messagebox.showinfo("সফল", f"ক্লায়েন্ট '{name}' সফলভাবে {status_text}!\nআগের বাকি: ৳ {due_val:,.2f}")
            self.set_focus_and_select(self.entry_bw_pages)
        except Exception as e:
            messagebox.showerror("ডাটাবেস ত্রুটি", f"ক্লায়েন্ট সংরক্ষণে ত্রুটি: {str(e)}")

    def save_invoice_action(self):
        """Save complete invoice snapshot to SQLite."""
        if not self.items_list:
            messagebox.showwarning("খালি বিল", "বিলে কোনো এন্ট্রি নেই! প্রথমে আইটেম যোগ করুন।")
            self.set_focus_and_select(self.entry_bw_pages)
            return

        client_name = self.entry_client_name.get().strip()
        whatsapp = self.entry_client_whatsapp.get().strip()

        if not whatsapp or not client_name:
            res = messagebox.askyesno(
                "ক্লায়েন্ট তথ্য নেই",
                "গ্রাহকের নাম ও WhatsApp নম্বর ছাড়া ইনভয়েস সেভ করতে চান?"
            )
            if not res:
                self.set_focus_and_select(self.entry_client_name)
                return

        # Ensure client is saved if details are entered
        client_id = self.current_client_id
        if client_name and whatsapp and not client_id:
            try:
                client_id, _ = database.save_or_update_client(
                    client_name,
                    whatsapp,
                    self.entry_client_address.get().strip()
                )
                self.current_client_id = client_id
            except Exception as e:
                messagebox.showerror("ক্লায়েন্ট সংরক্ষণ ত্রুটি", str(e))
                return

        total_bill = sum(float(item.get("total_amount", 0.0)) for item in self.items_list)
        total_deposit = sum(float(item.get("deposit", 0.0)) for item in self.items_list)
        latest_due = float(self.items_list[-1].get("new_due", 0.0))

        try:
            database.save_invoice(
                invoice_no=self.invoice_number,
                client_id=client_id,
                subtotal=total_bill,
                discount=0.0,
                net_total=latest_due,
                items=self.items_list,
                payment_status="Paid" if latest_due == 0 else "Due"
            )
            messagebox.showinfo(
                "ইনভয়েস সংরক্ষিত!",
                f"ইনভয়েস {self.invoice_number} সফলভাবে ডাটাবেসে সেভ হয়েছে!\n"
                f"মোট বিল: ৳ {total_bill:,.2f}\n"
                f"মোট জমা: ৳ {total_deposit:,.2f}\n"
                f"সর্বশেষ Due Amount: ৳ {latest_due:,.2f}"
            )
            self.reset_entire_bill()
        except Exception as e:
            messagebox.showerror("ডাটাবেস সংরক্ষণ ত্রুটি", f"বিল সেভ করতে ব্যর্থ: {str(e)}")

    def reset_entire_bill(self):
        """Reset all forms and start a fresh bill."""
        self.items_list = []
        self.current_client_id = None
        self.current_client_name = ""
        self.current_client_whatsapp = ""
        self.current_client_address = ""
        self.current_client_previous_due = 0.0
        self.invoice_number = self.generate_invoice_no()
        self.inv_lbl.config(text=f"ইনভয়েস নং: {self.invoice_number}")

        # Clear Client
        self.entry_client_name.delete(0, tk.END)
        self.entry_client_whatsapp.delete(0, tk.END)
        self.entry_client_address.delete(0, tk.END)
        self.lbl_client_previous_due.config(text="৳ 0.00")
        self.lbl_client_status.config(text="নতুন ক্লায়েন্ট", fg="#64748b", bg="#f1f5f9")

        # Clear Entries
        self.clear_entry_form()
        self.refresh_treeview()

        # Return focus to Client Name
        self.set_focus_and_select(self.entry_client_name)


def main():
    root = tk.Tk()
    app = BillingApp(root)
    root.mainloop()


if __name__ == "__main__":
    main()
