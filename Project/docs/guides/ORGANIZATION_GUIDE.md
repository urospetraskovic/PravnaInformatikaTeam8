# 📁 Project Organization Guide

## Clean Directory Structure

```
Project/
│
├── 📄 README.md                          ← START HERE!
├── 📄 package.json                       ← Node.js config
├── 🚀 setup.bat                          ← Windows: Run to start
├── 🚀 setup.sh                           ← Mac/Linux: Run to start
│
├── 📁 src/                              (Source Code)
│   ├── 📁 java/                         (Java Implementation)
│   │   ├── CaseDescription.java
│   │   ├── CaseDatabase.java
│   │   ├── CaseSimilarityCalculator.java
│   │   ├── KNNRetriever.java
│   │   ├── MontenegrianLegalCBR.java
│   │   └── TestScenarios.java
│   │
│   └── 📁 web/                          (Web UI)
│       ├── server.js                    (Express server)
│       ├── 📁 public/
│       │   └── index.html               (Beautiful UI)
│       └── package.json
│
├── 📁 data/                             (Case Data)
│   ├── EXTRACTED_CASES_DATABASE.csv     (Excel format)
│   ├── EXTRACTED_CASES_DATABASE.json    (JSON format)
│   └── CASE_DATABASE_STRUCTURED.py      (Python utility)
│
├── 📁 docs/                             (Documentation)
│   ├── START_HERE.md
│   ├── INDEX.md
│   ├── QUICK_REFERENCE_GUIDE.md
│   ├── JCOLIBRI_INTEGRATION_MANUAL.md
│   ├── JCOLIBRI_IMPLEMENTATION_COMPLETE.md
│   ├── COMPLETE_DELIVERABLES_SUMMARY.md
│   ├── FILE_MANIFEST.md
│   ├── PROJECT_COMPLETION_DASHBOARD.md
│   └── FINAL_SUMMARY.md
│
└── 📁 archive/                          (Old Exercise Materials)
    ├── EXTRACTED_MOBBING_CASES.txt
    ├── MOBBING_CASES_DATA.txt
    ├── VERDICT_EXTRACTION_GUIDE.txt
    ├── mobing krivicno.txt
    ├── mobbing presude u jedan veliki txt.txt
    ├── sve vezbe txt.txt
    ├── EXTRACTED_CASES_DATABASE.csv
    ├── EXTRACTED_CASES_DATABASE.json
    ├── EXTRACTION_COMPLETE_SUMMARY.md
    ├── PROJECT_STATUS_REPORT.txt
    └── 📁 vezbe/                        (Exercise files)
        ├── vezbe 1.docx
        ├── vezbe 2.docx
        ├── vezbe 3.docx
        └── vezbe 4.docx
```

---

## What Each Folder Contains

### 📁 `src/java/` - Java Implementation
**6 production classes (2,800+ lines)**
- Core case-based reasoning system
- All 13 cases fully loaded
- Similarity matching algorithm
- K-NN retrieval engine
- Test scenarios
- CLI application

**Compile & Run:**
```bash
cd src/java
javac *.java
java MontenegrianLegalCBR
```

### 📁 `src/web/` - Web UI
**Modern Express.js web server + Beautiful HTML/CSS/JS interface**
- No external UI framework (vanilla JS)
- Responsive design
- Real-time case search
- Statistics dashboard
- REST API backend

**Start Server:**
```bash
npm install
npm start
```

### 📁 `data/` - Case Data
**Case database in multiple formats**
- CSV (for Excel/databases)
- JSON (for web/APIs)
- Python utility for conversion
- All 13 Montenegrian verdicts

### 📁 `docs/` - Complete Documentation
**8 comprehensive guides (32,500+ words)**
- User guides
- Integration manuals
- Technical references
- Quick start guides
- Full feature inventory

### 📁 `archive/` - Old Materials
**Exercise files and previous work**
- Safely organized for reference
- Not needed for running system
- Keep for project history

---

## 🚀 How to Run (Pick One)

### **Option 1: Web UI (Easiest)**
```bash
npm install
npm start
# Opens http://localhost:3000 automatically
```

### **Option 2: Quick Setup Script**

**Windows:**
```bash
setup.bat
# Installs everything and starts server
```

**Mac/Linux:**
```bash
bash setup.sh
# Installs everything and starts server
```

### **Option 3: Java CLI**
```bash
cd src/java
javac *.java
java MontenegrianLegalCBR
# Interactive menu in terminal
```

---

## 📊 Which UI Should You Use?

| Aspect | Web UI | CLI |
|--------|--------|-----|
| **Ease of Use** | ⭐⭐⭐⭐⭐ | ⭐⭐⭐ |
| **Visual Appeal** | ⭐⭐⭐⭐⭐ | ⭐⭐ |
| **Performance** | Fast | Very Fast |
| **Mobile Access** | ✅ Yes | ❌ No |
| **Learning Curve** | None | Minimal |
| **Recommended** | **YES** | For advanced users |

**Recommendation:** Use the **Web UI** (it's better!)

---

## 🎯 Quick Navigation

### "I want to start RIGHT NOW"
1. Open terminal/PowerShell
2. Go to project folder
3. Run: `npm install && npm start`
4. Done! Browser opens automatically

### "I want to use the CLI"
1. Go to: `src/java/`
2. Run: `javac *.java`
3. Run: `java MontenegrianLegalCBR`
4. Follow menu

### "I want to understand the code"
1. Read: `docs/START_HERE.md`
2. Read: `docs/QUICK_REFERENCE_GUIDE.md`
3. Browse: `src/java/` (code is well-commented)

### "I want to integrate with jCOLIBRI"
1. Read: `docs/JCOLIBRI_INTEGRATION_MANUAL.md`
2. Follow: Step-by-step migration guide

---

## 📝 File Organization Benefits

✅ **Clear separation of concerns**
- Java code in `src/java/`
- Web code in `src/web/`
- Data in `data/`
- Documentation in `docs/`

✅ **Easy to find things**
- No clutter in root directory
- Logical folder structure
- Related files together

✅ **Professional appearance**
- Clean project layout
- Industry standard structure
- Easy for team collaboration

✅ **Better version control**
- Clear what's important
- Archive doesn't clutter main repo
- Easy to add `.gitignore`

---

## 🔧 To Add More Cases

1. Edit: `src/java/CaseDatabase.java`
2. Find: `loadAllCases()` method
3. Add new case:
   ```java
   CaseDescription newCase = new CaseDescription();
   newCase.setCaseNumber("K XXX/YYYY");
   newCase.setCaseType("Case Type");
   // ... set other fields ...
   caseList.add(newCase);
   ```
4. Recompile: `javac CaseDatabase.java`
5. Restart server

---

## 🎨 To Customize Web UI

Edit: `src/web/public/index.html`

Change:
- Colors (search for `#667eea`)
- Fonts (search for `font-family`)
- Layout (search for `display: grid`)
- Text (search for labels)

---

## ✅ Verification Checklist

- [ ] `src/java/` contains 6 Java files
- [ ] `src/web/` contains server.js and index.html
- [ ] `data/` contains CSV and JSON files
- [ ] `docs/` contains 8 documentation files
- [ ] `README.md` is in root
- [ ] `package.json` is in root
- [ ] `setup.bat` and `setup.sh` are in root

If all ✅, your project is **perfectly organized!**

---

## 🎉 You're All Set!

Everything is organized and ready to use.

**Next step:** Run `npm install && npm start` to start the web UI!

---

*Project organized: January 29, 2026*  
*Team: Pravna Informatika - Team 8*
