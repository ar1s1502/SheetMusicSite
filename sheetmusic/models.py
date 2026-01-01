from django.db import models

# Create your models here.
class Sheet(models.Model):
    title = models.CharField(max_length = 100)
    artist = models.CharField(max_length = 50)
    arranger = models.CharField(max_length = 50, default="Aaron Teng")
    vrsn = models.CharField(max_length = 10, default = "")
    synopsis = models.TextField(null=True, default=None)
    instr = models.CharField(max_length=50)

    def __str__(self):
        return f"{self.title} - {self.artist}"
    
    def file_path(self):
        title = (self.title).replace(" ","")
        return f"sheetmusic/{title}/{self.vrsn}_{title}.pdf"
    
    def mp3_path(self):
        title = (self.title).replace(" ","")
        return f"sheetmusic/{title}/{self.vrsn}_{title}.mp3"