from django import forms
from analyzer.models import Preset
import datetime

class DateRangePresetForm(forms.ModelForm):
    class Meta:
        model = Preset
        fields = ['name', 'start_date', 'end_date', 'image']
        widgets = {
            'start_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',
            }),
            'end_date': forms.DateInput(attrs={
                'class': 'form-control',
                'type': 'date',    
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Preset Name'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['preset_type'] = 'date_range'
        if not kwargs.get('instance'):
            today = datetime.date.today()
            first_day = today.replace(day=1)
            self.initial['start_date'] = first_day
            self.initial['end_date'] = today

class KeywordSearchPresetForm(forms.ModelForm):
    class Meta:
        model = Preset
        fields = ['name', 'keywords', 'image']
        widgets = {
            'keywords': forms.Textarea(attrs={
                'class': 'form-control',
                'placeholder': 'Comma-seperared values e.g., Amazon, Netflix, Salary'
            }),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Preset Name'
            }),
        }
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['preset_type'] = 'keyword_search'
        self.fields['keywords'].required = True


class AmountFilterPresetForm(forms.ModelForm):
    class Meta:
        model = Preset
        fields = ['name', 'amount_value', 'comparison_type', 'image']
        help_texts = {
            'amount_value': 'Amount for comparison',
            'comparison_type': 'Select a comparison type'
        }
        widgets = {
            'name': forms.TextInput(attrs={
                'class': 'form-control',
                'placeholder': 'Preset Name'
            }),
            'amount_value': forms.NumberInput(attrs={
                'class': 'form-control',
                'placeholder': 'e.g., 1000'
            }),
            'comparison_type': forms.Select(attrs={
                'class': 'form-select'
            }, ),
            'image': forms.ClearableFileInput(attrs={
                'class': 'form-control'
            }),
        }
        
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.initial['preset_type'] = 'amount_filter'
        self.fields['comparison_type'].required = True
        self.fields['amount_value'].required = True
        