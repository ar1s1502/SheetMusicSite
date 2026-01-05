from django.shortcuts import render, redirect
from django.http import JsonResponse, HttpResponse, FileResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt

from .models import Sheet
import os
import base64
import json
import stripe


#stripe test api key; secret

stripe.api_key = settings.STRIPE_SK
endpt_sec = settings.WEBHOOK_SEC 

def _serializeFile(arr: Sheet, file: str):
    with open("sheetmusic/static/" + arr.file_path(filetype = file), "rb") as f:
        pdf_bytes = f.read()
        return base64.b64encode(pdf_bytes).decode('utf-8')
    
def _fulfillOrder(session_id):

    # TODO: Make this function safe to run multiple times,
    # even concurrently, with the same session ID

    # TODO: Make sure fulfillment hasn't already been
    # performed for this Checkout Session

    session = stripe.checkout.Session.retrieve(session_id, expand=['line_items', 'customer'])
    #1. create new order object, save it. Fulfilled = false 

    if session.payment_status != 'unpaid':
        
        # TODO: Perform fulfillment of the line items. Order.fulfilled = True + order.save
        product = session.line_items.data[0]
        customer = session.customer
        print(customer)
        print(product)
        print(product.description)
        print('sheet_id: '+product.metadata['sheet_id'])
        sheet = Sheet.objects.get(id = product.metadata['sheet_id'])

        #TODO email as thank you + customer services
        # print("email: " + session.customer_email) #session.customer_email is NoneType for some reason
        #send and download zip

        # TODO: Record/save fulfillment status for this Checkout Session

    return

def index(request):
    arrangements = Sheet.objects.all()
    pdf_dict = {}
    for arr in arrangements:
        current_directory = os.getcwd()
        print("current directory: ", current_directory)
        #since unix file:// paths are not allowed to be accessed by browser, must send the pdf as bytes
        #must encode pdf as ascii byte string to make it json serializable
        encoded_bytes = _serializeFile(arr, "pdf")    
        pdf_dict[arr.id] = encoded_bytes

    #2. if session_id exists, get its order. 
    #3. check if order's been fulfilled and if it's been successfullyl paid. 
    #4. if not fulfilled && successfully paid, render download button with href=pdf_bytes. 
        # on client side, use checkout_confirm.js to click download automatically. 
    #5. change status to fulfilled upon rendering the download button

    context = {
        "arrangements": arrangements,
        "pdf_dict": pdf_dict,
        #Stripe shall redirect to index to display confirmation after a checkout is completed
        "checkoutsession_id": request.GET.get('session_id', None) #default to None if no 'session_id' param
    }
    return render(request, "sheetmusic/index.html", context)

def sheet(request, sheet_id: int):
    sheet_music = Sheet.objects.get(id = sheet_id)
    sheet_bytes = _serializeFile(sheet_music, "pdf")
    if (sheet_music.price == 0):
        sheet_price = "Free!"
    else:
        sheet_price = f"${(sheet_music.price/100):.2f}"

    context = {
        "sheet": sheet_music,
        "sheet_bytes": sheet_bytes,
        "price": sheet_price
    }
    return render(request, "sheetmusic/sheet.html", context)

def buy(request, sheet_id: int):
    sheet_music = Sheet.objects.get(id = sheet_id)
    sheet_bytes = _serializeFile(sheet_music, "pdf")
    if (sheet_music.price == 0):
        sheet_price = "Free!"
    else:
        sheet_price = f"${(sheet_music.price/100):.2f}"

    context = {
        "sheet": sheet_music,
        "sheet_bytes": sheet_bytes,
        "price": sheet_price,
    }
    return render(request, "sheetmusic/buy.html", context)

"""
    Stripe API routes
"""
def checkout(request)->JsonResponse:
    try:  
        #post data in request.body, not request.POST, because application/json payload, not from template
        post_data = json.loads(request.body)
        print(post_data)
        sheet = Sheet.objects.get(id = post_data['sheet_id'])
    except KeyError as e:
        print(str(e))
        return JsonResponse({
            "KeyError": str(e)
        })
    except Sheet.DoesNotExist as e: 
        print("specified id doesn't exist in Sheet")
        return JsonResponse({
            "DBError": str(e)
        })   
    try: 
        abs_return_path = request.build_absolute_uri(reverse('index'))

        session = stripe.checkout.Session.create(
            ui_mode = 'embedded',
            line_items=[{
                    'price_data': {
                        'currency': 'usd',
                        'product_data': {
                            'name': sheet.title
                        },
                    'unit_amount': sheet.price,
                    },
                    'quantity': 1,
                    'metadata': {
                        'sheet_id': sheet.id
                    }
                }],
            mode='payment',
            #redirect to home page + display confirmation there.
            return_url= f"{abs_return_path}?session_id={{CHECKOUT_SESSION_ID}}",
        )
    except Exception as e:
        print(str(e))
        return JsonResponse({
            "SessionCreateError": str(e)
        })
    
    session_data = {
        "clientSecret": session.client_secret
    }
    return JsonResponse(session_data)

def sesh_status(request)->JsonResponse:
    print("session_id: " + request.GET['session_id'])
    session = stripe.checkout.Session.retrieve(request.GET['session_id'], expand=['line_items'])
    product = session.line_items.data[0]
    customer = session.customer_details
    print("product, customer from session complete response:")
    print(customer) #customer.name, customer.email
    print(product)
    #fetch order instance corresponding to session_id and email
    # if paid, not fulfilled, enable download in session_details

    session_details = {
        "status": session.status,
        "customer_email": session.customer_details.email,
    }
    return JsonResponse(session_details)

#Webhook for payment confirmation
@csrf_exempt #TODO remove after deployment
def payment_webhook(request):
    try: 
        post_body = request.body
        sig_header = request.META['HTTP_STRIPE_SIGNATURE']
    except KeyError as e:
        print(str(e))
        return HttpResponse(status = 400)
    
    try:
        event = stripe.Webhook.construct_event(
            post_body, sig_header, endpt_sec
        )
    except ValueError as e:
        #invalid post req payload
        return HttpResponse(status = 400)
    except stripe.error.SignatureVerificationError as e:
        return HttpResponse(status = 400)

    if (event['type'] == 'checkout.session.completed' or 
        event['type'] == 'checkout.session.async_payment_succeeded'
    ):
        _fulfillOrder(session_id = event['data']['object']['id'])

    return HttpResponse(status = 200) 


    