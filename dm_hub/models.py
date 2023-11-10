
# seller class
class seller:
    def __init__(self, first_name, last_name, email_address, dob, gender,account_type, country, location, phone_number, password, sq_answer):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.dob = dob
        self.gender = gender
        self.account_type = account_type
        self.country = country
        self.location = location
        self.phone_number = phone_number
        self.password = password
        self.sq_answer = sq_answer
        self.products = [],
        self.orders = [],
        # self.cart = []
   
    def to_dict_object(self):
        seller_dict = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address,
            "dob": self.dob, "gender": self.gender,
            "account_type": self.account_type,
            "country": self.country,
            "location" : self.location,
            "phone_number": self.phone_number,
            "password": self.password,
            "sq_answer": self.sq_answer,
            "products": [],
            "orders": []
            }
        return seller_dict
    
    def __repr__(self):
        return f"\n{self.first_name}\n{self.last_name}\n{self.email_address}\n{self.phone_number}\n{self.location}\n{self.country}\n"
    
 
      
#buyer class
class buyer:
    def __init__(self, first_name, last_name, email_address, dob, gender,account_type, country, location, phone_number, password, sq_answer):
        self.first_name = first_name
        self.last_name = last_name
        self.email_address = email_address
        self.dob = dob
        self.gender = gender
        self.account_type = account_type
        self.country = country
        self.location = location
        self.phone_number = phone_number
        self.password = password
        self.sq_answer = sq_answer
        self.cart_items = [],
        
        
    def to_dict_object(self):
        seller_dict = {
            "first_name": self.first_name,
            "last_name": self.last_name,
            "email_address": self.email_address,
            "dob": self.dob, "gender": self.gender,
            "account_type": self.account_type,
            "country": self.country,
            "location" : self.location,
            "phone_number": self.phone_number,
            "password": self.password,
            "sq_answer": self.sq_answer,
            "cart_items": self.cart_items
            }
        return seller_dict
    
    def __repr__(self):
        return f"\n{self.first_name}\n{self.last_name}\n{self.email_address}\n{self.phone_number}\n{self.location}\n{self.country}\n"



# product class   
class product:
    def __init__(self, product_name, pdt_desc, category, price, currency, image=None, owner_id=None):
        self.product_name = product_name
        self.pdt_desc = pdt_desc
        self.category = category
        self.price = price
        self.currency = currency
        self.image = image
        self.owner_id = owner_id
        
    def to_dict_object(self):
        product_dict = {
            "product_name": self.product_name,
            "pdt_desc": self.pdt_desc,
            "category": self.category,
            "price": self.price,
            "currency": self.currency,
            "image": self.image,
            "owner_id": self.owner_id
        }
        return product_dict
        
    def __repr__(self):
        return f"\n{self.product_name}\n{self.category}\n{self.price}\n{self.currency}\n"  
        
