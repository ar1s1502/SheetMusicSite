from django.shortcuts import render
from django.http import JsonResponse, HttpResponse
from django.urls import reverse
from .models import Sheet
import os
import base64
import json
import stripe

#stripe test api key; secret
stripe.api_key = 'remov'

def _serializePDF(arr: Sheet):
    with open("sheetmusic/static/" + arr.file_path(), "rb") as f:
        pdf_bytes = f.read()
        return base64.b64encode(pdf_bytes).decode('utf-8')

def index(request):
    arrangements = Sheet.objects.all()
    pdf_dict = {}
    for arr in arrangements:
        current_directory = os.getcwd()
        print("current directory: ", current_directory)
        #since unix file:// paths are not allowed to be accessed by browser, must send the pdf as bytes
        #must encode pdf as ascii byte string to make it json serializable
        encoded_bytes = _serializePDF(arr)    
        pdf_dict[arr.id] = encoded_bytes

    context = {
        "arrangements": arrangements,
        "pdf_dict": pdf_dict,
        #Stripe shall redirect to index to display confirmation after a checkout is completed
        "checkoutsession_id": request.GET.get('session_id', None) #default to None if no 'session_id' param
    }
    return render(request, "sheetmusic/index.html", context)

def sheet(request, sheet_id: int):
    sheet_music = Sheet.objects.get(id = sheet_id)
    sheet_bytes = _serializePDF(sheet_music)
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
    sheet_bytes = _serializePDF(sheet_music)
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
        post_data = json.loads(request.body)
        print(post_data)
        sheet = Sheet.objects.get(id = post_data['sheet_id'])
    except KeyError as e:
        print(str(e))
        return JsonResponse({
            "KeyError": str(e)
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
    session = stripe.checkout.Session.retrieve(request.GET['session_id'])
    session_status = {
        "status": session.status,
        "customer_email": session.customer_details.email,
    }
    return JsonResponse(session_status)

    