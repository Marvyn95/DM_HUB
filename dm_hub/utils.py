from dm_hub.models import seller, buyer, product
from dm_hub import dmhub_client
import bcrypt
import random
from flask import session
from bson.objectid import ObjectId
from PIL import Image
from io import BytesIO
import secrets
import os


#extracts required user values from the form 
#takes form data as dictionary
def user_form_handler(data_object):
    data_object.pop("confirm_password")
    data_object.pop("submit")
    return list(data_object.values())

#adds user to database
#takes user form data values extracted to a list as arguments
def upload_to_database(user):
    seller_coll = dmhub_client["dm-hub"]["sellers"]
    buyer_coll = dmhub_client["dm-hub"]["buyers"]
    
    if user[5] == "Seller":
        new_seller = seller(*user)
        new_seller_dict = new_seller.to_dict_object()
        seller_coll.insert_one(new_seller_dict)
        return True    
    elif user[5] == "Buyer":
        new_buyer = buyer(*user)
        new_buyer_dict = new_buyer.to_dict_object()
        buyer_coll.insert_one(new_buyer_dict)
        return True
    else:
        return False

#checks user form registration email inputs if valid
def form_email_check(user_data):
    seller_coll = dmhub_client["dm-hub"]["sellers"]
    buyer_coll = dmhub_client["dm-hub"]["buyers"]
    
    found = seller_coll.find_one({"email_address": user_data["email_address"]})
    if found is not None:
        return False
    found = buyer_coll.find_one({"email_address": user_data["email_address"]})    
    if found is not None:
        return False
    return True

#checks whether registration form password data is okay
def form_password_check(user_data):
    if user_data["password"] == user_data["confirm_password"]:
        return True
    return False

#encrypt user's password
def encrypt_password(user):
    hashed_password = bcrypt.hashpw(user[-2].encode("utf-8"), bcrypt.gensalt())
    user[-2] = hashed_password
    return True

#verifying login details / authenticating user login
def authenticator(form_data):
    found_user = dmhub_client["dm-hub"]["sellers"].find_one({"email_address": form_data["email_address"]})
    if found_user == None:
        found_user = dmhub_client["dm-hub"]["buyers"].find_one({"email_address": form_data["email_address"]})   
    if found_user != None:
        if bcrypt.checkpw(form_data["password"].encode("utf-8"), found_user["password"]):
            found_user.pop("password")
            found_user.pop("sq_answer")
            return(found_user)
        else:
            return None
    else:
        return None
              
#getting specified number of products from the database from all sellers
def get_all_products(num):
    sellers = dmhub_client["dm-hub"]["sellers"].find()
    products = []
    for seller in sellers:
        products.extend(seller["products"])
    random.shuffle(products)
    return products[0:num]

#checks if user is logged in
def check_login_status():
    status = session.get("email_address")
    if status:
        user = dmhub_client["dm-hub"]["sellers"].find_one({"email_address": status})
        if user == None:
            user = dmhub_client["dm-hub"]["buyers"].find_one({"email_address": status})
        user.pop("password")
        user.pop("sq_answer")
        return (True, user)
    return (False, None)

#logs out user/ deletes user session
def logout_user():
    session.pop("email_address", None)
    return True

#validates user credentials for passsword change
def validate_password_change(form_data):
    email = form_data["email_address"]
    found = dmhub_client["dm-hub"]["sellers"].find_one({"email_address": email})
    if found == None:
        found == dmhub_client["dm-hub"]["buyers"].find_one({"email_address": email})
    if (found == None) or (form_data["sq_answer"] != found["sq_answer"]) or form_data["password"] != form_data["confirm_password"]:
        return False, None
    return True, found["account_type"]

#changes the password of the user once request has been approved
def change_user_password(form_data, acc_type):
    hashed_password = bcrypt.hashpw(form_data["password"].encode("utf-8"), bcrypt.gensalt())        
    if acc_type == "Seller":
        dmhub_client["dm-hub"]["sellers"].update_one({"email_address": form_data["email_address"]}, {"$set": {"password": hashed_password}})
    elif acc_type == "Buyer":
        dmhub_client["dm-hub"]["buyers"].update_one({"email_address": form_data["email_address"]}, {"$set": {"password": hashed_password}})
    return True

#gets all seller from database
def get_all_sellers():
    all_sellers = dmhub_client["dm-hub"]["sellers"].find()
    sellers = []
    for seller in all_sellers:
        seller.pop("password")
        seller.pop("sq_answer")
        sellers.append(seller)
    print(sellers)
    return sellers

#extracts values from new pdt form into a list
def pdt_form_handler(user, form_data):
    form_data = list(form_data.values())
    form_data.append(user["_id"])
    return form_data

#adds a new product to the database
def add_pdt_to_database(form_data):
    new_product = product(*form_data)
    new_product_dict = new_product.to_dict_object()
    dmhub_client["dm-hub"]["sellers"].update_one({"_id": ObjectId(new_product_dict["owner_id"])}, {"$push": {"products": new_product_dict}})
    return True

#get all products sold by seller
def get_seller_pdts(user_mail):
    seller = dmhub_client["dm-hub"]["sellers"].find_one({"email_address": user_mail})
    products = seller["products"]
    return products

#gets and user data by email
def get_user_by_mail(user_mail):
    user = dmhub_client["dm-hub"]["sellers"].find_one({"email_address": user_mail})
    if user == None:
        user = dmhub_client["dm-hub"]["buyers"].find_one({"email_address": user_mail})
    if user != None:
        user.pop("password")
        user.pop("sq_answer")
    return user

#filters user info to extact user data
def update_company_info(user, form_data):
    print(form_data)
    dmhub_client["dm-hub"]["sellers"].update_one({"_id": ObjectId(user["_id"])}, {"$set": {"company_info": form_data}})
    return True

#gets user company data from the database
def get_user_company_data(user):
    user_data = dmhub_client["dm-hub"]["sellers"].find_one({"_id": user["_id"]})
    company_data = user_data.get("company_info")
    print(company_data)
    return company_data

#gets user's orders from database
def get_user_orders(user):
    orders = dmhub_client["dm-hub"]["sellers"].find_one({"_id": user["_id"]}, {"orders": 1})["orders"]
    return orders

#deletes order from the database
def delete_order_from_database(user, product_name, buyer_email):
    orders = get_user_by_mail(user["email_address"])["orders"]
    new_order_list = []
    for order in orders:
        if order["product_name"] == product_name and order["buyer_info"][3] == buyer_email:
            continue
        new_order_list.append(order)
    dmhub_client["dm-hub"]["sellers"].update_one({"_id": ObjectId(user["_id"])}, {"$set": {"orders": new_order_list}})
    return True

#processes user orders
def register_order(user, owner_id, product_name):
    products = dmhub_client["dm-hub"]["sellers"].find_one({"_id": ObjectId(owner_id)})["products"]
    for pdt in products:
        if pdt["product_name"] == product_name:
            order = pdt       
    order.pop("owner_id")
    buyer_info = [user["first_name"], user["last_name"], user["phone_number"], user["email_address"], user["location"], user["country"]]
    order["buyer_info"] = buyer_info
    dmhub_client["dm-hub"]["sellers"].update_one({"_id": ObjectId(owner_id)}, {"$push": {"orders": order}})
    return True

#gets a product's information from the database
def get_product_info(owner_id, product_name):
    pdt_owner = dmhub_client["dm-hub"]["sellers"].find_one({"_id": ObjectId(owner_id)})
    products = pdt_owner["products"]
    for product in products:
        if product["product_name"] == product_name:
            break
    return product

#deletes a product from the database
def delete_product_from_database(user, product_name):
    products = dmhub_client["dm-hub"]["sellers"].find_one({"_id": ObjectId(user["_id"])})["products"]
    new_product_list = []
    for product in products:
        if product["product_name"] == product_name:
            continue
        new_product_list.append(product)
    dmhub_client["dm-hub"]["sellers"].update_one({"_id": ObjectId(user["_id"])}, {"$set": {"products": new_product_list}})
    return True

#processes the uploaded image (bytes) and returns name to save
def process_image_upload(image_bytes):
    image = Image.open(BytesIO(image_bytes))
    image_size = (600, 400)
    image.thumbnail(image_size)
    image_name = secrets.token_hex(16) + ".png"
    # directory = "./dm_hub/static/images/"
    # os.makedirs(directory, exist_ok=True)
    image.save(f"./dm_hub/static/images/{image_name}")
    return image_name