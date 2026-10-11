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
- Automated WhatsApp Due Notification Integration via pywhatkit
"""

import sys
import os
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

# Ensure UTF-8 output in Windows console if needed
if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass

import database
import whatsapp_sender


class BillingApp:
    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("আমার হিসাব (Amar Hisab) - প্রফেশনাল বিলিং ও লেজার সফটওয়্যার")
        self.root.geometry("1260x820")
        self.root.minsize(1120, 720)

        # Initialize Database
        database.init_db()

        # Application State
        self.items_list = []
        self.current_client_id = None
        self.current_client_name = ""
        self.current_client_whatsapp = ""
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
        # Clean soft slate background
        self.root.configure(bg="#f8fafc")

        self.style = ttk.Style()
        self.style.theme_use("clam")

        # Color Tokens
        self.COLOR_BG = "#f8fafc"            # Soft Slate-50 background
        self.COLOR_CARD = "#ffffff"          # Crisp White
        self.COLOR_BORDER = "#e2e8f0"        # Subtle Border
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

        # Card Container (TLabelframe)
        self.style.configure(
            "Card.TLabelframe",
            background=self.COLOR_CARD,
            bordercolor=self.COLOR_BORDER,
            relief="solid",
            borderwidth=1,
            padding=10
        )
        self.style.configure(
            "Card.TLabelframe.Label",
            background=self.COLOR_CARD,
            foreground="#1e3a8a",
            font=("Segoe UI", 11, "bold")
        )

        # Standard Label
        self.style.configure(
            "TLabel",
            background=self.COLOR_CARD,
            foreground=self.COLOR_TEXT_MAIN,
            font=("Segoe UI", 10)
        )
        self.style.configure(
            "FieldLabel.TLabel",
            background=self.COLOR_CARD,
            foreground="#334155",
            font=("Segoe UI", 9, "bold")
        )

        # Modern Entry Styling
        self.style.configure(
            "TEntry",
            fieldbackground="#ffffff",
            foreground="#0f172a",
            padding=5,
            bordercolor=self.COLOR_BORDER,
            lightcolor=self.COLOR_PRIMARY,
            darkcolor=self.COLOR_BORDER
        )

        # Primary Button (Blue)
        self.style.configure(
            "Primary.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.COLOR_PRIMARY,
            foreground="#ffffff",
            padding=7,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("Primary.TButton",
                       background=[("active", self.COLOR_PRIMARY_HOVER), ("pressed", "#1e40af")])

        # Success Button (Emerald)
        self.style.configure(
            "Success.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.COLOR_SUCCESS,
            foreground="#ffffff",
            padding=7,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("Success.TButton",
                       background=[("active", self.COLOR_SUCCESS_HOVER), ("pressed", "#047857")])

        # WhatsApp Button (Brand Green)
        self.style.configure(
            "WhatsApp.TButton",
            font=("Segoe UI", 10, "bold"),
            background=self.COLOR_WHATSAPP,
            foreground="#ffffff",
            padding=7,
            borderwidth=0,
            relief="flat",
            focuscolor="none"
        )
        self.style.map("WhatsApp.TButton",
                       background=[("active", self.COLOR_WHATSAPP_HOVER), ("pressed", "#15803d")])

        # Danger Button (Red)
        self.style.configure(
            "Danger.TButton",
            font=("Segoe UI", 9, "bold"),
            background=self.COLOR_DANGER,
            foreground="#ffffff",
            padding=6,
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
            padding=6,
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
            rowheight=30,
            font=("Segoe UI", 9),
            borderwidth=1
        )
        self.style.configure(
            "Treeview",
            background="#ffffff",
            foreground="#0f172a",
            fieldbackground="#ffffff",
            rowheight=30,
            font=("Segoe UI", 9),
            borderwidth=1
        )
        self.style.configure(
            "Treeview.Heading",
            background="#1e293b",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            padding=6,
            relief="flat"
        )
        self.style.configure(
            "Custom.Treeview.Heading",
            background="#1e293b",
            foreground="#ffffff",
            font=("Segoe UI", 9, "bold"),
            padding=6,
            relief="flat"
        )
        self.style.map("Treeview.Heading",
                       background=[("active", "#334155")])
        self.style.map("Custom.Treeview.Heading",
                       background=[("active", "#334155")])
        self.style.map("Custom.Treeview",
                       background=[("selected", "#dbeafe")],
                       foreground=[("selected", "#1e3a8a")])
        self.style.map("Treeview",
                       background=[("selected", "#dbeafe")],
                       foreground=[("selected", "#1e3a8a")])

    def create_header(self):
        """Top Brand Header with dark corporate gradient look & invoice pill."""
        header_frame = tk.Frame(self.root, bg="#0f172a", height=68)
        header_frame.pack(side=tk.TOP, fill=tk.X)

        # Bottom accent line (modern Blue-500 border)
        accent_line = tk.Frame(header_frame, bg="#3b82f6", height=2)
        accent_line.pack(side=tk.BOTTOM, fill=tk.X)

        # Left Title Box
        title_box = tk.Frame(header_frame, bg="#0f172a")
        title_box.pack(side=tk.LEFT, padx=22, pady=10)

        main_title = tk.Label(
            title_box,
            text="⚡ আমার হিসাব (Amar Hisab)",
            font=("Segoe UI", 16, "bold"),
            fg="#f8fafc",
            bg="#0f172a"
        )
        main_title.pack(anchor="w")

        subtitle = tk.Label(
            title_box,
            text="প্রফেশনাল ডিজিটাল বিলিং ও লেজার সফটওয়্যার (Total = [B&W + Color] × দর | Net = Total - জমা)",
            font=("Segoe UI", 9),
            fg="#94a3b8",
            bg="#0f172a"
        )
        subtitle.pack(anchor="w")

        # Right Info Box (Pill card)
        inv_box = tk.Frame(header_frame, bg="#1e293b", padx=14, pady=6, bd=1, relief="flat")
        inv_box.pack(side=tk.RIGHT, padx=22, pady=10)

        self.inv_lbl = tk.Label(
            inv_box,
            text=f"ইনভয়েস: {self.invoice_number}",
            font=("Segoe UI", 10, "bold"),
            fg="#38bdf8",
            bg="#1e293b"
        )
        self.inv_lbl.pack(anchor="e")

        today_str = datetime.date.today().strftime("%d-%m-%Y")
        date_lbl = tk.Label(
            inv_box,
            text=f"তারিখ: {today_str}",
            font=("Segoe UI", 9),
            fg="#cbd5e1",
            bg="#1e293b"
        )
        date_lbl.pack(anchor="e")

    def create_main_container(self):
        """Main Content Area containing all 3 core sections."""
        self.main_container = tk.Frame(self.root, bg="#f8fafc")
        self.main_container.pack(fill=tk.BOTH, expand=True, padx=15, pady=8)

    # ==============================================================
    # ১. শীর্ষ অংশ: ক্লায়েন্ট তথ্য ও WhatsApp বকেয়া যোগাযোগ
    # ==============================================================
    def create_top_client_section(self):
        """Top Section: Client Details, Previous Due, and WhatsApp Button."""
        client_frame = ttk.LabelFrame(
            self.main_container,
            text="👤 ১. ক্লায়েন্টের তথ্য ও WhatsApp বকেয়া যোগাযোগ (Client Details & WhatsApp)",
            style="Card.TLabelframe"
        )
        client_frame.pack(fill=tk.X, pady=(0, 8))

        inner = tk.Frame(client_frame, bg=self.COLOR_CARD)
        inner.pack(fill=tk.X, padx=5, pady=3)

        # Client Name
        lbl_name = ttk.Label(inner, text="গ্রাহকের নাম: *", style="FieldLabel.TLabel")
        lbl_name.grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")

        self.entry_client_name = ttk.Entry(inner, width=18, font=("Segoe UI", 10))
        self.entry_client_name.grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")

        # WhatsApp Number
        lbl_whatsapp = ttk.Label(inner, text="WhatsApp নম্বর: *", style="FieldLabel.TLabel")
        lbl_whatsapp.grid(row=0, column=2, padx=(0, 4), pady=4, sticky="w")

        self.entry_client_whatsapp = ttk.Entry(inner, width=15, font=("Segoe UI", 10))
        self.entry_client_whatsapp.grid(row=0, column=3, padx=(0, 6), pady=4, sticky="w")

        # Find Client Button
        btn_search = ttk.Button(
            inner,
            text="🔍 খুঁজুন",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.search_or_autofill_client
        )
        btn_search.grid(row=0, column=4, padx=(0, 10), pady=4)

        # Client Address
        lbl_address = ttk.Label(inner, text="ঠিকানা:", style="FieldLabel.TLabel")
        lbl_address.grid(row=0, column=5, padx=(0, 4), pady=4, sticky="w")

        self.entry_client_address = ttk.Entry(inner, width=16, font=("Segoe UI", 10))
        self.entry_client_address.grid(row=0, column=6, padx=(0, 10), pady=4, sticky="w")

        # Save Client Button
        btn_save_client = ttk.Button(
            inner,
            text="💾 ক্লায়েন্ট সেভ",
            style="Success.TButton",
            cursor="hand2",
            command=self.save_client_action
        )
        btn_save_client.grid(row=0, column=7, padx=(0, 10), pady=4)

        # Previous Due Badge for loaded client
        due_badge_frame = tk.Frame(inner, bg="#fef2f2", padx=10, pady=3, bd=1, relief="solid")
        due_badge_frame.grid(row=0, column=8, padx=(0, 10), pady=4)

        tk.Label(
            due_badge_frame,
            text="আগের বাকি (Due):",
            font=("Segoe UI", 9, "bold"),
            bg="#fef2f2",
            fg="#991b1b"
        ).pack(side=tk.LEFT, padx=(0, 4))

        self.lbl_client_previous_due = tk.Label(
            due_badge_frame,
            text="৳ 0.00",
            font=("Segoe UI", 10, "bold"),
            bg="#fef2f2",
            fg="#dc2626"
        )
        self.lbl_client_previous_due.pack(side=tk.LEFT)

        # Prominent 'WhatsApp-এ মেসেজ পাঠান' Button
        self.btn_whatsapp_top = ttk.Button(
            inner,
            text="💬 WhatsApp-এ মেসেজ পাঠান",
            style="WhatsApp.TButton",
            cursor="hand2",
            command=self.send_whatsapp_reminder
        )
        self.btn_whatsapp_top.grid(row=0, column=9, padx=(0, 8), pady=4)

        # Client Status Badge
        self.lbl_client_status = tk.Label(
            inner,
            text="নতুন ক্লায়েন্ট",
            font=("Segoe UI", 9, "bold"),
            fg="#475569",
            bg="#f1f5f9",
            padx=10,
            pady=4,
            relief="solid",
            bd=0
        )
        self.lbl_client_status.grid(row=0, column=10, padx=4, pady=4)

    # ==============================================================
    # ২. মাঝের অংশ: ডেটা এন্ট্রি ফর্ম ও নিখুঁত হিসাব
    # ==============================================================
    def create_middle_entry_section(self):
        """
        Middle Section: 5 Entry Boxes with Live Calculation Preview:
        Total = (B&W + Color) * Rate  (0 if Total Pages == 0)
        Net   = Total - Deposit
        New Due = Previous Due + Net
        """
        entry_frame = ttk.LabelFrame(
            self.main_container,
            text="📝 ২. ডেটা এন্ট্রি ফর্ম [Total = (B&W + Color) × দর | Net = Total - জমা | New Due = আগের বাকি + Net]",
            style="Card.TLabelframe"
        )
        entry_frame.pack(fill=tk.X, pady=(0, 8))

        inner = tk.Frame(entry_frame, bg=self.COLOR_CARD)
        inner.pack(fill=tk.X, padx=5, pady=5)

        # Field 1: ১. তারিখ (Date)
        lbl_date = ttk.Label(inner, text="১. তারিখ:", style="FieldLabel.TLabel")
        lbl_date.grid(row=0, column=0, padx=(0, 4), pady=4, sticky="w")

        self.entry_date = ttk.Entry(inner, width=12, font=("Segoe UI", 10, "bold"))
        self.entry_date.grid(row=0, column=1, padx=(0, 10), pady=4, sticky="w")
        today_default = datetime.date.today().strftime("%d-%m-%Y")
        self.entry_date.insert(0, today_default)

        # Field 2: ২. B&W পেজ (B&W Pages)
        lbl_bw = ttk.Label(inner, text="২. B&W পেজ:", style="FieldLabel.TLabel")
        lbl_bw.grid(row=0, column=2, padx=(0, 4), pady=4, sticky="w")

        self.entry_bw_pages = ttk.Entry(inner, width=9, font=("Segoe UI", 10, "bold"))
        self.entry_bw_pages.grid(row=0, column=3, padx=(0, 10), pady=4, sticky="w")
        self.entry_bw_pages.insert(0, "0")
        self.entry_bw_pages.bind("<KeyRelease>", self.update_live_calculations)

        # Field 3: ৩. Color পেজ (Color Pages)
        lbl_color = ttk.Label(inner, text="৩. Color পেজ:", style="FieldLabel.TLabel")
        lbl_color.grid(row=0, column=4, padx=(0, 4), pady=4, sticky="w")

        self.entry_color_pages = ttk.Entry(inner, width=9, font=("Segoe UI", 10, "bold"))
        self.entry_color_pages.grid(row=0, column=5, padx=(0, 10), pady=4, sticky="w")
        self.entry_color_pages.insert(0, "0")
        self.entry_color_pages.bind("<KeyRelease>", self.update_live_calculations)

        # Field 4: ৪. দর (Rate)
        lbl_rate = ttk.Label(inner, text="৪. দর (৳):", style="FieldLabel.TLabel")
        lbl_rate.grid(row=0, column=6, padx=(0, 4), pady=4, sticky="w")

        self.entry_rate = ttk.Entry(inner, width=9, font=("Segoe UI", 10, "bold"))
        self.entry_rate.grid(row=0, column=7, padx=(0, 10), pady=4, sticky="w")
        self.entry_rate.insert(0, "2.00")
        self.entry_rate.bind("<KeyRelease>", self.update_live_calculations)

        # Field 5: ৫. জমা (Deposit)
        lbl_dep = ttk.Label(inner, text="৫. জমা (৳):", style="FieldLabel.TLabel")
        lbl_dep.grid(row=0, column=8, padx=(0, 4), pady=4, sticky="w")

        self.entry_deposit = ttk.Entry(inner, width=10, font=("Segoe UI", 10, "bold"))
        self.entry_deposit.grid(row=0, column=9, padx=(0, 12), pady=4, sticky="w")
        self.entry_deposit.insert(0, "0")
        self.entry_deposit.bind("<KeyRelease>", self.update_live_calculations)

        # Live calculation preview badges
        preview_box = tk.Frame(inner, bg="#f8fafc", padx=10, pady=4, bd=1, relief="solid")
        preview_box.grid(row=0, column=10, padx=(0, 8), pady=2)

        # Total Amount Preview
        tk.Label(preview_box, text="Total:", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT, padx=(2, 2))
        self.lbl_preview_total = tk.Label(preview_box, text="৳ 0.00", font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#2563eb")
        self.lbl_preview_total.pack(side=tk.LEFT, padx=(0, 8))

        # Net Amount Preview
        tk.Label(preview_box, text="Net:", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_preview_net = tk.Label(preview_box, text="৳ 0.00", font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#059669")
        self.lbl_preview_net.pack(side=tk.LEFT, padx=(0, 8))

        # New Due Preview
        tk.Label(preview_box, text="New Due:", font=("Segoe UI", 9, "bold"), bg="#f8fafc", fg="#475569").pack(side=tk.LEFT, padx=(0, 2))
        self.lbl_preview_new_due = tk.Label(preview_box, text="৳ 0.00", font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#dc2626")
        self.lbl_preview_new_due.pack(side=tk.LEFT, padx=(0, 2))

        # Action Buttons
        btn_add = ttk.Button(
            inner,
            text="💾 সেভ করুন (Enter)",
            style="Primary.TButton",
            cursor="hand2",
            command=self.save_entry_action
        )
        btn_add.grid(row=0, column=11, padx=(0, 6), pady=4)

        btn_clear_form = ttk.Button(
            inner,
            text="🔄 রিসেট (Esc)",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.clear_entry_form
        )
        btn_clear_form.grid(row=0, column=12, padx=0, pady=4)

    # ==============================================================
    # ৩. নিচের অংশ: টেবিল (Treeview) ও লেজার হিসাব
    # ==============================================================
    def create_bottom_table_section(self):
        """Bottom Section: Treeview table displaying ledger records & totals."""
        table_frame = ttk.LabelFrame(
            self.main_container,
            text="📋 ৩. বিলের আইটেম ও লেজার তালিকা (Ledger Table) - কোনো রো সিলেক্ট করে সরাসরি WhatsApp পাঠান",
            style="Card.TLabelframe"
        )
        table_frame.pack(fill=tk.BOTH, expand=True, pady=(0, 5))

        table_container = tk.Frame(table_frame, bg=self.COLOR_CARD)
        table_container.pack(fill=tk.BOTH, expand=True, padx=5, pady=4)

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
        self.tree.heading("new_due", text="নতুন Due Amount (৳)", anchor=tk.E)

        self.tree.column("sl", width=45, anchor=tk.CENTER)
        self.tree.column("date", width=105, anchor=tk.CENTER)
        self.tree.column("bw", width=90, anchor=tk.CENTER)
        self.tree.column("color", width=90, anchor=tk.CENTER)
        self.tree.column("rate", width=85, anchor=tk.E)
        self.tree.column("total_amount", width=125, anchor=tk.E)
        self.tree.column("deposit", width=105, anchor=tk.E)
        self.tree.column("net_amount", width=125, anchor=tk.E)
        self.tree.column("prev_due", width=115, anchor=tk.E)
        self.tree.column("new_due", width=135, anchor=tk.E)

        # Alternating row tag colors for sleek readability
        self.tree.tag_configure("even", background="#ffffff")
        self.tree.tag_configure("odd", background="#f8fafc")

        self.tree.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        # Summary & Actions Bar below Table
        summary_panel = tk.Frame(table_frame, bg="#f8fafc", padx=12, pady=7, bd=1, relief="solid")
        summary_panel.pack(fill=tk.X, padx=5, pady=(4, 4))

        # Left side buttons: Delete Selected, Reset All
        left_actions = tk.Frame(summary_panel, bg="#f8fafc")
        left_actions.pack(side=tk.LEFT)

        btn_remove = ttk.Button(
            left_actions,
            text="🗑️ আইটেম মুছুন (Delete)",
            style="Danger.TButton",
            cursor="hand2",
            command=self.delete_selected_item
        )
        btn_remove.pack(side=tk.LEFT, padx=(0, 10))

        btn_reset_bill = ttk.Button(
            left_actions,
            text="📄 নতুন বিল (Ctrl+N)",
            style="Secondary.TButton",
            cursor="hand2",
            command=self.reset_entire_bill
        )
        btn_reset_bill.pack(side=tk.LEFT)

        # Right side: Summary stats, WhatsApp button & Save Invoice
        right_totals = tk.Frame(summary_panel, bg="#f8fafc")
        right_totals.pack(side=tk.RIGHT)

        # Total Bill
        tk.Label(right_totals, text="সর্বমোট বিল:", font=("Segoe UI", 10), bg="#f8fafc").grid(row=0, column=0, padx=4, sticky="e")
        self.lbl_subtotal = tk.Label(right_totals, text="৳ 0.00", font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#1e293b")
        self.lbl_subtotal.grid(row=0, column=1, padx=(2, 12), sticky="w")

        # Total Deposit
        tk.Label(right_totals, text="মোট জমা:", font=("Segoe UI", 10), bg="#f8fafc").grid(row=0, column=2, padx=4, sticky="e")
        self.lbl_total_deposit_stat = tk.Label(right_totals, text="৳ 0.00", font=("Segoe UI", 10, "bold"), bg="#f8fafc", fg="#059669")
        self.lbl_total_deposit_stat.grid(row=0, column=3, padx=(2, 12), sticky="w")

        # Current Total Due
        tk.Label(right_totals, text="সর্বশেষ Due Amount:", font=("Segoe UI", 11, "bold"), bg="#f8fafc", fg="#dc2626").grid(row=0, column=4, padx=4, sticky="e")
        self.lbl_total_due_stat = tk.Label(right_totals, text="৳ 0.00", font=("Segoe UI", 11, "bold"), bg="#f8fafc", fg="#dc2626")
        self.lbl_total_due_stat.grid(row=0, column=5, padx=(2, 16), sticky="w")

        # WhatsApp Button (Bottom Location)
        btn_whatsapp_bottom = ttk.Button(
            right_totals,
            text="💬 WhatsApp-এ মেসেজ পাঠান",
            style="WhatsApp.TButton",
            cursor="hand2",
            command=self.send_whatsapp_reminder
        )
        btn_whatsapp_bottom.grid(row=0, column=6, padx=(0, 6))

        # Save Complete Invoice
        btn_save_inv = ttk.Button(
            right_totals,
            text="💾 সম্পূর্ণ বিল সংরক্ষণ (Ctrl+S)",
            style="Success.TButton",
            cursor="hand2",
            command=self.save_invoice_action
        )
        btn_save_inv.grid(row=0, column=7, padx=4)

    def create_status_bar(self):
        """Bottom-most status bar for system telemetry."""
        status_bar = tk.Frame(self.root, bg="#e2e8f0", height=26)
        status_bar.pack(side=tk.BOTTOM, fill=tk.X)

        self.status_left = tk.Label(
            status_bar,
            text="🟢 ডাটাবেস প্রস্তুত (SQLite Connected: amar_hisab.db) | হিসাব ইঞ্জিন সক্রিয়",
            font=("Segoe UI", 9),
            bg="#e2e8f0",
            fg="#047857"
        )
        self.status_left.pack(side=tk.LEFT, padx=12)

        self.status_right = tk.Label(
            status_bar,
            text="আইটেম: 0 টি",
            font=("Segoe UI", 9),
            bg="#e2e8f0",
            fg="#475569"
        )
        self.status_right.pack(side=tk.RIGHT, padx=12)

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
        self.root.bind("<Delete>", lambda e: self.delete_selected_item())
        self.root.bind("<Escape>", lambda e: self.clear_entry_form())

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
        """Re-render Treeview rows with sleek alternating row striping."""
        for row in self.tree.get_children():
            self.tree.delete(row)

        for idx, item in enumerate(self.items_list, start=1):
            tag = "even" if idx % 2 == 0 else "odd"
            self.tree.insert(
                "",
                tk.END,
                values=(
                    idx,
                    item["entry_date"],
                    item["bw_pages"],
                    item["color_pages"],
                    f"{item['rate']:,.2f}",
                    f"{item['total_amount']:,.2f}",
                    f"{item['deposit']:,.2f}",
                    f"{item['net_amount']:,.2f}",
                    f"{item['previous_due']:,.2f}",
                    f"{item['new_due']:,.2f}"
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
                text=f"📌 সিলেক্টেড রো SL-{item_vals[0]}: বকেয়া ৳ {row_due:,.2f} | WhatsApp-এ পাঠানোর জন্য প্রস্তুত",
                fg="#1e40af"
            )

    def recalculate_totals(self):
        """Recalculate total bill, deposits, and latest due."""
        total_bill = sum(item["total_amount"] for item in self.items_list)
        total_deposit = sum(item["deposit"] for item in self.items_list)

        if self.items_list:
            latest_due = self.items_list[-1]["new_due"]
        else:
            latest_due = self.current_client_previous_due

        self.lbl_subtotal.config(text=f"৳ {total_bill:,.2f}")
        self.lbl_total_deposit_stat.config(text=f"৳ {total_deposit:,.2f}")
        self.lbl_total_due_stat.config(text=f"৳ {latest_due:,.2f}")

    # ==============================================================
    # WhatsApp মেসেজ অটোমেশন (pywhatkit ইন্টিগ্রেশন)
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
            latest_due = self.items_list[-1]["new_due"]
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
            "WhatsApp মেসেজ পাঠান (pywhatkit)",
            f"গ্রাহক: {client_name}\n"
            f"WhatsApp নম্বর: {formatted_phone}\n"
            f"সর্বশেষ বকেয়া (Due): ৳ {latest_due:,.2f}\n\n"
            f"মেসেজ প্রিভিউ:\n-----------------------------------\n"
            f"{msg_preview}\n-----------------------------------\n\n"
            f"আপনি কি pywhatkit এর মাধ্যমে স্বয়ংক্রিয়ভাবে এই মেসেজটি পাঠাতে চান?"
        )
        if not confirm:
            return

        # Update telemetry
        self.status_left.config(
            text=f"⏳ {client_name} ({formatted_phone})-কে pywhatkit দিয়ে WhatsApp মেসেজ পাঠানো হচ্ছে...",
            fg="#2563eb"
        )

        # Non-blocking callback handlers
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
    # ক্লায়েন্ট ও ইনভয়েস হ্যান্ডলিং (Client & Invoice Logic)
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

            # Load previous due from database
            due_val = database.get_client_due(client["id"])
            self.current_client_previous_due = due_val

            self.entry_client_name.delete(0, tk.END)
            self.entry_client_name.insert(0, client["name"])
            self.entry_client_address.delete(0, tk.END)
            self.entry_client_address.insert(0, client["address"] or "")

            self.lbl_client_previous_due.config(text=f"৳ {due_val:,.2f}")
            self.lbl_client_status.config(
                text=f"পুরাতন ক্লায়েন্ট (ID: {client['id']}) | বাকি: ৳ {due_val:,.2f}",
                fg="#1e40af",
                bg="#dbeafe"
            )
            self.update_live_calculations()

            if not silent:
                messagebox.showinfo(
                    "ক্লায়েন্ট পাওয়া গেছে",
                    f"গ্রাহক: {client['name']}\nসর্বশেষ বকেয়া (Due): ৳ {due_val:,.2f}"
                )
            self.set_focus_and_select(self.entry_date)
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
            self.set_focus_and_select(self.entry_date)
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

        total_bill = sum(item["total_amount"] for item in self.items_list)
        total_deposit = sum(item["deposit"] for item in self.items_list)
        latest_due = self.items_list[-1]["new_due"]

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
