from django.shortcuts import render
from .models import Sheet
import os
import base64

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
        "pdf_dict": pdf_dict
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