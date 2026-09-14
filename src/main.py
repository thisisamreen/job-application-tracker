# ============================================================
# FILE: JOB APPLICATION TRACKER (PYTHON CLI PROJECT)
# Topic: File Handling, Automation, and Job Tracking System
# WHY: Job seekers apply to many companies and lose track of
# application status. This tool stores applications, allows
# searching/filtering, exports reports, and sends reminders.
# ============================================================

# ============================================================
# EXAMPLE 1 — Real World Story
# Story: Suppose you applied to:
#
# Amazon – Data Analyst
# Google – ML Engineer
# Flipkart – Data Scientist
#
# After a week you forget:
# - Which company you applied to
# - Which role
# - When you applied
# - When to follow up
#
# This Job Tracker solves that problem.
# ============================================================


# ============================================================
# IMPORT REQUIRED LIBRARIES
# ============================================================

import csv
import os
from datetime import datetime
from difflib import SequenceMatcher
from openpyxl import Workbook
import smtplib
from email.message import EmailMessage
from dotenv import load_dotenv


# ============================================================
# FUNCTION 1 — Initialize Storage
# WHY: Ensure the data folder and CSV file exist before using
# the system.
# ============================================================

def init_file():

    # Create data folder if it does not exist
    os.makedirs("data", exist_ok=True)

    # Create CSV file if missing
    if not os.path.exists("data/jobs.csv"):

        with open("data/jobs.csv", "w", newline="") as file:
            writer = csv.writer(file)

            # CSV Header
            writer.writerow(["Company", "Role", "Location", "Status", "Date"])


# ============================================================
# HELPERS — Clean text, read rows, fuzzy match
# ============================================================

def clean(text):
    # Strip leading/trailing spaces and collapse repeated inner spaces
    return " ".join(text.split())


def read_jobs():
    # Returns (header, rows) with every cell cleaned and blank rows skipped
    with open("data/jobs.csv", "r", newline="") as file:
        reader = csv.reader(file)
        header = [clean(cell) for cell in next(reader, [])]
        rows = [[clean(cell) for cell in row] for row in reader if any(cell.strip() for cell in row)]
    return header, rows


def fuzzy_match(query, value, threshold=0.75):
    # Case-insensitive match that allows partial text ("Mann", "Trad")
    # and small spelling mistakes ("Manai", "Aplied")
    query = clean(query).lower()
    value = clean(value).lower()

    if not query:
        return False
    if query in value:
        return True
    if SequenceMatcher(None, query, value).ratio() >= threshold:
        return True

    # Compare against each word, and against word prefixes of the same length,
    # so a misspelled partial word still matches
    for word in value.split():
        if SequenceMatcher(None, query, word).ratio() >= threshold:
            return True
        if len(query) >= 3 and SequenceMatcher(None, query, word[:len(query)]).ratio() >= threshold:
            return True
    return False


def examples(rows, column, limit=5):
    # Unique existing values for a column, used as help text
    seen = []
    for row in rows:
        if len(row) > column and row[column] and row[column] not in seen:
            seen.append(row[column])
    return ", ".join(seen[:limit])


def print_job(row):
    print(f"Company: {row[0]}, Role: {row[1]}, Location: {row[2]}, Status: {row[3]}, Date: {row[4]}")


# ============================================================
# FUNCTION 2 — Add Job Application
# Story: User applied to Amazon for Data Analyst role
# ============================================================

def add_job(company, role, location, status):

    with open("data/jobs.csv", "a", newline="") as file:

        writer = csv.writer(file)

        writer.writerow([
            clean(company),
            clean(role),
            clean(location),
            clean(status),
            datetime.now().strftime("%Y-%m-%d")
        ])

    print("✅ Job added successfully")


# ============================================================
# FUNCTION 3 — View All Jobs
# ============================================================

def view_jobs():

    _, rows = read_jobs()
    print("\nYour Job Applications:")

    for row in rows:
        print_job(row)


# ============================================================
# FUNCTION 4 — Update Job Status
# Story: Amazon changed status from Applied → Interview
# ============================================================

def update_job_status():

    header, rows = read_jobs()
    print(f"(e.g. {examples(rows, 0)})")
    company_name = clean(input("Enter company name: "))
    matches = [row for row in rows if fuzzy_match(company_name, row[0])]

    if not matches:
        print("❌ Company not found")
        return

    for i, row in enumerate(matches, start=1):
        print(f"{i}. ", end="")
        print_job(row)

    if len(matches) > 1:
        pick = clean(input("Choose job number to update: "))
        if not pick.isdigit() or not 1 <= int(pick) <= len(matches):
            print("❌ Invalid choice")
            return
        target = matches[int(pick) - 1]
    else:
        target = matches[0]

    print(f"(e.g. {examples(rows, 3)})")
    target[3] = clean(input("Enter new status: "))

    with open("data/jobs.csv", "w", newline="") as file:
        writer = csv.writer(file)
        writer.writerow(header)
        writer.writerows(rows)
    print("✅ Status updated successfully")


# ============================================================
# FUNCTION 5 — Search Job
# ============================================================

def search_job():

    _, rows = read_jobs()

    print("\nSearch Job By:")
    print("1. Company Name")
    print("2. Status")

    choice = clean(input("Choose option: "))

    if choice == "1":
        print(f"Tip: partial names and small typos work. e.g. {examples(rows, 0)}")
        query = clean(input("Enter company name: "))
        matches = [row for row in rows if fuzzy_match(query, row[0])]

    elif choice == "2":
        print(f"Tip: e.g. {examples(rows, 3)}")
        query = clean(input("Enter status: "))
        # Exact status first so "Applied" doesn't also return "Not Applied Yet";
        # fall back to fuzzy matching for typos
        matches = [row for row in rows if row[3].lower() == query.lower()]
        if not matches:
            matches = [row for row in rows if fuzzy_match(query, row[3])]

    else:
        print("❌ Invalid choice")
        return

    if not matches:
        print("❌ No matching jobs found")
        return

    for row in matches:
        print_job(row)


# ============================================================
# FUNCTION 6 — Filter Jobs
# ============================================================

def filter_jobs():

    _, rows = read_jobs()

    print("\nFilter Jobs By:")
    print("1. Role")
    print("2. Location")

    option = clean(input("Choose option: "))

    if option == "1":
        print(f"Tip: e.g. {examples(rows, 1)}")
        query = clean(input("Enter role: "))
        matches = [row for row in rows if fuzzy_match(query, row[1])]

    elif option == "2":
        print(f"Tip: e.g. {examples(rows, 2)}")
        query = clean(input("Enter location: "))
        matches = [row for row in rows if fuzzy_match(query, row[2])]

    else:
        print("❌ Invalid choice")
        return

    if not matches:
        print("❌ No matching jobs found")
        return

    for row in matches:
        print_job(row)


# ============================================================
# FUNCTION 7 — Export Data to Excel
# ============================================================

def export_to_excel():

    wb = Workbook()
    ws = wb.active
    ws.title = "Job Applications"
    with open("data/jobs.csv", "r") as file:
        reader = csv.reader(file)
        for row in reader:
            ws.append(row)
    wb.save("job_applications.xlsx")
    print("✅ Exported to Excel")


# ============================================================
# FUNCTION 8 — Email Reminder
# ============================================================

def send_email_reminders():
    load_dotenv(os.path.join(os.path.dirname(os.path.abspath(__file__)), "..", ".env"))
    sender_email = (os.getenv("EMAIL_ADDRESS") or "").strip()
    # Gmail app passwords are shown with spaces; SMTP expects them removed
    sender_password = (os.getenv("EMAIL_PASSWORD") or "").replace(" ", "")

    if not sender_email or not sender_password:
        print("❌ Email credentials missing")
        return

    pending = []

    with open("data/jobs.csv", "r") as file:
        reader = csv.reader(file)
        next(reader, None)

        for row in reader:
            row = [cell.strip() for cell in row]
            if len(row) >= 4 and row[3].lower() == "applied":
                pending.append(f"{row[0]} | {row[1]} | {row[2]}")

    if not pending:
        print("No pending applications to remind about")
        return

    msg = EmailMessage()
    msg["From"] = sender_email
    msg["To"] = sender_email
    msg["Subject"] = "Job Application Reminder"
    msg.set_content("Follow up on these jobs:\n\n" + "\n".join(pending) + "\n")

    try:
        with smtplib.SMTP_SSL("smtp.gmail.com", 465, timeout=30) as server:
            server.login(sender_email, sender_password)
            server.send_message(msg)
    except smtplib.SMTPAuthenticationError:
        print("❌ Gmail rejected the login. EMAIL_PASSWORD must be a Gmail App Password "
              "(requires 2-Step Verification), not your normal password.")
        return
    except (smtplib.SMTPException, OSError) as e:
        print(f"❌ Failed to send email: {e}")
        return

    print(f"📧 Reminder email sent ({len(pending)} jobs)")


# ============================================================
# MAIN PROGRAM — CLI MENU
# ============================================================

if __name__ == "__main__":

    init_file()

    while True:

        print("\n=== Job Application Tracker ===")

        print("1 Add Job")
        print("2 View Jobs")
        print("3 Update Status")
        print("4 Search Job")
        print("5 Filter Jobs")
        print("6 Export Excel")
        print("7 Send Reminder")
        print("8 Exit")

        choice = clean(input("Choose option: "))

        if choice == "1":

            add_job(
                input("Company: "),
                input("Role: "),
                input("Location: "),
                input("Status: ")
            )

        elif choice == "2":
            view_jobs()

        elif choice == "3":
            update_job_status()

        elif choice == "4":
            search_job()

        elif choice == "5":
            filter_jobs()

        elif choice == "6":
            export_to_excel()

        elif choice == "7":
            send_email_reminders()

        elif choice == "8":
            print("Goodbye 👋")
            break

        else:
            print("❌ Invalid choice")


# ============================================================
# TIME COMPLEXITY SUMMARY
# ============================================================

# Add Job → O(1)
# View Jobs → O(n)
# Update Status → O(n)
# Search Job → O(n)
# Filter Job → O(n)
# Export Excel → O(n)

# n = number of job applications


# ============================================================
# KEY TAKEAWAYS
# ============================================================

# 1. Demonstrates Python file handling using CSV
# 2. Implements CRUD operations (Create, Read, Update, Delete)
# 3. Automates job tracking
# 4. Exports reports to Excel
# 5. Sends automated email reminders
# 6. Real-world CLI productivity tool