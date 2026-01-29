# 📊 Data & Database

All case data and export files are organized in this folder.

## 📂 Subfolders

### 💾 `cases/`
Case database and data files (CSV, JSON).

**Contents:**
- `DB/` - Database folder
  - `EXTRACTED_CASES_DATABASE.csv` - Cases in CSV format
  - `EXTRACTED_CASES_DATABASE.json` - Cases in JSON format

### 📤 `exports/`
Data export tools and utilities.

**Contents:**
- `CASE_DATABASE_STRUCTURED.py` - Python data processor
- `case_processor.py` - Case processing utility

---

## 🔍 What's Here

- **13 Montenegrian Court Verdicts** - All extracted and normalized
- **CSV Format** - Easy to import into Excel/Sheets
- **JSON Format** - Perfect for web/JavaScript integration
- **Python Tools** - For data processing and conversion

---

## 📝 File Details

**EXTRACTED_CASES_DATABASE.csv**
- 13 rows (one per verdict)
- 60+ columns (case details, dates, parties, etc.)
- Ready for analysis and importing

**EXTRACTED_CASES_DATABASE.json**
- Structured JSON format
- Nested data for complex fields
- Perfect for API integration

**Python Tools**
- `CASE_DATABASE_STRUCTURED.py` - Structured case database tool
- `case_processor.py` - Process and transform case data

---

## 💡 Usage

### View Cases
```bash
# Open CSV in Excel/Sheets
open cases/DB/EXTRACTED_CASES_DATABASE.csv

# Or parse JSON
cat cases/DB/EXTRACTED_CASES_DATABASE.json
```

### Process Data
```bash
# Use Python tool
python exports/case_processor.py
python exports/CASE_DATABASE_STRUCTURED.py
```

---

**Total Cases:** 13  
**Last Updated:** Today  
**Status:** ✅ Complete and organized
