from io import BytesIO
from datetime import date
import pdfplumber
import pandas as pd
import re
import base64


def get_pdf_df(pdf_file, password=None):
    pdf = pdfplumber.open(pdf_file, password=password)
    transactions = list()
    
    for page in pdf.pages:
        text = page.extract_text()
        
        pattern = r'(\d{2}-\d{2}-\d{4})\s+(.*?)\s+(\S+?)\s+([0-9,.]+\([DrC]+\))\s+([0-9,.]+\([DrC]+\))'
        
        matches = re.findall(pattern, text)
        
        for match in matches:
            date, narration, reference, amount, balance = match
            
            amount_val = float(amount.split('(')[0].replace(',',''))
            is_withdrawal = '(Dr)' in amount
            withdrawal = amount_val if is_withdrawal else 0
            deposit = amount_val if not is_withdrawal else 0
            
            balance_val = float(balance.split('(')[0].replace(',',''))
            
            transactions.append({
                'Date': date,
                'Narration': narration.strip(),
                'Reference': reference,
                'Withdrawal': withdrawal,
                'Deposit': deposit,
                'Balance': balance_val
            })
    pdf.close()
    
    if not transactions:
        return None
    
    df = pd.DataFrame(transactions)
    df['Date'] = pd.to_datetime(df['Date'], format='%d-%m-%Y')
    return df

def filter_date_range(df, start_date, end_date):
    if isinstance(start_date, date):
        start_date = pd.to_datetime(start_date, format='%d-%m-%Y')
    if isinstance(end_date, date):
        end_date = pd.to_datetime(end_date, format='%d-%m-%Y')
    
    return df[(df['Date'] >= start_date) & (df['Date'] <= end_date)]

def filter_keyword(df, keywords):
    ret_df = df[df['Narration'].str.contains('|'.join(keywords), case=False)].copy()
    ret_df['Keyword'] = ret_df['Narration'].apply(lambda x: ', '.join([k for k in keywords if k.lower() in x.lower()]))
    ret_df = ret_df.drop(['Reference', 'Balance'], axis=1) 
    return ret_df


def amount_filter(df, amount, comparison_type):
      if comparison_type == 'eq':
        return (df[(df['Withdrawal'] == amount) | (df['Deposit'] == amount)], 
                f"equal to {amount}")
        
      elif comparison_type == 'lt':
          return (df[(df['Withdrawal'] < amount) & (df['Withdrawal'] > 0) | 
                          (df['Deposit'] < amount) & (df['Deposit'] > 0)],
                  f"less than {amount}")
      elif comparison_type == 'gt':
          return (df[(df['Withdrawal'] > amount) | (df['Deposit'] > amount)],
                  f"greater than {amount}")
      else:
          return None
      
      
def analyze_date_range(df, start, end):
    if df is None or df.empty:
        return None
    
    filtered_df = filter_date_range(df, start, end)
    
    if filtered_df.empty:
        return {
            'transaction_count': 0,
            'total_withdrawal': 0,
            'total_deposit': 0,
            'net_flow': 0,
            'transactions': filtered_df.to_dict('records'),
            'chart': None
        }
    
    daily_totals = filtered_df.groupby(filtered_df['Date'].dt.date).agg({
        'Withdrawal': 'sum',
        'Deposit': 'sum'
    })

    ax = daily_totals.plot.bar(
        width=0.8,
        figsize=(10, 5),
        alpha=0.6,
        stacked=False  
    )

    ax.set_title('Daily Transaction Flow')
    ax.set_xlabel('Date')
    ax.set_ylabel('Amount')
    ax.legend(['Deposits', 'Withdrawals'])
    
    buffer = BytesIO()
    ax.figure.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return {
        'transaction_count': len(filtered_df),
        'total_withdrawal': filtered_df['Withdrawal'].sum(),
        'total_deposit': filtered_df['Deposit'].sum(),
        'net_flow': filtered_df['Deposit'].sum() - filtered_df['Withdrawal'].sum(),
        'transactions': filtered_df.to_dict('records')[:10],
        'chart': chart_image
    }
    

def analyze_keywords(df, keywords:str):
    if df is None or df.empty or not keywords:
        return None
    
    keyword_list = [k.strip().lower() for k in keywords.split(',') if k.strip()]
    
    if not keyword_list:
        return None
    
    filtered_df = filter_keyword(df, keyword_list)
    
    if filtered_df.empty:
        return {
            'transaction_count': 0,
            'total_withdrawal': 0,
            'total_deposit': 0,
            'net_flow': 0,
            'keywords': keyword_list,
            'transactions': [],
            'chart': None
        }
    
    distribution = filtered_df.groupby('Keyword').agg({
    'Withdrawal': 'sum',
    'Deposit': 'sum'
    })  
    
    ax = distribution.plot.bar(
    width=0.8,
    figsize=(10, 5),
    alpha=0.6,
    stacked=False,
    color = ['red', 'blue']
    )

    ax.set_title('Daily Transaction Flow')
    ax.set_xlabel('Keyword')
    ax.set_ylabel('Amount')
    
    buffer = BytesIO()
    ax.figure.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    keyword_stats = [{
        'keyword': keyword,
        'count': len(filtered_df[filtered_df['Keyword'] == keyword]),
        'withdrawal': distribution.loc[keyword, 'Withdrawal'],
        'deposit': distribution.loc[keyword, 'Deposit']
    } for keyword in keyword_list]
            
    return {
        'transaction_count': len(filtered_df),
        'total_withdrawal': filtered_df['Withdrawal'].sum(),
        'total_deposit': filtered_df['Deposit'].sum(),
        'net_flow': filtered_df['Deposit'].sum() - filtered_df['Withdrawal'].sum(),
        'keywords': keyword_list,
        'keyword_stats': keyword_stats,
        'transactions': filtered_df.to_dict('records')[:10],
        'chart': chart_image
    }
    
    
def analyze_amount_filter(df, amount, comparison_type):
    if df is None or df.empty:
        return None
    try:
        filtered_df, comparison_text = amount_filter(df, amount, comparison_type)
    except TypeError:
        return None
    
    if filtered_df.empty:
        return {
            'transaction_count': 0,
            'total_withdrawal': 0,
            'total_deposit': 0,
            'net_flow': 0,
            'comparison_text': comparison_text,
            'transactions': [],
            'chart': None
        }
    all_amounts = []
    all_amounts.extend(filtered_df[filtered_df['Withdrawal'] > 0]['Withdrawal'].tolist())
    all_amounts.extend(filtered_df[filtered_df['Deposit'] > 0]['Deposit'].tolist())

    amounts_series = pd.DataFrame(all_amounts)
    # ax = filtered_df[['Withdrawal', 'Deposit']].plot.hist(alpha=0.7, figsize=(10, 5), stacked=False)
    # print(filtered_df[['Withdrawal', 'Deposit']])
    ax = amounts_series.plot.hist(bins=20, alpha=0.7, figsize=(10, 5), legend=False)

    ax.axvline(x=amount, color='r', linestyle='--', label=f'Filter amount: {amount}')
    ax.set_title(f'Distribution of Transaction Amounts {comparison_text}')
    ax.set_xlabel('Amount')
    ax.set_ylabel('Frequency')
    handles, labels = ax.get_legend_handles_labels()
    ax.legend(handles=handles[1:], labels=labels[1:])
    
    buffer = BytesIO()
    ax.figure.savefig(buffer, format='png')
    buffer.seek(0)
    chart_image = base64.b64encode(buffer.getvalue()).decode('utf-8')
    
    return {
        'transaction_count': len(filtered_df),
        'total_withdrawal': filtered_df['Withdrawal'].sum(),
        'total_deposit': filtered_df['Deposit'].sum(),
        'net_flow': filtered_df['Deposit'].sum() - filtered_df['Withdrawal'].sum(),
        'comparison_text': comparison_text,
        'transactions': filtered_df.to_dict('records')[:10],
        'chart': chart_image
    }