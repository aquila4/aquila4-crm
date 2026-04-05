from datetime import datetime

from flask import Flask, render_template, redirect, url_for, request, flash, send_file
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db, User, Sale, Commission, Marketer, Notification
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash
from flask_migrate import Migrate

from reportlab.platypus import SimpleDocTemplate, Paragraph, Spacer, Table
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from sqlalchemy import func
from io import BytesIO
from reportlab.platypus import Image
app = Flask(__name__)
app.config.from_object(Config)

# =========================
# DB INIT
# =========================
db.init_app(app)
migrate = Migrate(app, db)

# =========================
# LOGIN
# =========================
login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))

# =========================
# INIT DB
# =========================
with app.app_context():
    db.create_all()

# =========================
# LOGIN
# =========================
@app.route("/", methods=["GET", "POST"])
def login():
    if request.method == "POST":
        user = User.query.filter_by(username=request.form['username']).first()

        if user and check_password_hash(user.password, request.form['password']):
            login_user(user)
            return redirect(url_for("dashboard"))

        flash("Invalid credentials")

    return render_template("login.html")

# =========================
# LOGOUT
# =========================
@app.route("/logout")
@login_required
def logout():
    logout_user()
    return redirect(url_for("login"))

# =========================
# DASHBOARD
# =========================
@app.route("/dashboard")
@login_required
def dashboard():
    search = request.args.get("search", "")

    query = Sale.query
    if search:
        query = query.filter(Sale.client_name.contains(search))

    sales = query.all()
    commissions = Commission.query.all()

    total_sales = sum([s.amount or 0 for s in sales])
    total_commission = sum([c.amount or 0 for c in commissions])

    # notifications
    notifications = Notification.query.order_by(Notification.created_at.desc()).limit(10).all()

    # monthly data (for chart)
    results = db.session.query(
    func.to_char(Commission.created_at, 'YYYY-MM'),
    func.sum(Commission.amount)
).group_by(func.to_char(Commission.created_at, 'YYYY-MM')).all()
    months = [r[0] for r in results]
    earnings = [float(r[1]) for r in results]

    return render_template(
        "dashboard.html",
        sales=sales,
        total_sales=total_sales,
        total_commission=total_commission,
        search=search,
        notifications=notifications,
        months=months,
        earnings=earnings
    )

# =========================
# ADD SALE
# =========================
@app.route("/add_sale", methods=["GET", "POST"])
@login_required
def add_sale():

    marketer_id = request.args.get("marketer_id")
    marketers = Marketer.query.all()

    if request.method == "POST":

        client_name = request.form.get("client_name")
        sale_type = request.form.get("sale_type")

        try:
            amount = float(request.form.get("amount"))
        except:
            amount = 0

        plot_number = request.form.get("plot_number")
        land_location = request.form.get("land_location")

        form_marketer_id = request.form.get("marketer_id")

        try:
            marketer_id = int(form_marketer_id)
        except:
            marketer_id = None

        try:
            number_of_plots = int(plot_number)
        except:
            number_of_plots = 0

        sale = Sale(
            client_name=client_name,
            amount=amount,
            plot_number=plot_number,
            land_location=land_location,
            marketer_id=marketer_id,
            sale_type=sale_type
        )

        db.session.add(sale)
        db.session.commit()

        # commission
        if marketer_id and sale_type == "marketer":
            commission = Commission(
                sale_id=sale.id,
                marketer_id=marketer_id,
                amount=number_of_plots * 20000
            )

            db.session.add(commission)
            db.session.commit()

        # notification
        notification = Notification(
            message=f"New sale added: {client_name} - ₦{amount}"
        )
        db.session.add(notification)
        db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template(
        "add_sale.html",
        marketers=marketers,
        marketer_id=marketer_id
    )

@app.route("/edit_sale/<int:id>", methods=["GET", "POST"])
@login_required
def edit_sale(id):
    sale = Sale.query.get_or_404(id)

    if request.method == "POST":
        sale.client_name = request.form['client_name']
        sale.amount = float(request.form['amount'])
        sale.plot_number = request.form['plot_number']
        sale.land_location = request.form['land_location']

        db.session.commit()
        return redirect(url_for('dashboard'))

    return render_template("edit_sale.html", sale=sale)

# =========================
# DELETE SALE
# =========================
@app.route("/delete_sale/<int:id>")
@login_required
def delete_sale(id):
    sale = Sale.query.get_or_404(id)

    Commission.query.filter_by(sale_id=sale.id).delete()

    db.session.delete(sale)
    db.session.commit()

    return redirect(url_for("dashboard"))

# =========================
# MARKETER PROFILE STATS API
# =========================
@app.route("/marketer/<int:id>/stats")
def marketer_stats(id):
    commissions = Commission.query.filter_by(marketer_id=id).all()
    total = sum([c.amount or 0 for c in commissions])
    return {"total": total}

# =========================
# MARKETERS
# =========================
@app.route("/marketers")
@login_required
def marketers():
    marketers = Marketer.query.all()
    return render_template("marketers.html", marketers=marketers)

# =========================
# ADD MARKETER
# =========================
@app.route("/add_marketer", methods=["GET", "POST"])
@login_required
def add_marketer():
    if request.method == "POST":
        marketer = Marketer(
            full_name=request.form['name'],
            phone=request.form['phone'],
            email=request.form['email']
        )

        db.session.add(marketer)
        db.session.commit()

        return redirect(url_for('marketers'))

    return render_template("add_marketer.html")

# =========================
# MARKETER PROFILE
# =========================
@app.route("/marketer/<int:id>")
@login_required
def marketer_profile(id):
    marketer = Marketer.query.get_or_404(id)

    sales = Sale.query.filter_by(marketer_id=id).all()
    commissions = Commission.query.filter_by(marketer_id=id).all()

    total_sales = sum([s.amount or 0 for s in sales])
    total_commission = sum([c.amount or 0 for c in commissions])

    return render_template(
        "marketer_profile.html",
        marketer=marketer,
        sales=sales,
        total_sales=total_sales,
        total_commission=total_commission
    )

# =========================
# EDIT MARKETER
# =========================
@app.route("/edit_marketer/<int:id>", methods=["GET", "POST"])
@login_required
def edit_marketer(id):
    marketer = Marketer.query.get_or_404(id)

    if request.method == "POST":
        marketer.full_name = request.form['name']
        marketer.phone = request.form['phone']
        marketer.email = request.form['email']

        db.session.commit()

        return redirect(url_for('marketer_profile', id=marketer.id))

    return render_template("edit_marketer.html", marketer=marketer)

# =========================
# DELETE MARKETER
# =========================
@app.route("/delete_marketer/<int:id>")
@login_required
def delete_marketer(id):
    marketer = Marketer.query.get_or_404(id)

    if marketer.sales:
        return "Cannot delete marketer with sales."

    db.session.delete(marketer)
    db.session.commit()

    return redirect(url_for('marketers'))


@app.route("/marketer/<int:id>/pdf")
@login_required
def marketer_pdf(id):
    marketer = Marketer.query.get_or_404(id)

    filter_type = request.args.get("filter")  # all / month

    sales_query = Sale.query.filter_by(marketer_id=id)

    # 🔥 apply month filter
    if filter_type == "month":
        now = datetime.utcnow()
        sales_query = sales_query.filter(
            func.extract('year', Sale.created_at) == now.year,
            func.extract('month', Sale.created_at) == now.month
        )

    sales = sales_query.all()

    commissions = Commission.query.filter_by(marketer_id=id).all()

    buffer = BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    styles = getSampleStyleSheet()

    elements = []

    # Title
    elements.append(Paragraph(f"{marketer.full_name} Sales Report", styles['Title']))
    elements.append(Spacer(1, 12))

    # Table
    data = [["Client", "Amount", "Plot", "Location", "Date"]]

    for sale in sales:
        data.append([
            sale.client_name,
            f"₦{sale.amount:,.0f}",
            sale.plot_number,
            sale.land_location,
            sale.created_at.strftime('%Y-%m-%d') if sale.created_at else "—"
        ])

    table = Table(data, colWidths=[140, 80, 60, 140, 100])  # 👈 FIX WIDTH

    table.setStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 9),  # 👈 slightly bigger
    ])

    elements.append(table)

    # Totals
    total_sales = sum([s.amount or 0 for s in sales])
    total_commission = sum([c.amount or 0 for c in commissions])

    elements.append(Spacer(1, 20))
    elements.append(Paragraph(f"Total Sales: ₦{total_sales:,.0f}", styles['Normal']))
    elements.append(Paragraph(f"Total Commission: ₦{total_commission:,.0f}", styles['Normal']))

    doc.build(elements)

    buffer.seek(0)

    return send_file(
        buffer,
        as_attachment=True,
        download_name=f"{marketer.full_name}_report.pdf",
        mimetype='application/pdf'
    )

# =========================
# EXPORT PDF
# =========================

@app.route("/export/pdf")
@login_required
def export_pdf():

    filter_type = request.args.get("filter")  # all / month

    sales_query = Sale.query

    # ✅ FILTER LOGIC
    if filter_type == "month":
        now = datetime.utcnow()

        sales_query = sales_query.filter(
            func.extract('year', Sale.created_at) == now.year,
            func.extract('month', Sale.created_at) == now.month
        )

    # ✅ USE FILTERED RESULT
    sales = sales_query.all()

    filename = "report.pdf"
    doc = SimpleDocTemplate(filename, pagesize=A4)
    styles = getSampleStyleSheet()

    elements = []

    elements.append(Paragraph("Great Marcy Realty Sales", styles['Title']))
    elements.append(Spacer(1, 12))

    data = [["Client", "Amount", "Plot", "Location", "Marketer", "Date"]]

    for sale in sales:
        data.append([
            sale.client_name,
            f"₦{sale.amount:,.0f}",
            sale.plot_number,
            sale.land_location,
            sale.marketer.full_name if sale.marketer else "—",
            sale.created_at.strftime('%Y-%m-%d') if sale.created_at else "—"
        ])

    table = Table(data, colWidths=[150, 70, 50, 120, 100, 80])

    table.setStyle([
        ("BACKGROUND", (0,0), (-1,0), colors.grey),
        ("TEXTCOLOR", (0,0), (-1,0), colors.white),
        ("GRID", (0,0), (-1,-1), 1, colors.black),
        ("FONTSIZE", (0,0), (-1,-1), 8),
    ])

    elements.append(table)

    doc.build(elements)

    return send_file(filename, as_attachment=True)

# =========================
# DEFAULT ADMIN
# =========================
with app.app_context():
    if not User.query.filter_by(username="admin").first():
        admin = User(
            username="admin",
            password=generate_password_hash("admin123"),
            role="admin"
        )
        db.session.add(admin)
        db.session.commit()
        print("Admin created")

# =========================
# RUN
# =========================
if __name__ == "__main__":
    app.run(debug=True)