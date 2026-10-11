"""
Bill Generator for Amar Hisab
Generates:
  1. PDF bill (via reportlab if available, fallback HTML-to-PDF via browser)
  2. Printable HTML bill (opens in default browser)
  3. WhatsApp-ready full bill text
"""

import os
import datetime
import webbrowser
import tempfile
import urllib.parse

# ── PDF via reportlab (optional) ─────────────────────────────────
try:
    from reportlab.lib.pagesizes import A4
    from reportlab.lib import colors as rlc
    from reportlab.lib.units import cm
    from reportlab.platypus import (SimpleDocTemplate, Table, TableStyle,
                                     Paragraph, Spacer, HRFlowable)
    from reportlab.lib.styles import ParagraphStyle
    from reportlab.pdfbase import pdfmetrics
    from reportlab.pdfbase.ttfonts import TTFont
    _HAS_RL = True
except ImportError:
    _HAS_RL = False


# ═══════════════════════════════════════════════════════════════════
# HTML BILL  (always available, opens in browser for Print / Save PDF)
# ═══════════════════════════════════════════════════════════════════
def generate_html_bill(client_name: str, whatsapp: str, address: str,
                       items: list, shop_name: str = "আমার হিসাব") -> str:
    """Build a complete HTML bill string."""
    today = datetime.date.today().strftime("%d-%m-%Y")
    inv_no = f"BILL-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    total_bill    = sum(float(i.get("total_amount", 0)) for i in items)
    total_deposit = sum(float(i.get("deposit", 0))      for i in items)
    total_pages   = sum(int(i.get("bw_pages", 0)) + int(i.get("color_pages", 0)) for i in items)
    final_due     = float(items[-1]["new_due"]) if items else 0.0

    rows_html = ""
    for idx, item in enumerate(items, 1):
        net = float(item.get("net_amount", 0))
        if net < 0:
            row_bg = "#fef2f2"
            net_color = "#dc2626"
        elif net > 0:
            row_bg = "#f0fdf4"
            net_color = "#059669"
        else:
            row_bg = "#f8fafc"
            net_color = "#475569"

        rows_html += f"""
        <tr style="background:{row_bg}">
          <td style="text-align:center">{idx}</td>
          <td style="text-align:center">{item.get('entry_date','')}</td>
          <td style="text-align:center">{item.get('bw_pages',0)}</td>
          <td style="text-align:center">{item.get('color_pages',0)}</td>
          <td style="text-align:right">{float(item.get('rate',0)):,.0f}</td>
          <td style="text-align:right">{float(item.get('total_amount',0)):,.2f}</td>
          <td style="text-align:right">{float(item.get('deposit',0)):,.2f}</td>
          <td style="text-align:right;color:{net_color};font-weight:bold">{net:+,.2f}</td>
          <td style="text-align:right">{float(item.get('previous_due',0)):,.2f}</td>
          <td style="text-align:right;font-weight:bold;color:#1e40af">{float(item.get('new_due',0)):,.2f}</td>
        </tr>"""

    html = f"""<!DOCTYPE html>
<html lang="bn">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{shop_name} — {client_name} — {today}</title>
<style>
  * {{ box-sizing: border-box; margin: 0; padding: 0; }}
  body {{ font-family: 'Segoe UI', Arial, sans-serif; background: #f8fafc;
         color: #0f172a; padding: 20px; font-size: 13px; }}
  .page {{ max-width: 1050px; margin: auto; background: #fff;
           border: 1px solid #e2e8f0; border-radius: 8px;
           padding: 28px 32px; box-shadow: 0 4px 24px #0001; }}

  /* Header */
  .header {{ background: linear-gradient(135deg,#0f172a 0%,#1e3a8a 100%);
             color: #fff; border-radius: 6px; padding: 18px 24px;
             margin-bottom: 18px; }}
  .header h1 {{ font-size: 22px; letter-spacing: 1px; }}
  .header p  {{ font-size: 11px; color: #94a3b8; margin-top: 3px; }}
  .header .right {{ float: right; text-align: right; }}
  .header .right span {{ font-size: 16px; color: #38bdf8; font-weight: bold; }}

  /* Info */
  .info-grid {{ display: grid; grid-template-columns: 1fr 1fr;
                gap: 8px; margin-bottom: 18px; }}
  .info-box {{ background: #f8fafc; border: 1px solid #e2e8f0;
               border-radius: 5px; padding: 10px 14px; }}
  .info-box label {{ font-size: 10px; text-transform: uppercase;
                     letter-spacing: 0.5px; color: #64748b; }}
  .info-box .val {{ font-size: 14px; font-weight: 700; color: #0f172a; margin-top: 2px; }}

  /* Table */
  table {{ width: 100%; border-collapse: collapse; margin-bottom: 18px; }}
  th {{ background: #1e293b; color: #fff; font-size: 11px;
        padding: 8px 6px; text-align: center; }}
  td {{ font-size: 12px; padding: 6px 6px; border-bottom: 1px solid #f1f5f9; }}
  tr:hover td {{ background: #eff6ff !important; }}

  /* Summary */
  .summary {{ display: grid; grid-template-columns: repeat(3,1fr);
              gap: 12px; margin-bottom: 18px; }}
  .sum-card {{ border-radius: 6px; padding: 12px 16px; text-align: center; }}
  .sum-card label {{ font-size: 10px; text-transform: uppercase;
                     letter-spacing: 0.5px; display: block; margin-bottom: 4px; }}
  .sum-card .amount {{ font-size: 18px; font-weight: 800; }}
  .card-blue  {{ background:#dbeafe; color:#1e3a8a; }}
  .card-green {{ background:#d1fae5; color:#064e3b; }}
  .card-red   {{ background:#fee2e2; color:#7f1d1d; }}

  /* Footer */
  .footer {{ border-top: 2px solid #e2e8f0; padding-top: 12px;
             color: #94a3b8; font-size: 11px; text-align: center; }}

  /* Print */
  @media print {{
    body {{ background: white; padding: 0; }}
    .page {{ box-shadow: none; border: none; }}
    .no-print {{ display: none !important; }}
    @page {{ margin: 1cm; size: A4; }}
  }}
</style>
</head>
<body>
<div class="page">

  <!-- Print button (hidden on print) -->
  <div class="no-print" style="text-align:right;margin-bottom:12px">
    <button onclick="window.print()"
      style="background:#2563eb;color:#fff;border:none;padding:8px 18px;
             border-radius:5px;font-size:13px;cursor:pointer;margin-right:8px">
      🖨️ প্রিন্ট করুন
    </button>
    <button onclick="window.close()"
      style="background:#475569;color:#fff;border:none;padding:8px 14px;
             border-radius:5px;font-size:13px;cursor:pointer">
      ✕ বন্ধ করুন
    </button>
  </div>

  <!-- Header -->
  <div class="header">
    <div class="right">
      <span>৳ {final_due:,.2f}</span><br>
      <small style="color:#94a3b8">সর্বশেষ বাকি</small>
    </div>
    <h1>⚡ {shop_name}</h1>
    <p>Professional Billing &amp; Ledger | ডিজিটাল হিসাব সিস্টেম</p>
  </div>

  <!-- Client Info -->
  <div class="info-grid">
    <div class="info-box">
      <label>গ্রাহকের নাম</label>
      <div class="val">{client_name}</div>
    </div>
    <div class="info-box">
      <label>WhatsApp নম্বর</label>
      <div class="val">{whatsapp}</div>
    </div>
    <div class="info-box">
      <label>ঠিকানা</label>
      <div class="val">{address or '—'}</div>
    </div>
    <div class="info-box">
      <label>বিল নং | তারিখ</label>
      <div class="val">{inv_no} | {today}</div>
    </div>
  </div>

  <!-- Ledger Table -->
  <table>
    <thead>
      <tr>
        <th>SL</th><th>তারিখ</th><th>B&amp;W</th><th>Color</th>
        <th>দর (৳)</th><th>Total (৳)</th><th>জমা (৳)</th>
        <th>Net (৳)</th><th>আগের বাকি</th><th>নতুন Due (৳)</th>
      </tr>
    </thead>
    <tbody>
      {rows_html}
    </tbody>
  </table>

  <!-- Summary Cards -->
  <div class="summary">
    <div class="sum-card card-blue">
      <label>সর্বমোট বিল</label>
      <div class="amount">৳ {total_bill:,.2f}</div>
      <small>মোট {total_pages} পেজ</small>
    </div>
    <div class="sum-card card-green">
      <label>মোট জমা</label>
      <div class="amount">৳ {total_deposit:,.2f}</div>
    </div>
    <div class="sum-card card-red">
      <label>সর্বশেষ বাকি (Due)</label>
      <div class="amount">৳ {final_due:,.2f}</div>
    </div>
  </div>

  <div class="footer">
    এই বিলটি '{shop_name}' বিলিং সিস্টেম দ্বারা স্বয়ংক্রিয়ভাবে তৈরি হয়েছে। তারিখ: {today}
  </div>
</div>
</body>
</html>"""
    return html


def open_html_bill_in_browser(client_name: str, whatsapp: str, address: str,
                               items: list, shop_name: str = "আমার হিসাব") -> str:
    """
    Save HTML bill to a temp file and open in default browser.
    Returns the temp file path.
    """
    html = generate_html_bill(client_name, whatsapp, address, items, shop_name)
    safe = "".join(c for c in client_name if c.isalnum() or c in " _-")[:20]
    ts   = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"Bill_{safe}_{ts}.html"
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)
    with open(fpath, "w", encoding="utf-8") as f:
        f.write(html)
    webbrowser.open(f"file:///{fpath.replace(os.sep, '/')}")
    return fpath


# ═══════════════════════════════════════════════════════════════════
# PDF via reportlab
# ═══════════════════════════════════════════════════════════════════
def generate_pdf_bill(client_name: str, whatsapp: str, address: str,
                      items: list, shop_name: str = "আমার হিসাব") -> str:
    """
    Generate PDF using reportlab.
    Returns the saved file path.
    Raises RuntimeError if reportlab not installed.
    """
    if not _HAS_RL:
        raise RuntimeError(
            "reportlab ইনস্টল নেই।\n"
            "কমান্ড দিন: pip install reportlab\n\n"
            "বিকল্প: HTML বিল ব্রাউজারে খুলুন → Print → Save as PDF"
        )

    safe  = "".join(c for c in client_name if c.isalnum() or c in " _-")[:24]
    ts    = datetime.datetime.now().strftime("%Y%m%d_%H%M%S")
    fname = f"Bill_{safe}_{ts}.pdf"
    fpath = os.path.join(os.path.dirname(os.path.abspath(__file__)), fname)

    # ── font: try Kalpurush (Bengali), fallback Helvetica ────────
    font_name = "Helvetica"
    kfont = os.path.join(os.path.dirname(os.path.abspath(__file__)), "Kalpurush.ttf")
    if os.path.exists(kfont):
        try:
            pdfmetrics.registerFont(TTFont("Kalpurush", kfont))
            font_name = "Kalpurush"
        except Exception:
            pass

    doc = SimpleDocTemplate(fpath, pagesize=A4,
                            leftMargin=1.5*cm, rightMargin=1.5*cm,
                            topMargin=1.5*cm, bottomMargin=1.5*cm)

    DARK  = rlc.HexColor("#0f172a")
    BLUE  = rlc.HexColor("#2563eb")
    LBLUE = rlc.HexColor("#dbeafe")
    GREEN = rlc.HexColor("#d1fae5")
    RED   = rlc.HexColor("#fee2e2")
    LGRAY = rlc.HexColor("#f8fafc")
    MGRAY = rlc.HexColor("#e2e8f0")
    WHITE = rlc.white

    def _p(txt, fn=font_name, fs=9, color=DARK, align=0, bold=False):
        fn_use = fn
        return Paragraph(
            f"<b>{txt}</b>" if bold else txt,
            ParagraphStyle("_", fontName=fn_use, fontSize=fs,
                           textColor=color, alignment=align, leading=fs+3)
        )

    story = []
    today = datetime.date.today().strftime("%d-%m-%Y")
    inv_no = f"BILL-{datetime.datetime.now().strftime('%Y%m%d%H%M%S')}"

    # Header table
    hdr_data = [[
        _p(f"⚡ {shop_name}", fs=16, bold=True),
        _p(f"বিল নং: {inv_no}\nতারিখ: {today}", fs=8, align=2)
    ]]
    hdr_tbl = Table(hdr_data, colWidths=["65%","35%"])
    hdr_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), DARK),
        ("TEXTCOLOR", (0,0),(-1,-1), WHITE),
        ("TOPPADDING",(0,0),(-1,-1), 8),
        ("BOTTOMPADDING",(0,0),(-1,-1), 8),
        ("LEFTPADDING",(0,0),(-1,-1),14),
        ("RIGHTPADDING",(0,0),(-1,-1),14),
    ]))
    story.append(hdr_tbl)
    story.append(Spacer(1, 6))

    # Client info
    info_data = [[
        _p(f"<b>গ্রাহক:</b> {client_name}", fs=9),
        _p(f"<b>WhatsApp:</b> {whatsapp}", fs=9),
        _p(f"<b>ঠিকানা:</b> {address or '—'}", fs=9),
    ]]
    info_tbl = Table(info_data, colWidths=["35%","30%","35%"])
    info_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(-1,-1), LGRAY),
        ("BOX",(0,0),(-1,-1),0.5,MGRAY),
        ("INNERGRID",(0,0),(-1,-1),0.3,MGRAY),
        ("TOPPADDING",(0,0),(-1,-1),5),
        ("BOTTOMPADDING",(0,0),(-1,-1),5),
        ("LEFTPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(info_tbl)
    story.append(Spacer(1, 8))

    # Ledger table
    col_w = [0.7*cm,2.1*cm,1.3*cm,1.3*cm,1.5*cm,1.9*cm,1.7*cm,1.9*cm,2.0*cm,2.1*cm]
    headers = ["SL","তারিখ","B&W","Color","দর","Total","জমা","Net","আগের বাকি","নতুন Due"]
    tbl_data = [[_p(h, fs=8, bold=True) for h in headers]]

    for idx, item in enumerate(items, 1):
        net = float(item.get("net_amount", 0))
        bg  = RED if net < 0 else (GREEN if net > 0 else WHITE)
        tbl_data.append([
            _p(str(idx), fs=8, align=1),
            _p(item.get("entry_date",""), fs=8, align=1),
            _p(str(item.get("bw_pages",0)), fs=8, align=1),
            _p(str(item.get("color_pages",0)), fs=8, align=1),
            _p(f"{float(item.get('rate',0)):,.0f}", fs=8, align=2),
            _p(f"{float(item.get('total_amount',0)):,.2f}", fs=8, align=2),
            _p(f"{float(item.get('deposit',0)):,.2f}", fs=8, align=2),
            _p(f"{net:+,.2f}", fs=8, align=2, color=rlc.HexColor("#dc2626") if net<0 else rlc.HexColor("#059669")),
            _p(f"{float(item.get('previous_due',0)):,.2f}", fs=8, align=2),
            _p(f"{float(item.get('new_due',0)):,.2f}", fs=8, align=2, bold=True, color=BLUE),
        ])

    ledger = Table(tbl_data, colWidths=col_w, repeatRows=1)
    tbl_style = [
        ("BACKGROUND",(0,0),(-1,0), DARK),
        ("TEXTCOLOR", (0,0),(-1,0), WHITE),
        ("ALIGN",     (0,0),(-1,-1),"CENTER"),
        ("FONTSIZE",  (0,0),(-1,-1), 8),
        ("TOPPADDING",(0,0),(-1,-1), 3),
        ("BOTTOMPADDING",(0,0),(-1,-1), 3),
        ("LEFTPADDING",(0,0),(-1,-1), 3),
        ("RIGHTPADDING",(0,0),(-1,-1), 3),
        ("BOX",(0,0),(-1,-1),0.5, MGRAY),
        ("INNERGRID",(0,0),(-1,-1),0.3, MGRAY),
    ]
    for idx, item in enumerate(items, 1):
        net = float(item.get("net_amount", 0))
        bg  = RED if net < 0 else (GREEN if net > 0 else (LGRAY if idx%2==0 else WHITE))
        tbl_style.append(("BACKGROUND",(0,idx),(-1,idx), bg))
    ledger.setStyle(TableStyle(tbl_style))
    story.append(ledger)
    story.append(Spacer(1, 10))

    # Summary
    total_bill    = sum(float(i.get("total_amount",0)) for i in items)
    total_deposit = sum(float(i.get("deposit",0))      for i in items)
    total_pages   = sum(int(i.get("bw_pages",0))+int(i.get("color_pages",0)) for i in items)
    final_due     = float(items[-1]["new_due"]) if items else 0.0

    sum_data = [[
        _p(f"সর্বমোট বিল\n৳ {total_bill:,.2f}", fs=10, bold=True, align=1),
        _p(f"মোট জমা\n৳ {total_deposit:,.2f}", fs=10, bold=True, align=1),
        _p(f"সর্বশেষ Due\n৳ {final_due:,.2f}", fs=10, bold=True, align=1,
           color=rlc.HexColor("#dc2626")),
        _p(f"মোট পেজ\n{total_pages}", fs=10, bold=True, align=1),
    ]]
    sum_tbl = Table(sum_data, colWidths=["25%","25%","25%","25%"])
    sum_tbl.setStyle(TableStyle([
        ("BACKGROUND",(0,0),(0,0), LBLUE),
        ("BACKGROUND",(1,0),(1,0), GREEN),
        ("BACKGROUND",(2,0),(2,0), RED),
        ("BACKGROUND",(3,0),(3,0), LGRAY),
        ("BOX",(0,0),(-1,-1),0.5,MGRAY),
        ("INNERGRID",(0,0),(-1,-1),0.5,MGRAY),
        ("TOPPADDING",(0,0),(-1,-1),8),
        ("BOTTOMPADDING",(0,0),(-1,-1),8),
    ]))
    story.append(sum_tbl)
    story.append(Spacer(1, 10))
    story.append(HRFlowable(width="100%", thickness=1, color=MGRAY))
    story.append(Spacer(1, 4))
    story.append(_p(f"এই বিলটি '{shop_name}' সিস্টেম দ্বারা তৈরি। তারিখ: {today}",
                    fs=8, color=rlc.HexColor("#94a3b8"), align=1))

    doc.build(story)
    return fpath


# ═══════════════════════════════════════════════════════════════════
# WhatsApp full bill text
# ═══════════════════════════════════════════════════════════════════
def generate_whatsapp_bill_text(client_name: str, items: list,
                                 shop_name: str = "আমার হিসাব") -> str:
    """Generate a compact WhatsApp-friendly full bill message."""
    today      = datetime.date.today().strftime("%d-%m-%Y")
    total_bill = sum(float(i.get("total_amount",0)) for i in items)
    total_dep  = sum(float(i.get("deposit",0))      for i in items)
    final_due  = float(items[-1]["new_due"]) if items else 0.0

    lines = [
        f"আসসালামু আলাইকুম {client_name},",
        f"",
        f"*{shop_name}* — পূর্ণ হিসাব বিবরণী",
        f"তারিখ: {today}",
        f"─────────────────────",
    ]
    for idx, item in enumerate(items, 1):
        net = float(item.get("net_amount", 0))
        sign = "✅" if net <= 0 else "📄"
        lines.append(
            f"{sign} {idx}. {item.get('entry_date','')} | "
            f"B&W:{item.get('bw_pages',0)} Color:{item.get('color_pages',0)} | "
            f"Total:৳{float(item.get('total_amount',0)):,.0f} | "
            f"জমা:৳{float(item.get('deposit',0)):,.0f} | "
            f"Due:৳{float(item.get('new_due',0)):,.0f}"
        )
    lines += [
        f"─────────────────────",
        f"📊 সর্বমোট বিল: ৳ {total_bill:,.2f}",
        f"💰 মোট জমা:    ৳ {total_dep:,.2f}",
        f"🔴 সর্বশেষ বাকি: *৳ {final_due:,.2f}*",
        f"",
        f"অনুগ্রহ করে সুবিধামতো বকেয়া পরিশোধ করুন।",
        f"ধন্যবাদ! 🙏",
    ]
    return "\n".join(lines)


def send_full_bill_whatsapp(phone: str, client_name: str, items: list,
                             shop_name: str = "আমার হিসাব"):
    """Open WhatsApp Web with the full bill text pre-filled."""
    from whatsapp_sender import format_phone_number
    formatted = format_phone_number(phone)
    text = generate_whatsapp_bill_text(client_name, items, shop_name)
    encoded = urllib.parse.quote(text)
    url = f"https://web.whatsapp.com/send?phone={formatted}&text={encoded}"
    webbrowser.open(url)
    return formatted
