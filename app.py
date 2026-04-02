from flask import Flask, render_template, redirect, url_for, request, flash
from flask_login import LoginManager, login_user, login_required, logout_user, current_user
from models import db
from config import Config
from werkzeug.security import generate_password_hash, check_password_hash

app = Flask(__name__)
app.config.from_object(Config)

db.init_app(app)
from models import User, Sale, Commission

# ⬇️ IMPORT MODELS HERE (VERY IMPORTANT)
from models import User, Sale, Commission

login_manager = LoginManager()
login_manager.init_app(app)
login_manager.login_view = "login"

# Load user
@login_manager.user_loader
def load_user(user_id):
    return db.session.get(User, int(user_id))
    
# Initialize DB
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

    return render_template(
        "dashboard.html",
        sales=sales,
        total_sales=total_sales,
        total_commission=total_commission,
        search=search
    )
# =========================
# ADD SALE
# =========================

@app.route("/add_sale", methods=["GET", "POST"])
@login_required
def add_sale():

    # ✅ Only admin allowed
    if current_user.role != "admin":
        return "Unauthorized", 403

    if request.method == "POST":

        sale_type = request.form.get('sale_type')

        client_name = request.form.get("client_name")
        amount_str = request.form.get("amount")
        plot_number = request.form.get("plot_number")
        land_location = request.form.get("land_location")
        marketer_name = request.form.get("marketer_name")

        # ✅ Validation
        if not client_name:
            return "Client name is required", 400

        if not amount_str:
            return "Amount is required", 400

        if not sale_type:
            return "Sale type is required", 400

        try:
            amount = float(amount_str)
        except ValueError:
            return "Invalid amount", 400

        # ✅ FIX: define number_of_plots
        try:
            number_of_plots = int(plot_number)
        except:
            number_of_plots = 0

        # ✅ Create sale
        sale = Sale(
            client_name=client_name,
            amount=amount,
            sale_type=sale_type,
            marketer_name=marketer_name,
            plot_number=plot_number,
            land_location=land_location
        )

        db.session.add(sale)
        db.session.commit()  # ✅ FIRST commit

        # 💰 Commission logic (FIXED)
        if sale.sale_type == "marketer":

            commission_amount = number_of_plots * 20000  # 🔥 CORRECT

            commission = Commission(
                sale_id=sale.id,
                amount=commission_amount
            )

            db.session.add(commission)
            db.session.commit()

        return redirect(url_for('dashboard'))

    return render_template("add_sale.html")
        
# =========================
# EDIT SALE
# =========================
@app.route("/edit_sale/<int:id>", methods=["GET", "POST"])
@login_required
def edit_sale(id):

    sale = Sale.query.get_or_404(id)

    if current_user.role != "admin":
        return "Unauthorized", 403

    if request.method == "POST":

        sale.client_name = request.form['client_name']
        sale.amount = float(request.form['amount'])
        sale.plot_number = request.form.get("plot_number")
        sale.land_location = request.form.get("land_location")
        sale.sale_type = request.form.get("sale_type")

        db.session.commit()

        # 🔥 UPDATE COMMISSION
        number_of_plots = 0
        try:
            number_of_plots = int(sale.plot_number)
        except:
            number_of_plots = 0

        commission_amount = number_of_plots * 20000

        commission = Commission.query.filter_by(sale_id=sale.id).first()

        if commission:
            commission.amount = commission_amount
        else:
            commission = Commission(
                sale_id=sale.id,
                amount=commission_amount
            )
            db.session.add(commission)

        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("edit_sale.html", sale=sale)


@app.route("/delete_sale/<int:id>")
@login_required
def delete_sale(id):

    if current_user.role != "admin":
        return "Unauthorized", 403

    sale = Sale.query.get_or_404(id)

    # delete commission first
    Commission.query.filter_by(sale_id=sale.id).delete()

    db.session.delete(sale)
    db.session.commit()

    return redirect(url_for("dashboard"))


# =========================
# CREATE USER (ADMIN ONLY)
# =========================
@app.route("/create_user", methods=["GET", "POST"])
@login_required
def create_user():

    if current_user.role != "admin":
        return "Unauthorized", 403

    if request.method == "POST":
        username = request.form['username']
        password = generate_password_hash(request.form['password'])
        role = request.form['role']

        user = User(
            username=username,
            password=password,
            role=role
        )

        db.session.add(user)
        db.session.commit()

        return redirect(url_for("dashboard"))

    return render_template("create_user.html")


with app.app_context():
    from models import User
    from werkzeug.security import generate_password_hash

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
# RUN APP
# =========================
if __name__ == "__main__":
    app.run(debug=True)