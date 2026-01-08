from django.urls import path

from . import views

urlpatterns=[
    path("", views.index, name="index"),
    path("<int:sheet_id>/", views.sheet, name="sheet"),
    path("buy/<int:sheet_id>/", views.buy, name="buy"),
    path("contact", views.contact_form, name="contact"),
    path("contact_submit", views.contact_submit, name="contact_submit"),
    #Stripe
    path("create_checkout_sesh", views.checkout, name="checkout"),
    path("get_sesh_status", views.sesh_status, name="session"),
    path("payment_hook", views.payment_webhook, name="payment_webhook"),
]