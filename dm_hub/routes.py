from dm_hub import app
from flask import render_template,url_for, request, flash, redirect, session
import json

from PIL import Image
from dm_hub.models import seller, buyer, product
from dm_hub.utils import (
    user_form_handler,
    upload_to_database,
    form_email_check,
    form_password_check,
    encrypt_password,
    authenticator,
    get_all_products,
    check_login_status,
    logout_user,
    validate_password_change,
    change_user_password,
    get_all_sellers,
    add_pdt_to_database,
    pdt_form_handler,
    get_seller_pdts,
    get_user_by_mail,
    update_company_info,
    get_user_orders,
    delete_order_from_database,
    register_order,
    get_product_info,
    delete_product_from_database,
    process_image_upload
    )


@app.route("/")
@app.route("/home")
def home_route():
    login_status = check_login_status()
    products = get_all_products(50)
    return render_template("home_page.html", products = products, login_status = login_status)

@app.route("/about_page")
def about_route():
    return render_template("about_page.html")


@app.route("/register", methods=["GET", "POST"])
def register_route():
    login_status = check_login_status()
    if request.method == "POST":
        form_data = dict(request.form)
        if form_password_check(form_data):
            if form_email_check(form_data):
                user_data = user_form_handler(form_data)
                encrypt_password(user_data)
                upload_to_database(user_data)
                flash("Your Account Was Created Succesfully")
                return redirect(url_for("login_route"))
            else:
                flash("An Account Already Exists With That Email Address!")
        else:
            flash("Please confirm with a similar password")
    return render_template("register_page.html", login_status = login_status)


@app.route("/login", methods=["GET", "POST"])
def login_route():
    login_status = check_login_status()
    if login_status[0] == True:
        flash("Youre Already Logged In")
        return redirect(url_for("home_route"))
    if request.method == "POST":
        form_data = dict(request.form)
        user_logged = authenticator(form_data)
        if user_logged != None:
            session["email_address"] = user_logged["email_address"]
            flash("You Have Successfully Logged In")
            return redirect(url_for("home_route"))
        else:
            flash("Login Unsucessfull !!!")
    return render_template("login_page.html", login_status = login_status)


@app.route("/logout_page")
def logout_route():
    logout_user()
    return redirect(url_for("home_route"))


@app.route("/account_page/")
def account_page_route():
    login_status = check_login_status()
    user_mail = request.args.get("user_mail")
    user = get_user_by_mail(user_mail)
    company_info = user.get("company_info") if user else None
    if user != None:
        if user["account_type"] == "Seller":
            products = get_seller_pdts(user_mail)
        else:
            products = None
    return render_template("account_page.html", login_status = login_status, user_mail = user_mail, products = products, user = user, company_info = company_info)


@app.route("/password_reset_page", methods=["GET", "POST"])
def password_reset_route():
    login_status = check_login_status()
    if request.method == "POST":
        form_data = dict(request.form)
        status = validate_password_change(form_data)
        if status[0]:
            change_user_password(form_data, status[1])
            flash("Password Change Successful")
            return redirect(url_for("login_route"))
        else:
            flash("Password Change not Approved !!!")
            flash("Check Email and Mother's Maiden Name inserted")
            flash("Check Password Confirmation")
    return render_template("password_reset_page.html", login_status = login_status)


@app.route("/sellers_page")
def sellers_route():
    login_status = check_login_status()
    all_sellers = get_all_sellers()    
    return render_template("sellers_page.html", login_status = login_status, all_sellers = all_sellers)


@app.route("/new_product_page", methods=["GET", "POST"])
def new_product_route():
    login_status = check_login_status()
    if request.method == "POST":
        product_name = request.form["product_name"]
        pdt_desc = request.form["pdt_desc"]
        category = request.form["category"]
        price = request.form["price"]
        currency = request.form["currency"]
        image = request.files["image"].read()
        image_name = process_image_upload(image)
        form_data = {
            "product_name": product_name,
            "pdt_desc": pdt_desc,
            "category": category,
            "price": price,
            "currency": currency,
            "image": image_name
        }
        pdt_data = pdt_form_handler(login_status[1], form_data)
        add_pdt_to_database(pdt_data)
        flash("Your Product Has Been Added  Successfully!!")
        return redirect(url_for("account_page_route", user_mail = login_status[1]["email_address"]))
    return render_template("new_product_page.html", login_status = login_status)


@app.route("/update_info_page", methods=["GET", "POST"])
def update_info_route():
    login_status = check_login_status()
    if request.method == "GET":
        form_data = login_status[1]
    if request.method == "POST":
        form_data = dict(request.form)
        update_company_info(login_status[1], form_data)
        flash("Your Company Info Has Been Updated")
    return render_template("update_info_page.html", login_status=login_status, form_data = form_data)


@app.route("/orders_page")
def orders_route():
    login_status = check_login_status()
    product_name = request.args.get("product_name")
    buyer_email = request.args.get("buyer_email")
    if product_name and buyer_email:
        delete_order_from_database(login_status[1], product_name, buyer_email)
    orders = get_user_orders(login_status[1])
    return render_template("orders_page.html", login_status = login_status, orders = orders)


@app.route("/product_page")
def product_page_route():
    login_status = check_login_status()
    order = request.args.get("order")
    product_name = request.args.get("product_name")
    owner_id = request.args.get("owner_id")
    delete = request.args.get("delete")
    product_info = get_product_info(owner_id, product_name)
    if login_status[0] == False:
        if order == "True":
            flash("Please Login Or Register To Order Item !!!")
    elif login_status[0] == True:
        if delete == "True":
            delete_product_from_database(login_status[1], product_name)
            flash("Your Product Has Been Deleted !!!")            
            return redirect(url_for("account_page_route", user_mail = login_status[1]["email_address"]))
        if order == 'True':
            register_order(login_status[1], owner_id, product_name)
            flash("Your Item Has Been Successfully Ordered, The Product Seller Will Contact You !!!")
    return render_template("product_page.html", login_status = login_status, product_info = product_info)


@app.route("/edit_product_page", methods=["GET", "POST"])
def edit_product_route():
    login_status = check_login_status()
    product_name = request.args.get("product_name")
    if request.method == "POST":
        product_name = request.form["product_name"]
        pdt_desc = request.form["pdt_desc"]
        category = request.form["category"]
        price = request.form["price"]
        currency = request.form["currency"]
        image = request.files["image"].read()
        image_name = process_image_upload(image)
        form_data = {
            "product_name": product_name,
            "pdt_desc": pdt_desc,
            "category": category,
            "price": price,
            "currency": currency,
            "image": image_name
        }
        pdt_data = pdt_form_handler(login_status[1], form_data)
        delete_product_from_database(login_status[1], product_name)
        add_pdt_to_database(pdt_data)
        flash("Your Product Has Been updated Successfully!!")
        return redirect(url_for("product_page_route", login_status = login_status, product_name = pdt_data[1], owner_id = login_status[1]["_id"]))        
    elif request.method == "GET":
        product_info = get_product_info(login_status[1]["_id"], product_name)
    return render_template("edit_product_page.html", login_status = login_status, form_data = product_info)