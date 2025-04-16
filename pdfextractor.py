import pdfplumber
import pandas as pd
import re


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


if __name__ == '__main__':
    import os
    import sys
    
    os.makedirs('results', exist_ok=True)
    
    _, file, crn, result_name = sys.argv
    
    df = get_pdf_df(file, crn)
    df.to_csv(f'results/{result_name}.csv')