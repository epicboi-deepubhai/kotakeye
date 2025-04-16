# Kotakeye

## Overview
Kotakeye is a financial analysis application that extracts and processes data from bank statements to provide tailored statistics and visualizations. The application can parse PDF bank statements, analyze transactions, and generate insights based on user-defined criteria.

## Features
- PDF statement extraction to pandas DataFrame
- Customizable statistical analysis based on:
  - Date ranges
  - Keyword searches in transaction descriptions
  - Amount-based comparisons
- Visualization of financial data through charts
- Persistent preset storage for repeated analyses
- User-friendly web interface built with Django

## Technical Architecture
- **Backend**: Django framework
- **Data Processing**: Pandas for DataFrame manipulation
- **Data Visualization**: Matplotlib/Pandas plotting functionality
- **Data Storage**: SQLite database (for presets only)
- **Authentication**: Uses Kotak's CRN number for verification

## PDF Extractor Script

The repository includes a standalone PDF extraction script that converts bank statements to CSV files:

### Using the PDF Extractor
```bash
python pdfextractor.py [statement_file] [crn_number] [output_name]
```

Example:
```bash
python pdfextractor.py statement.pdf [your_crn] march-statement
```

This will generate a CSV file in the 'results' directory.

## Installation

```bash
# Clone the repository
git clone https://github.com/yourusername/kotakeye.git
cd kotakeye

# Create and activate virtual environment
python -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# Install dependencies
pip install -r requirements.txt

# Run migrations
python manage.py migrate

# Start the development server
python manage.py runserver
```

## Usage

### Google Colab Notebook
For data exploration and testing, you can use my Colab notebook: [Kotakeye](https://colab.research.google.com/drive/1ZvAd2Ulziia-3ThsWW2vukeBD2fw15ns?authuser=1#scrollTo=KHBklVO89xaB)

### Django Web Application

1. Upload your bank statement PDFs
2. Enter your Kotak CRN number for authentication
3. Create analysis presets or use existing ones:
   - Date range presets
   - Keyword search presets
   - Amount comparison presets
4. Select presets and click "Analyze Bank Statements"
5. View statistical results and visualizations

## Data Privacy
- Bank statements are processed in-memory and not stored permanently
- Only analysis presets are saved to the database
- No sensitive transaction data is retained after the session ends



## Dependencies
- pdfplumber
- pandas
- Django
- matplotlib

## Contribution
Contributions are welcome! 
You can update the regex pattern to match your own Bank's statement and submit a pull request.
We can add a Bank dropdown to select whichever bank statements are to be processed.


---

## 👨‍💻 Author
Developed by [epicboi-deepubhai](https://github.com/epicboi-deepubhai)