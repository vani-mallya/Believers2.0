import tkinter as tk
from tkinter import messagebox
import sqlite3
import csv
import os

# ================= FILES =================
SKILLS_FILE = "skills_db.csv"
VACANCIES_FILE = "vacancies_db.csv"

# ================= DATABASE =================
conn = sqlite3.connect("")
c = conn.cursor()

c.execute("DROP TABLE IF EXISTS users")
c.execute("""
CREATE TABLE users(
    name TEXT,
    email TEXT UNIQUE,
    password TEXT,
    age INTEGER,
    location TEXT,
    yearly_income INTEGER
)
""")
conn.commit()

# ================= WINDOW =================
root = tk.Tk()
root.title("EmpowHer")
root.attributes("-fullscreen", True)
root.bind("<Escape>", lambda e: root.attributes("-fullscreen", False))

BG = "#F4F6FB"
root.configure(bg=BG)

# ================= FONTS =================
FONT_WELCOME = ("DejaVu Sans", 42, "bold")
FONT_SUBTITLE = ("DejaVu Sans", 24)
FONT_CARD = ("DejaVu Sans", 20, "bold")
FONT_ENTRY = ("DejaVu Sans", 18)
FONT_TITLE = ("DejaVu Sans", 34, "bold")

current_user = None

# ================= HELPERS =================
def clear():
    for w in root.winfo_children():
        w.destroy()

def entry(parent, placeholder="", show=None):
    e = tk.Entry(parent, font=FONT_ENTRY, show=show, justify="center")
    e.insert(0, placeholder)
    return e

# ================= ROUNDED CARD =================
def rounded_card(parent, text, bg, command):
    W, H, R = 300, 210, 30
    canvas = tk.Canvas(parent, width=W, height=H, bg=BG, highlightthickness=0)

    def rr(x1, y1, x2, y2, r):
        canvas.create_arc(x1, y1, x1+r*2, y1+r*2, start=90, extent=90, fill=bg, outline=bg)
        canvas.create_arc(x2-r*2, y1, x2, y1+r*2, start=0, extent=90, fill=bg, outline=bg)
        canvas.create_arc(x2-r*2, y2-r*2, x2, y2, start=270, extent=90, fill=bg, outline=bg)
        canvas.create_arc(x1, y2-r*2, x1+r*2, y2, start=180, extent=90, fill=bg, outline=bg)
        canvas.create_rectangle(x1+r, y1, x2-r, y2, fill=bg, outline=bg)
        canvas.create_rectangle(x1, y1+r, x2, y2-r, fill=bg, outline=bg)

    rr(8, 8, W-8, H-8, R)

    canvas.create_text(
        W//2, H//2,
        text=text,
        fill="white",
        font=FONT_CARD,
        width=240,
        justify="center"
    )

    canvas.bind("<Button-1>", lambda e: command())
    return canvas

# ================= BUYER PAGE =================
def buyer_page():
    clear()

    tk.Label(root, text="Buy Products", font=FONT_TITLE, bg=BG).pack(pady=10)
    tk.Label(root, text="Select the item you want to purchase", font=FONT_SUBTITLE, bg=BG).pack(pady=10)

    with open("items_db.csv", newline="", encoding="utf-8") as f:
        items = list(csv.DictReader(f))

    item_var = tk.StringVar(value=items[0]["item_name"])
    opt = tk.OptionMenu(root, item_var, *[i["item_name"] for i in items])
    opt.config(font=("DejaVu Sans", 16), width=30)
    opt.pack(pady=10)

    output = tk.Text(root, height=14, width=90, font=("DejaVu Sans", 15), bd=0, padx=20, pady=20)
    output.pack(pady=20)

    def show_shops():
        output.delete("1.0", tk.END)
        with open("item_shops.csv", newline="", encoding="utf-8") as f:
            shops = [s for s in csv.DictReader(f) if s["item_name"] == item_var.get()]

        if not shops:
            output.insert(tk.END, "No shops found for this item.")
        else:
            for s in shops:
                output.insert(
                    tk.END,
                    f"Shop: {s['shop_name']}\n"
                    f"Location: {s['location']}\n"
                    f"Price: ₹{s['price']}\n"
                    "--------------------------------------\n\n"
                )

    tk.Button(root, text="View Nearby Shops", font=FONT_CARD, height=2, command=show_shops).pack()
    tk.Button(root, text="Back", font=FONT_SUBTITLE, bg=BG, bd=0,
              command=lambda: dashboard(current_user)).pack(pady=10)

# ================= JOB SEARCH =================
def job_search_page():
    clear()

    tk.Label(root, text="Job Search", font=FONT_TITLE, bg=BG).pack(pady=10)
    tk.Label(root, text="Select your skill", font=FONT_SUBTITLE, bg=BG).pack(pady=10)

    with open(SKILLS_FILE, newline="", encoding="utf-8") as f:
        skills = [r["skill_name"] for r in csv.DictReader(f)]

    skill_var = tk.StringVar(value=skills[0])
    tk.OptionMenu(root, skill_var, *skills).pack()

    output = tk.Text(root, height=16, width=90, font=("DejaVu Sans", 15), bd=0)
    output.pack(pady=20)

    def show_jobs():
        output.delete("1.0", tk.END)
        found = False
        with open(VACANCIES_FILE, newline="", encoding="utf-8") as f:
            for job in csv.DictReader(f):
                if job["skill_required"] == skill_var.get():
                    found = True
                    output.insert(
                        tk.END,
                        f"Job: {job['job_title']}\n"
                        f"Employer: {job['employer_name']}\n"
                        f"Location: {job['location']}\n"
                        f"Salary: ₹{job['salary_per_month']}\n"
                        "--------------------------------------\n\n"
                    )
        if not found:
            output.insert(tk.END, "No vacancies found.")

    tk.Button(root, text="Show Vacancies", font=FONT_CARD, height=2, command=show_jobs).pack()
    tk.Button(root, text="Back", font=FONT_SUBTITLE, bg=BG, bd=0,
              command=lambda: dashboard(current_user)).pack(pady=10)
# ================= RECRUITER =================
def recruiter_page():
    clear()

    tk.Label(root, text="Recruiter Dashboard", font=FONT_TITLE, bg=BG).pack(pady=10)
    tk.Label(root, text="Post a Job Vacancy", font=FONT_SUBTITLE, bg=BG).pack(pady=10)

    with open(SKILLS_FILE, newline="", encoding="utf-8") as f:
        skills = [r["skill_name"] for r in csv.DictReader(f)]

    skill_var = tk.StringVar(value=skills[0])
    tk.OptionMenu(root, skill_var, *skills).pack(pady=5)

    fields = {}
    for label in ["Job Title", "Location", "Monthly Salary", "Employer Name"]:
        tk.Label(root, text=label, font=("DejaVu Sans", 16), bg=BG).pack()
        e = tk.Entry(root, font=FONT_ENTRY)
        e.pack(pady=5)
        fields[label] = e

    def post_job():
        with open(VACANCIES_FILE, newline="", encoding="utf-8") as f:
            rows = list(csv.reader(f))
            next_id = len(rows)

        with open(VACANCIES_FILE, "a", newline="", encoding="utf-8") as f:
            csv.writer(f).writerow([
                next_id,
                skill_var.get(),
                fields["Job Title"].get(),
                fields["Location"].get(),
                fields["Monthly Salary"].get(),
                fields["Employer Name"].get()
            ])

        messagebox.showinfo("Success", "Vacancy posted")
        dashboard(current_user)

    tk.Button(root, text="Post Vacancy", font=FONT_CARD, height=2, command=post_job).pack(pady=10)
    tk.Button(root, text="Back", font=FONT_SUBTITLE, bg=BG, bd=0,
              command=lambda: dashboard(current_user)).pack()
    
# ================= Financial page: =================
def financial_help_page():
    clear()

    tk.Label(
        root,
        text="Financial Support Services",
        font=FONT_TITLE,
        bg=BG
    ).pack(pady=20)

    tk.Label(
        root,
        text="Choose how you would like to participate",
        font=FONT_SUBTITLE,
        bg=BG
    ).pack(pady=10)

    container = tk.Frame(root, bg=BG)
    container.pack(expand=True)

    tk.Button(
        container,
        text="Lender\nSupport Women Entrepreneurs",
        font=FONT_CARD,
        width=28,
        height=4,
        command=lender_page
    ).grid(row=0, column=0, padx=40, pady=30)

    tk.Button(
        container,
        text="Debt Seeker\nRequest Financial Assistance",
        font=FONT_CARD,
        width=28,
        height=4,
        command=debt_seeker_page
    ).grid(row=0, column=1, padx=40, pady=30)

    # ✅ FIXED BACK BUTTON
    tk.Button(
        root,
        text="Back",
        font=FONT_SUBTITLE,
        bg=BG,
        bd=0,
        command=lambda: dashboard(current_user)
    ).pack(pady=20)

# ================= Dept Seeker =================
def debt_seeker_page():
    clear()

    card = tk.Frame(root, bg="white")
    card.pack(padx=300, pady=40, fill="x")

    tk.Label(
        card,
        text="Request Financial Assistance",
        font=FONT_TITLE,
        bg="white"
    ).pack(pady=20)

    fields = {}

    def add_field(label):
        tk.Label(
            card,
            text=label,
            font=("DejaVu Sans", 16),
            bg="white",
            anchor="w"
        ).pack(fill="x", padx=40, pady=(8, 2))

        e = tk.Entry(card, font=FONT_ENTRY)
        e.pack(fill="x", padx=40, pady=(0, 8), ipady=8)
        fields[label] = e

    add_field("Purpose of Loan (Job / Business / Skill)")
    add_field("Amount Required (₹)")
    add_field("Expected Monthly Income (₹)")
    add_field("Repayment Period (months)")
    add_field("Short Description")

    def submit_request():
        try:
            with open("financial_requests.csv", "a", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow([
                    fields["Purpose of Loan (Job / Business / Skill)"].get(),
                    fields["Amount Required (₹)"].get(),
                    fields["Expected Monthly Income (₹)"].get(),
                    fields["Repayment Period (months)"].get(),
                    fields["Short Description"].get()
                ])

            messagebox.showinfo("Success", "Your request has been submitted")
            financial_help_page()

        except:
            messagebox.showerror("Error", "Please check your inputs")

    tk.Button(
        card,
        text="Submit Request",
        font=FONT_CARD,
        height=2,
        command=submit_request
    ).pack(pady=20)

    tk.Button(
        card,
        text="Back",
        font=FONT_SUBTITLE,
        bg="white",
        bd=0,
        command=financial_help_page
    ).pack(pady=(0, 20))
# ================= Lender page =================
def lender_page():
    clear()

    tk.Label(
        root,
        text="Active Financial Requests",
        font=FONT_TITLE,
        bg=BG
    ).pack(pady=20)

    output = tk.Text(
        root,
        height=18,
        width=100,
        font=("DejaVu Sans", 14),
        bd=0
    )
    output.pack(pady=20)

    try:
        with open("financial_requests.csv", newline="", encoding="utf-8") as f:
            reader = csv.reader(f)
            next(reader)  # skip header
            found = False

            for row in reader:
                found = True
                output.insert(
                    tk.END,
                    f"Purpose: {row[0]}\n"
                    f"Amount Required: ₹{row[1]}\n"
                    f"Expected Monthly Income: ₹{row[2]}\n"
                    f"Repayment Period: {row[3]} months\n"
                    f"Description: {row[4]}\n"
                    "--------------------------------------------\n\n"
                )

            if not found:
                output.insert(tk.END, "No financial requests available at the moment.")

    except FileNotFoundError:
        output.insert(tk.END, "No financial requests available.")

    tk.Button(
        root,
        text="Back",
        font=FONT_SUBTITLE,
        bg=BG,
        bd=0,
        command=financial_help_page
    ).pack(pady=20)


# ================= SCHEMES =================
def schemes_page():
    clear()
    tk.Label(root, text="Government Schemes", font=FONT_TITLE, bg=BG).pack(pady=10)

    with open("schemes.csv", newline="", encoding="utf-8") as f:
        for row in csv.reader(f):
            tk.Label(root, text=" | ".join(row),
                     font=("DejaVu Sans", 14), bg=BG).pack(anchor="w", padx=40)

    tk.Button(root, text="Back", font=FONT_SUBTITLE, bg=BG, bd=0,
              command=lambda: dashboard(current_user)).pack(pady=10)

# ================= DASHBOARD =================
def dashboard(username):
    global current_user
    current_user = username
    clear()

    tk.Label(root, text=f"Welcome {username}", font=FONT_WELCOME, bg=BG).pack(pady=10)
    tk.Label(root, text="Select your service", font=FONT_SUBTITLE, bg=BG).pack(pady=10)

    services = [
        ("Buy Products", "#5B5BD6", buyer_page),
        ("Recruiter", "#E67E22", recruiter_page),
        ("Sell Products", "#27AE60", lambda: messagebox.showinfo("Info", "Coming Soon")),
        ("Job Search", "#C0392B", job_search_page),
        ("Financial Help", "#2980B9", financial_help_page),
        ("Government Schemes", "#8E44AD", schemes_page),
    ]

    grid = tk.Frame(root, bg=BG)
    grid.pack(expand=True, fill="both", padx=80)

    for c in range(3):
        grid.columnconfigure(c, weight=1)
    for r in range(2):
        grid.rowconfigure(r, weight=1)

    for i, (t, col, cmd) in enumerate(services):
        rounded_card(grid, t, col, cmd).grid(row=i//3, column=i%3, padx=35, pady=30)

    tk.Button(root, text="Logout", font=("DejaVu Sans", 16),
              bg=BG, bd=0, command=language_page).pack(pady=10)





# ================= AUTH FLOW =================
def language_page():
    clear()
    tk.Label(root, text="Choose Language", font=FONT_TITLE, bg=BG).pack(pady=40)
    tk.Button(root, text="English", font=FONT_CARD, height=2, command=welcome_page).pack()

def welcome_page():
    clear()
    tk.Label(root, text="EmpowHer", font=FONT_TITLE, bg=BG).pack(pady=30)
    tk.Button(root, text="Create Account", font=FONT_CARD, command=signup_page).pack(pady=10)
    tk.Button(root, text="Login", font=FONT_CARD, command=login_page).pack()

def signup_page():
    clear()

    card = tk.Frame(root, bg="white")
    card.pack(pady=30, padx=300, fill="x")

    tk.Label(card, text="Create Account",
             font=FONT_TITLE, bg="white").pack(pady=20)

    fields = {}

    def add_field(label, show=None):
        tk.Label(card, text=label,
                 font=("DejaVu Sans", 16),
                 bg="white", anchor="w"
        ).pack(fill="x", padx=40, pady=(6, 2))

        e = tk.Entry(card, font=FONT_ENTRY, show=show)
        e.pack(fill="x", padx=40, pady=(0, 8), ipady=8)
        fields[label] = e

    add_field("Name")
    add_field("Email")
    add_field("Password", show="*")
    add_field("Age")
    add_field("Location")
    add_field("Yearly Income")

    def register():
        try:
            c.execute(
                "INSERT INTO users VALUES (?,?,?,?,?,?)",
                (
                    fields["Name"].get().strip(),
                    fields["Email"].get().strip().lower(),
                    fields["Password"].get().strip(),
                    int(fields["Age"].get()),
                    fields["Location"].get().strip(),
                    int(fields["Yearly Income"].get())
                )
            )
            conn.commit()
            messagebox.showinfo("Success", "Account created!")
            login_page()
        except sqlite3.IntegrityError:
            messagebox.showerror("Error", "This email is already registered")
        except ValueError:
            messagebox.showerror("Error", "Age and income must be numbers")

    # ✅ THIS BUTTON WILL ALWAYS BE VISIBLE NOW
    tk.Button(
        card,
        text="Create Account",
        font=FONT_CARD,
        height=2,
        command=register
    ).pack(pady=20)

    tk.Button(
        card,
        text="Back",
        font=FONT_SUBTITLE,
        bg="white",
        bd=0,
        command=welcome_page
    ).pack(pady=(0, 20))



            
def login_page():
    clear()
    tk.Label(root, text="Login", font=FONT_TITLE, bg=BG).pack(pady=20)

    email = entry(root, "Phone or Email")
    password = entry(root, "Password", show="*")

    email.pack(fill="x", padx=350, pady=10, ipady=10)
    password.pack(fill="x", padx=350, pady=10, ipady=10)

    def login():
        c.execute("SELECT name FROM users WHERE email=? AND password=?",
                  (email.get(), password.get()))
        user = c.fetchone()
        if user:
            dashboard(user[0])
        else:
            messagebox.showerror("Error", "Wrong details")

    tk.Button(root, text="Login", font=FONT_CARD, command=login).pack(pady=10)
    tk.Button(root, text="Back", font=FONT_SUBTITLE, bg=BG, bd=0, command=welcome_page).pack()

# ================= START =================
language_page()
root.mainloop()



