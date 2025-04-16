from django.db import models

class Preset(models.Model):
    PRESET_TYPES = [
        ('date_range', "Date Range"),
        ('amount_filter', "Amount Filter"),
        ('keyword', "Keyword"),
    ]
    
    COMPARISONS = [
        ('=', "Equals"),
        ('gt', "Greater Than"),
        ('lt', "Less Than"),
    ]
    
    DEFAULT_IMAGE = 'images/default.png'
    
    name = models.CharField(max_length=30)
    image = models.ImageField(upload_to='images/', null=False, blank=False, default=DEFAULT_IMAGE)
    preset_type = models.CharField(choices=PRESET_TYPES)
    start_date = models.DateField(null=True, blank=True)
    end_date = models.DateField(null=True, blank=True)
    
    keywords = models.TextField(null=True, blank=True, 
                                help_text='Comma-seperated keywords')
    
    amount_value = models.FloatField(null=True, blank=True)
    comparison_type = models.CharField(choices=COMPARISONS, null=True, blank=True)
    
    def __str__(self):
        return self.name