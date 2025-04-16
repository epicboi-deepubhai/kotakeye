from django.shortcuts import render, redirect, get_object_or_404
from django.contrib import messages
from django.views import View
from django.views.generic import CreateView
from django.http import Http404
from analyzer.models import Preset
from analyzer.forms import DateRangePresetForm, KeywordSearchPresetForm, AmountFilterPresetForm
from analyzer.utils import get_pdf_df, analyze_amount_filter, analyze_date_range, analyze_keywords
import json
import pandas as pd

class IndexView(View):
    def get(self, request, *args, **kwargs):
        request.session.setdefault('dataframes', list())
        
        date_range_presets = Preset.objects.filter(preset_type='date_range').order_by('name')
        keyword_presets = Preset.objects.filter(preset_type='keyword').order_by('name')
        amount_filter_presets = Preset.objects.filter(preset_type='amount_filter').order_by('name')
        pdf_count = len(request.session.get('dataframes', []))

        context = {
            'pdf_count': pdf_count,
            'date_range_presets': date_range_presets,
            'amount_presets': amount_filter_presets,
            'keyword_presets': keyword_presets
        }
        return render(request, 'index.html', context)

    def post(self, request, *args, **kwargs):
        password = request.POST.get('password', None)
        uploaded_files = request.FILES.getlist('pdf_files')
        dfs = request.session.get('dataframes', [])
        pdf_count = len(dfs)
        
        for pdf_file in uploaded_files:
            try:
                df = get_pdf_df(pdf_file, password)
                if df is not None:
                    df_json = df.to_json(orient='records', date_format='iso')
                    print(df_json)
                    dfs.append(json.loads(df_json))
                    pdf_count += 1
            except Exception as e:
                messages.error(request,
                               f'Error processing {pdf_file.name}: {str(e)}\nDid you enter the correct password?',
                               extra_tags='danger')

        request.session['dataframes'] = dfs
        
        date_range_presets = Preset.objects.filter(preset_type='date_range').order_by('name')
        keyword_presets = Preset.objects.filter(preset_type='keyword').order_by('name')
        amount_filter_presets = Preset.objects.filter(preset_type='amount_filter').order_by('name')

        context = {
            'pdf_count': pdf_count,
            'date_range_presets': date_range_presets,
            'amount_filter_presets': amount_filter_presets,
            'keyword_presets': keyword_presets
        }
        
        if pdf_count > 0:
            messages.success(request, f'Successfully processed {pdf_count} statement(s)')
            return render(request, 'index.html', context)
        else:
            messages.warning(request, "No valid data was extracted from the uploaded files")
            return redirect('index')
        

class CreatePresetView(CreateView):
    template_name = 'create_preset.html'
    form_class = None
    title = ''
    preset_type = ''

    def dispatch(self, request, *args, **kwargs):
        self.preset_type = self.kwargs['preset_type']

        if self.preset_type == 'date_range':
            self.form_class = DateRangePresetForm
            self.title = 'Create Date Range Preset'
        elif self.preset_type == 'keyword_search':
            self.form_class = KeywordSearchPresetForm
            self.title = 'Create Keyword Search Preset'
        elif self.preset_type == 'amount_filter':
            self.form_class = AmountFilterPresetForm
            self.title = 'Create Amount Filter Preset'
        else:
            messages.error(request, f"Invalid preset type: {self.preset_type}", extra_tags='danger')
            return redirect('index')

        return super().dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['title'] = self.title
        return context

    def form_valid(self, form):
        preset = form.save(commit=False)
        preset.preset_type = self.preset_type if self.preset_type != 'keyword_search' else 'keyword'
        preset.save()
        messages.success(self.request, f"Preset '{preset.name}' created successfully")
        return redirect('index')

    
    
def delete_preset(request, id):
    try:
        preset = get_object_or_404(Preset, pk=id)
        preset.delete()
    except Http404:
        messages.error(request, f"Preset does not exist with id: {id}", extra_tags='danger')
    return redirect('index')


def clear_session(request):
    request.session.pop('dataframes')
    return redirect('index')
    
    
def results(request):
    session_dataframes = request.session.get('dataframes', [])
    if not session_dataframes:
        messages.warning(request, "No bank statements have been uploaded yet")
        return redirect('index')
    
    selected_preset_ids = request.GET.get('presets', '').split(',')
    selected_preset_ids = [int(id) for id in selected_preset_ids if id.isdigit()]
    
    if not selected_preset_ids:
        messages.warning(request, "No presets selected for analysis")
        return redirect('index')
    
    dataframes = []
    for df_dict in session_dataframes:
        df = pd.DataFrame.from_dict(df_dict)
        if 'Date' in df.columns:
            df['Date'] = pd.to_datetime(df['Date'])
        dataframes.append(df)
    
    if dataframes:
        combined_df = pd.concat(dataframes, ignore_index=True)
    else:
        messages.error(request, "Error reconstructing transaction data", extra_tags='danger')
        return redirect('index')
    
    results = []
    
    for preset_id in selected_preset_ids:
        try:
            preset = get_object_or_404(Preset, pk=preset_id)
            
            if preset.preset_type == 'date_range':
                analysis_result = analyze_date_range(
                    combined_df, preset.start_date, preset.end_date
                )
                
            elif preset.preset_type == 'keyword':
                analysis_result = analyze_keywords(combined_df, preset.keywords)
                
            elif preset.preset_type == 'amount_filter':
                analysis_result = analyze_amount_filter(
                    combined_df, preset.amount_value, preset.comparison_type
                )
                
            
            if analysis_result:
                results.append({
                    'preset': preset,
                    'result': analysis_result,
                })
            
        except Http404:
            messages.warning(request, f"Preset does not exist with id: {preset_id}")
        except Exception as e:
            messages.error(request, f"Error analyzing with preset '{preset.name}': {str(e)}", extra_tags='danger')
    
    
    context = {
        'results': results,
        'pdf_count': len(session_dataframes)
    }
    
    return render(request, 'results.html', context)

#618278372