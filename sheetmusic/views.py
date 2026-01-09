from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from .models import Sheet, Order, Request, Feedback
from .forms import FeedbackForm, RequestForm

import os
import base64
import smtplib #for email
from email.message import EmailMessage
import json
import stripe

#TODO: replace stripe test api key
stripe.api_key = settings.STRIPE_SK
endpt_sec = settings.WEBHOOK_SEC 

def _serializeFile(arr: Sheet, file_type: str):
    with open("sheetmusic/static/" + arr.file_path(filetype = file_type), "rb") as f:
        pdf_bytes = f.read()
        return base64.b64encode(pdf_bytes).decode('utf-8')

def _sendEmail(to_addr: str, subj: str,
               msg_txt: str | None, file: bytes | None, file_name: str | None):
    
    from_addr = "aaronteng2779@gmail.com"
    email = EmailMessage()
    email['Subject'] = subj
    email['From'] = from_addr
    email['To'] = to_addr
    if msg_txt:
        email.set_content(msg_txt)
    if file: 
        email.add_attachment(file, maintype='application', subtype='octet-stream', filename=file_name)

    #authenticate to SMTP server
    with smtplib.SMTP_SSL('smtp.gmail.com', 465) as serv:
        serv.login(from_addr, settings.GMAIL_APP_PW)
        serv.send_message(email)

def _fulfillOrder(session_id):
    session = stripe.checkout.Session.retrieve(session_id, expand=['line_items'])
    product = session.line_items.data[0]
    customer = session.customer_details
    print('product, customer from _fulfill:')
    print(customer)
    print(f"{product.description}'s sheet_id: {product.metadata['sheet_id']}")
    # Make sure fulfillment hasn't already been performed for this Session
    try:
        order = Order.objects.get(session_id = session.id)
    except Order.DoesNotExist:
        sheet = Sheet.objects.get(id = product.metadata['sheet_id'])
        order = sheet.order_set.create(
            session_id=session.id,
            customer_name=customer['name'],
            email = customer['email'],
        )
    if (order.fulfilled): 
        return
    if session.payment_status != 'unpaid':
        #Perform fulfillment of the line items.
        #Record/save fulfillment status for this Checkout Session
        order.paid = True
        order.fulfilled = True
        order.save()
        print(f"Order from _fulfillOrder: {order}")
        #email as thank you + customer services. 
        with open(f"sheetmusic/static/{sheet.file_path(filetype="mscz")}", "rb") as f:
            bytes = f.read()
        thankyoumsg = """Hello!
        Attached below is a .mscz file of the Musescore4 Project that created the sheet music. 
        (The .zip file is sometimes too large to be linked as an attachment).         
        Opening the .mscz file with Musescore will give you access to the full score.
        If there is any mistake in the sheet music, let me know and I will send you a fixed copy, or you can edit it yourself

    - Aaron"""
        _sendEmail(to_addr = customer.email,
                   subj = "Your Sheet Music Order",
                   msg_txt = thankyoumsg,
                   file = bytes,
                   file_name = sheet.title.replace(" ","") + ".mscz")

    return

"""
    Views
"""
def index(request):
    arrangements = Sheet.objects.all()
    pdf_dict = {}
    for arr in arrangements:
        current_directory = os.getcwd()
        print("current directory: ", current_directory)
        #since unix file:// paths are not allowed to be accessed by browser, must send the pdf as bytes
        #must encode pdf as ascii byte string to make it json serializable 
        pdf_dict[arr.id] = _serializeFile(arr, "pdf")

    context = {
        "arrangements": arrangements,
        "pdf_dict": pdf_dict,
        #Stripe shall redirect to index to display confirmation + download product after a checkout is completed
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

def contact_form(request):
    req_form = RequestForm(label_suffix="")
    fdbk_form = FeedbackForm(label_suffix="")

    context = {
        "req_form": req_form,
        "fdbk_form": fdbk_form,
    }
    return render(request, 'sheetmusic/contact_form.html', context)

def contact_submit(request)->HttpResponse:
    #validate form
    #if successful create new Request or Feedback, send email, set success message
    #else, set error message
    #return render contact_form again, display banner with msg

    if (request.POST['formtype'] == 'request'):
        return HttpResponse(status = 200)
    elif (request.POST['formtype'] == 'feedback'):

        return HttpResponse(status = 200)
    else:
        return HttpResponse(status = 400)


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
            name_collection={
                'individual': {
                    'optional': False,
                    'enabled': True,
                }
            },
            custom_text={
                'submit': {
                    'message': "After completing the checkout form, check your email for a receipt from Stripe.",
                },
            },
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

    if session.status == 'complete':
        try:
            order = Order.objects.get(session_id = session.id, sheet__id = product['metadata']['sheet_id'])
        except Order.DoesNotExist:
            sheet = Sheet.objects.get(id = product['metadata']['sheet_id'])
            order = sheet.order_set.create(
                session_id=session.id,
                customer_name=customer['name'],
                email = customer['email'],
                #for free orders, return_url ('index') is rendered before webhook handler, hence payment_status would be 'paid'
                paid = True if session.payment_status != 'unpaid' else False 
            )
    print(f"order: {order}")
    display_download = order and (order.paid)
    print(f'display_download: {display_download}')

    session_details = {
        "status": session.status,
        "customer_email": customer.email,
        "display_download": display_download,
        "download_content": _serializeFile(order.sheet, 'zip') if display_download else None,
        "filetype": 'zip' if display_download else None,
        "download_title": order.sheet.title.replace(" ","") if display_download else None
    }
    
    return JsonResponse(session_details)

#Webhook waiting payment confirmation from stripe
#For some reason, this triggers after get_sesh_status if product is free, and before get_sesh_status if product isn't. 
#Hence the weird order fulfillment logic where an order can be created both in get_sesh_status and in _fulfillOrder
#Also because the webhook is returning a response to stripe, you can not route to app urls from this function (and conseq. _fulfillOrder)
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
    event['type'] == 'checkout.session.async_payment_succeeded'):
        _fulfillOrder(session_id = event['data']['object']['id'])

    return HttpResponse(status = 200) 


    