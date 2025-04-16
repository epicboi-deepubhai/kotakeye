from django.contrib import admin
from analyzer.models import Preset

@admin.register(Preset)
class PresetAdmin(admin.ModelAdmin):
    list_display = ('name', 'preset_type')
    search_fields = ('name',)