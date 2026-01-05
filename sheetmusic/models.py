from django.db import models

# Create your models here.
class Sheet(models.Model):
    # A sheet has many orders
    title = models.CharField(max_length = 100)
    artist = models.CharField(max_length = 50)
    arranger = models.CharField(max_length = 50, default="Aaron Teng")
    vrsn = models.CharField(max_length = 10, default = "")
    synopsis = models.TextField(null=True, default=None)
    instr = models.CharField(max_length=50)
    price = models.IntegerField(default = 200) #in cents

    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    def file_path(self, filetype: str)->str:
        title = (self.title).replace(" ", "")
        return f"sheetmusic/{title}/{self.vrsn}_{title}." + filetype

    #template tags can't take args in model method calls (besides self), so need to define as a property
    def mp3_path(self):
        title = (self.title).replace(" ","")
        return f"sheetmusic/{title}/{self.vrsn}_{title}.mp3"


class Order(models.Model):
    #belongs to a Sheet.
    session_id = models.CharField(max_length = 512)     #stripe checkout.session obj ID
    customer_id = models.CharField(max_length = 512)    #stripe customer obj ID
    customer_name = models.CharField(max_length = 60)
    email = models.EmailField(max_length = 100)
    fulfilled = models.BooleanField(default = False)
    paid = models.BooleanField(default = False)
    

