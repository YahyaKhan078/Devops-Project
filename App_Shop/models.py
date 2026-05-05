from django.db import models
from django.conf import settings

# Create your models here.

class AgeGroup(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
# Men
# Boys        

class Category(models.Model):
    name = models.CharField(max_length=50)
    def __str__(self):
        return self.name
    
# Tops
# Bottoms
    
class ClothingType(models.Model):
    name = models.CharField(max_length=50)

    def __str__(self):
        return self.name
    
# Jeans
# Shirts
# Tees




class Product(models.Model):

    mainimage = models.ImageField(upload_to='Products')
    image2 = models.ImageField(upload_to='Products', blank=True, null=True)
    image3 = models.ImageField(upload_to='Products', blank=True, null=True)
    name = models.CharField(max_length=100)
    preview_text = models.TextField(max_length=200)
    detail_text = models.TextField(max_length=1000)

    price = models.DecimalField(max_digits=10, decimal_places=2)
    old_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, default=0.00)

    created = models.DateTimeField(auto_now_add=True)

    # NORMALIZED RELATIONS
    age_group = models.ForeignKey(AgeGroup, on_delete=models.CASCADE)
    category = models.ForeignKey(Category, on_delete=models.CASCADE, default=1)
    clothing_type = models.ForeignKey(ClothingType, on_delete=models.CASCADE)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ('-created',)



class Review(models.Model):
    user = models.ForeignKey(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    product = models.ForeignKey(Product, on_delete=models.CASCADE, related_name='reviews')

    rating = models.IntegerField(default=5)  # 1–5 stars
    comment = models.TextField(blank=True)

    created = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.user} - {self.product} ({self.rating})"

    


