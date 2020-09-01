from flask import Flask, render_template, request, redirect, Response, session
from config import Config as cfg
import requests
import sqlcon
import mysqlconfig
import json


application = Flask(__name__, template_folder="templates")
application.debug = True
application.secret_key = cfg.SECRET_KEY


def get_registered_webhooks_for_shop():
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    get_webhooks_response = requests.get("https://" + session.get("shop") +
                                         "/admin/webhooks.json",
                                         headers=headers)

    if get_webhooks_response.status_code == 200:
        webhooks = json.loads(get_webhooks_response.text)
        print(webhooks)
        return webhooks
    else:
        return False


@application.route('/products', methods=['GET'])
def products():
    """ Get a stores products """
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    storeUrl = session.get("shop")

    endpoint = "/admin/products.json"
    response = requests.get("https://{0}{1}".format(session.get("shop"), endpoint), headers=headers)
    print(response)

    #If connection has been successfull ...
    if response.status_code == 200:
        products = json.loads(response.text)
        #print(json.dumps(products, indent=2))
        conn = sqlcon.mysqlconnect()
        
        productlist = products['products']

        for fields in productlist:



            productShopifyId = fields['id']
            vendor = fields['vendor']
            productTitle = fields['title']
            productPrice = fields['variants'][0]['price']
            productComparePrice = fields['variants'][0]['compare_at_price']
            productCategory = fields['product_type']
            productSubcategory = ''
            productImage = fields['images'][0]['src']

            if productCategory is None:
                productCategory = None

            if productSubcategory is None:
                productSubcategory = None

            if productComparePrice is None:
                productComparePrice = None

            verified = 'False'

            
            print(productShopifyId)
            print(vendor)
            print(productTitle)
            print(productPrice)
            print(productComparePrice)
            print(productCategory)
            print(productSubcategory)
            print(productImage)


            #Reference child json elements
            #print(fields['variants'][0]['product_id'])


            concatInput = (productShopifyId, storeUrl, vendor, verified, productTitle, productPrice, productComparePrice, productCategory, productSubcategory, productImage)
            concatUpdateInput = (productTitle, productPrice, productComparePrice, productCategory, productSubcategory, productImage, productShopifyId)


            with conn.cursor() as cur:
                checkProductExists = """SELECT product_id FROM products WHERE productShopifyId = %s"""
                cur.execute(checkProductExists, productShopifyId)
                result = cursor.fetchone()
                print(result)

                if result > 0:
                    updateProduct = """UPDATE products SET productName = %s, 
                    price = %s, 
                    comparePrice = %s,
                    productCategory = %s,
                    productSubcategory = %s,
                    productImage = %s,
                    updated_at = now()
                    where shopify_id = %s"""
                    cur.execute(sql, concatInput)
                    conn.commit()
                    cur.close()
                else
                    insertsql = """INSERT INTO products (shopify_id, store_url, vendor, verified, productName, price, comparePrice, productCategory, productSubcategory, productImage, updated_at, install_date) 
                    VALUES 
                    (%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())"""
                    #.format(productShopifyId, storeUrl, vendor, productTitle, productPrice, productComparePrice, productCategory, productSubcategory, productImage)
                    cur.execute(sql, concatInput)
                    conn.commit()
                    cur.close()
           

        return render_template('products.html', 
            products=products.get("products"))
    #If connection was unsuccessful ...
    else:
        return False


@application.route('/webhooks', methods=['GET', 'POST'])
def webhooks():
    if request.method == "GET":
        return render_template('webhooks.html',
                               webhooks=get_registered_webhooks_for_shop())
    else:
        ###THIS IS WHERE THE WEBHOOK UPDATES ####
        #webhook_data = json.loads(request.data)

        products = json.loads(request.data)
        #print(json.dumps(products, indent=2))
        conn = sqlcon.mysqlconnect()
        
        productlist = products['products']

        for fields in productlist:



            productShopifyId = fields['id']
            vendor = fields['vendor']
            productTitle = fields['title']
            productPrice = fields['variants'][0]['price']
            productComparePrice = fields['variants'][0]['compare_at_price']
            productCategory = fields['product_type']
            productSubcategory = ''
            productImage = fields['images'][0]['src']

            if productCategory is None:
                productCategory = None

            if productSubcategory is None:
                productSubcategory = None

            if productComparePrice is None:
                productComparePrice = None
            
            print(productShopifyId)
            print(vendor)
            print(productTitle)
            print(productPrice)
            print(productComparePrice)
            print(productCategory)
            print(productSubcategory)
            print(productImage)


            #Reference child json elements
            #print(fields['variants'][0]['product_id'])


            concatInput = (productShopifyId, productTitle, productPrice, productComparePrice, productCategory, productSubcategory, productImage, productShopifyId)
            
            with conn.cursor() as cur:
                            sql = """UPDATE products SET %s, %s, %s, %s, %s, %s, %s, %s
                            where shopify_id = %s"""
                            #(%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,now(),now())
                            #.format(productShopifyId, storeUrl, vendor, productTitle, productPrice, productComparePrice, productCategory, productSubcategory, productImage)
                            cur.execute(sql, concatInput)
                            conn.commit()
                            cur.close()


        #print("Title: {0}".format(webhook_data.get("title")))
        return Response(status=200)





@application.route('/register_webhook', methods=['GET'])
def register_webhook():
    headers = {
        "X-Shopify-Access-Token": session.get("access_token"),
        "Content-Type": "application/json"
    }

    payload = {
        "webhook": {
            "topic": "products/update",
            "address": "https://{0}/webhooks".format(cfg.HOST),
            "format": "json"
        }
    }
    response = requests.post("https://" + session.get("shop")
                             + "/admin/webhooks.json",
                             data=json.dumps(payload), headers=headers)

    if response.status_code == 201:

        return render_template('register_webhook.html',
                               webhook_response=json.loads(response.text))
    else:
        return Response(response="{0} - {1}".format(response.status_code,
                                                    response.text), status=200)


@application.route('/install', methods=['GET'])
def install():
    """
    Connect a shopify store
    """
    if request.args.get('shop'):
        shop = request.args.get('shop')
    else:
        return Response(response="Error:parameter shop not found", status=500)

    auth_url = "https://{0}/admin/oauth/authorize?client_id={1}&scope={2}&redirect_uri={3}".format(
        shop, cfg.SHOPIFY_CONFIG["API_KEY"], cfg.SHOPIFY_CONFIG["SCOPE"],
        cfg.SHOPIFY_CONFIG["REDIRECT_URI"]
    )
    print("Debug - auth URL: ", auth_url)

    return redirect(auth_url)



@application.route('/connect', methods=['GET'])
def connect():
    if request.args.get("shop"):
        params = {
            "client_id": cfg.SHOPIFY_CONFIG["API_KEY"],
            "client_secret": cfg.SHOPIFY_CONFIG["API_SECRET"],
            "code": request.args.get("code")
        }
        resp = requests.post(
            "https://{0}/admin/oauth/access_token".format(
                request.args.get("shop")
            ),
            data=params
        )

        

        if 200 == resp.status_code:
            resp_json = json.loads(resp.text)
            print(resp_json)

            session['access_token'] = resp_json.get("access_token")
            session['shop'] = request.args.get("shop")

            t = (session['shop'], session['access_token'])

            conn = sqlcon.mysqlconnect()


            with conn.cursor() as cur:
                            sql = """INSERT INTO shopify_installs (store_url,access_token,install_date) VALUES (%s,%s,now())"""
                            cur.execute(sql, t)
                            conn.commit()
                            cur.close()

#           Uncomment to turn back on webhooks when live
            return render_template('welcome.html', from_shopify=resp_json)
#           return render_template('products.html', from_shopify=resp_json)


        else:
            print("Failed to get access token: ", resp.status_code, resp.text)
            return render_template('error.html')

        



if __name__ == "__main__":
    application.run(host="#RemovedForSecurity")


