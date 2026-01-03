from django.urls import path

from . import views

urlpatterns=[
    path("", views.index, name="index"),
    path("<int:sheet_id>/", views.sheet, name="sheet"),
    path("buy/<int:sheet_id>/", views.buy, name="buy"),
]