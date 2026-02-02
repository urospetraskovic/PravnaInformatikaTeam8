# Frontend Data Display Fix Guide

## Issues Identified and Fixed

### 1. **AKOmanToso File Path Mapping Issue** ✅ FIXED
**Problem**: The server was trying to fetch XML files using case IDs like "K 34/14", but the actual files are named "Case_34_14.xml"

**Solution**: Updated `/api/akomantoso/:caseId` endpoint in `server.js` to convert case ID format:
- Input: "K 34/14" → Extract "34" and "14" → Convert to "Case_34_14"
- This allows the server to correctly locate and serve XML files

**File Changed**: `src/web/server.js` (lines ~330-355)

### 2. **Frontend Panel Visibility Issue** ✅ FIXED
**Problem**: The Glava 23 panel wouldn't display properly when clicked

**Solution**: 
- Added proper CSS positioning for panels (absolute positioning within app-wrapper)
- Updated `.panel` and `.glava-panel` CSS classes with correct z-index and positioning
- Ensured panels overlay correctly with z-index: 50

**Files Changed**: `src/web/public/index.html` (CSS section, lines ~460-490)

### 3. **App Wrapper Layout Issue** ✅ FIXED  
**Problem**: The app-wrapper wasn't properly containing absolutely positioned elements

**Solution**: Added `position: relative;` to `.app-wrapper` CSS so absolute positioning works correctly

**File Changed**: `src/web/public/index.html` (line ~24)

---

## How the Data Flow Works Now

```
1. User opens frontend (http://localhost:3000)
   ↓
2. loadCases() fetches /api/cases → loads JSON data from database
   ↓
3. Cases display in sidebar with filtering
   ↓
4. User clicks on a case
   ↓
5. displayCase() fetches /api/akomantoso/{caseId} → XML file
   ↓
6. XML is parsed to extract:
   - Case metadata (court, type, verdict)
   - Articles (from TLCReference tags)
   - Applicable law details
   ↓
7. Articles are made clickable → navigateToArticle()
   ↓
8. User clicks on article number
   ↓
9. Frontend switches to Glava 23 tab and scrolls to article
   ↓
10. Article highlights briefly (yellow background), then returns to normal
```

---

## Key Features Now Working

### ✅ Data Display
- Cases load from JSON database
- XML metadata displays correctly
- All case fields render properly

### ✅ Article Navigation
- Clickable article tags show up in case details
- Clicking an article:
  1. Switches to "Glava 23 - Krivični kodeks" tab
  2. Scrolls to the specific article
  3. Highlights the article with yellow background
  4. Auto-highlights fade after 2 seconds

### ✅ Tab Switching
- "📋 Presude" tab shows all cases
- "📖 Glava 23 - Krivični kodeks" tab shows complete criminal code

### ✅ Filtering
- Filter cases by type using dropdown
- Shows count of cases per type

### ✅ Statistics
- Total cases counter
- Guilty verdict counter
- Acquitted verdict counter

---

## Testing the Frontend

### Step 1: Start the Server
```bash
cd src/web
npm install  # If not already done
npm start
```

The server will start at `http://localhost:3000`

### Step 2: Verify Data Loading
1. Open browser console (F12 → Console)
2. Check for any errors (should see "✅ Successfully loaded X cases")
3. Cases list should populate in the left sidebar

### Step 3: Test Case Selection
1. Click on any case in the sidebar
2. Case details should appear in the main content area
3. Should see: Court, Type, Sentence, Year, Defendant, Victim, Articles, Evidence

### Step 4: Test Article Navigation
1. Click on an article tag (blue clickable tag)
2. Should automatically switch to "Glava 23 - Krivični kodeks" tab
3. Should scroll to the specific article
4. Article should highlight with yellow background

### Step 5: Test Tab Switching
1. Click "Glava 23 - Krivični kodeks" button at top
2. Should see full criminal code (Glava 23) content
3. Articles 258-286 should display with proper formatting

### Step 6: Test Filtering
1. Use "Filter by type" dropdown
2. Should only show cases of selected type
3. Count should update

---

## File Locations Reference

| Component | File |
|-----------|------|
| Frontend UI | `src/web/public/index.html` |
| Backend Server | `src/web/server.js` |
| Case Database (JSON) | `data/cases/DB/EXTRACTED_CASES_DATABASE.json` |
| AKOmanToso Files | `data/cases/akomantoso/*.xml` |
| Sample AKOmanToso | `archive/exercise_materials/vezbe/01 Вежбе/02_ZBSP_akn.xml` |

---

## AKOmanToso File Structure Reference

Each case's XML file should follow this structure:

```xml
<?xml version="1.0" encoding="UTF-8"?>
<judgment xmlns="...">
  <meta>
    <identification source="court">
      <FRBRWork>
        <FRBRthis value="/akn/me/judgment/{case_id}/!main"/>
        <FRBRuri value="/akn/me/judgment/{case_id}"/>
        <FRBRdate date="{verdict_date}"/>
        <FRBRnumber value="{case_number}"/>
        <FRBRname value="{case_type}"/>
      </FRBRWork>
      <!-- ... more metadata ... -->
    </identification>
    <references source="application">
      <!-- Article references like: -->
      <TLCReference eId="ref_Clan_258" href="/akn/me/act/criminal-code/glava-23#Clan 258" showAs="Clan 258"/>
    </references>
  </meta>
  <body>
    <background>
      <p><strong>Sud:</strong> {court}</p>
      <p><strong>Broj predmeta:</strong> {case_number}</p>
      <!-- ... more background ... -->
    </background>
    <!-- ... more sections ... -->
  </body>
</judgment>
```

---

## Common Issues and Solutions

### Issue: Cases not loading
**Solution**: 
1. Check browser console for errors
2. Ensure `data/cases/DB/EXTRACTED_CASES_DATABASE.json` exists
3. Check server console: should show "✅ Successfully loaded X cases"

### Issue: AKOmanToso XML not found
**Solution**:
1. Check that XML file exists in `data/cases/akomantoso/`
2. Verify file naming matches format: `Case_XX_YY.xml`
3. Check server console for: "AkomaNtoso file not found: {path}"

### Issue: Glava 23 tab doesn't show content
**Solution**:
1. Open browser developer tools (F12)
2. Check Console for any JavaScript errors
3. Check if panel CSS is working: `#glava23-panel.active` should be visible
4. Try clicking "Glava 23" button again

### Issue: Article clicks don't navigate
**Solution**:
1. Verify article tags are being rendered (should be blue clickable tags)
2. Check that article IDs in Glava 23 section match (e.g., `id="258"`)
3. Open console, click article, check if `navigateToArticle()` is called
4. Verify Glava 23 has articles with IDs 258-286

---

## Next Steps for Full Implementation

### To Generate AKOmanToso Files from Verdicts:
```bash
python generate_akomantoso.py
```

### To Regenerate AKOmanToso Files with New Cases:
1. Update `data/cases/DB/EXTRACTED_CASES_DATABASE.json`
2. Run: `python generate_akomantoso.py`
3. Restart server
4. Refresh browser

### To Add More Articles to Glava 23:
1. Edit the HTML article section in `src/web/public/index.html`
2. Follow the existing format:
```html
<div class="article" id="258">
  <div class="article-number">Član 258 - Article Title</div>
  <div class="article-content">
    <!-- article text here -->
  </div>
</div>
```

### To Customize Case Display:
1. Modify `displayCase()` function in JavaScript
2. Update fields in the case detail template
3. Add more metadata from the XML file as needed

---

## Architecture Overview

```
Frontend (Single Page Application)
├── Navigation Tabs (top)
├── Left Sidebar (cases list & filter)
├── Main Content Area
│   ├── Panel 1: Case Details (with clickable articles)
│   └── Panel 2: Glava 23 (full criminal code)
│
Backend (Node.js Express)
├── API Routes
│   ├── GET /api/cases → all cases
│   ├── GET /api/statistics → case statistics
│   ├── GET /api/akomantoso/:caseId → XML for case
│   └── GET /api/search/type/:type → filtered cases
│
Data Files
├── JSON Database (extracted cases)
└── AKOmanToso XML Files (case documents)
```

---

## Debugging Checklist

- [ ] Server starts without errors
- [ ] `http://localhost:3000` loads the UI
- [ ] Cases appear in sidebar
- [ ] Clicking a case shows details
- [ ] Article tags are clickable (blue)
- [ ] Glava 23 tab switches properly
- [ ] Clicking article navigates to code section
- [ ] Article highlight works
- [ ] Filtering by type works
- [ ] Statistics display correct numbers

---

**Last Updated**: February 2, 2026
**Status**: Frontend display and navigation system fixed
