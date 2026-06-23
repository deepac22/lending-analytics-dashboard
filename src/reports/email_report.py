import matplotlib
matplotlib.use('Agg')
import matplotlib.pyplot as plt
import pandas as pd
import psycopg2
from pptx import Presentation
from pptx.util import Inches
from datetime import datetime
import smtplib
from email.mime.multipart import MIMEMultipart
from email.mime.base import MIMEBase
from email.mime.text import MIMEText
from email import encoders
import os
import sys

# ==========================================
# ALL CREDENTIALS COME FROM ENVIRONMENT VARIABLES
# (GitHub Secrets or your local terminal)
# ==========================================
DB_ENDPOINT = os.getenv("DB_ENDPOINT")
DB_NAME = os.getenv("DB_NAME", "lendingdb")
DB_USER = os.getenv("DB_USER", "lending_admin")
DB_PASSWORD = os.getenv("DB_PASSWORD")
SENDER_EMAIL = os.getenv("SENDER_EMAIL")
SENDER_PASSWORD = os.getenv("SENDER_PASSWORD")
RECEIVER_EMAIL = os.getenv("RECEIVER_EMAIL")
SMTP_SERVER = "smtp.gmail.com"
SMTP_PORT = 587

# Check if we have all the necessary secrets
if not all([DB_ENDPOINT, DB_PASSWORD, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL]):
    print("❌ ERROR: Missing environment variables!")
    print("Please set: DB_ENDPOINT, DB_PASSWORD, SENDER_EMAIL, SENDER_PASSWORD, RECEIVER_EMAIL")
    sys.exit(1)

print("✅ Environment variables loaded successfully.")

# ==========================================
# FUNCTION: Generate the PPT Report
# ==========================================
def generate_ppt():
    print("📊 Connecting to AWS RDS...")
    conn = psycopg2.connect(
        host=DB_ENDPOINT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        port=5432
    )
    
    query = """
        SELECT 
            p.loan_id,
            p.remaining_balance,
            p.payment_status,
            c.province,
            pr.product_type
        FROM loan_portfolio p
        JOIN clients c ON p.client_id = c.client_id
        JOIN loan_products pr ON p.product_id = pr.product_id
    """
    df = pd.read_sql(query, conn)
    conn.close()
    print(f"✅ Loaded {len(df)} records from cloud DB.")

    total_loans = len(df)
    total_value = df['remaining_balance'].sum()
    delinquent = df[df['payment_status'].isin(['90+ Days Past Due', 'Default'])]
    del_rate = (len(delinquent) / total_loans) * 100 if total_loans > 0 else 0

    prov_del = df[df['payment_status'].isin(['90+ Days Past Due', 'Default'])].groupby('province').size()
    
    fig, ax = plt.subplots(figsize=(10, 6))
    if not prov_del.empty:
        prov_del.plot(kind='bar', ax=ax, color='#d4af37')
        ax.set_title('Delinquent Loans by Province', fontsize=16)
        ax.set_ylabel('Count')
        ax.grid(axis='y', linestyle='--', alpha=0.7)
    else:
        ax.text(0.5, 0.5, 'No Delinquent Loans', ha='center', va='center')
    
    chart_path = 'data/delinquency_chart.png'
    plt.savefig(chart_path, bbox_inches='tight')
    plt.close()

    print("📁 Generating PowerPoint...")
    prs = Presentation()
    
    slide = prs.slides.add_slide(prs.slide_layouts[0])
    slide.shapes.title.text = "Lending Portfolio Health Report"
    slide.placeholders[1].text = f"Generated: {datetime.now().strftime('%Y-%m-%d %H:%M')}"

    slide = prs.slides.add_slide(prs.slide_layouts[1])
    slide.shapes.title.text = "Executive Summary"
    text_frame = slide.placeholders[1].text_frame
    text_frame.text = f"Total Active Loans: {total_loans:,}\n"
    text_frame.text += f"Total Portfolio Value: ${total_value:,.2f}\n"
    text_frame.text += f"Delinquency Rate: {del_rate:.2f}%\n"
    text_frame.text += f"At-Risk Loans: {len(delinquent)}"

    slide = prs.slides.add_slide(prs.slide_layouts[5])
    slide.shapes.title.text = "Regional Delinquency Breakdown"
    left = Inches(1)
    top = Inches(1.5)
    slide.shapes.add_picture(chart_path, left, top, width=Inches(8))

    output_ppt = 'data/Lending_Portfolio_Report.pptx'
    prs.save(output_ppt)
    print(f"✅ PPT saved to {output_ppt}")
    return output_ppt

def send_email(attachment_path):
    print("📧 Preparing to send email...")
    
    msg = MIMEMultipart()
    msg['From'] = SENDER_EMAIL
    msg['To'] = RECEIVER_EMAIL
    msg['Subject'] = f"Daily Lending Report - {datetime.now().strftime('%Y-%m-%d')}"

    body = "Attached is the daily lending portfolio health report."
    msg.attach(MIMEText(body, 'plain'))

    with open(attachment_path, "rb") as attachment:
        part = MIMEBase('application', 'octet-stream')
        part.set_payload(attachment.read())
        encoders.encode_base64(part)
        part.add_header(
            'Content-Disposition',
            f"attachment; filename= {os.path.basename(attachment_path)}",
        )
        msg.attach(part)

    server = smtplib.SMTP(SMTP_SERVER, SMTP_PORT)
    server.starttls()
    server.login(SENDER_EMAIL, SENDER_PASSWORD)
    server.sendmail(SENDER_EMAIL, RECEIVER_EMAIL, msg.as_string())
    server.quit()
    print("✅ Email sent successfully!")

if __name__ == "__main__":
    ppt_file = generate_ppt()
    send_email(ppt_file)