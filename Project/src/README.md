# 💻 Source Code

All application source code is organized in this folder.

## 📂 Subfolders

### ☕ `java/`
Java-based Case-Based Reasoning (CBR) system implementation.

**Core Classes (6 total):**
- `CaseDescription.java` - Case data representation
- `CaseDatabase.java` - Database management
- `CaseSimilarityCalculator.java` - Similarity scoring (5-factor algorithm)
- `KNNRetriever.java` - K-Nearest Neighbor retrieval
- `MontenegrianLegalCBR.java` - Main CBR system
- `TestScenarios.java` - Test suite

**Total Lines:** 2,800+  
**All 13 Cases:** Fully loaded and tested

### 🌐 `web/`
Modern web interface for the CBR system.

**Components:**
- `server.js` - Express.js backend server
- `public/index.html` - HTML/CSS/JS frontend
- REST API for case querying
- Responsive design (desktop & mobile)

---

## 🚀 Running the System

### Java CBR System
```bash
# Compile
javac java/*.java

# Run tests
java MontenegrianLegalCBR
```

### Web Interface
```bash
# Install dependencies
npm install

# Start server
npm start

# Opens at http://localhost:3000
```

---

## 📋 Project Structure

| Component | Type | Files | LOC |
|-----------|------|-------|-----|
| Java System | Core Logic | 6 | 2,800+ |
| Web UI | Frontend | 2 | 800+ |
| **Total** | - | 8 | 3,600+ |

---

## 🎯 Architecture

**Java Backend:**
- Case representation and management
- Similarity calculation (5 factors)
- K-NN retrieval algorithm
- All 13 Montenegrian court verdicts

**Web Frontend:**
- Express.js REST API
- HTML/CSS/JS interface
- Real-time case retrieval
- Beautiful, responsive design

---

## ✅ Features

✅ 13 Complete Court Verdicts  
✅ 5-Factor Similarity Algorithm  
✅ K-Nearest Neighbor Retrieval  
✅ Web-Based Interface  
✅ REST API  
✅ Fully Tested & Working  

---

**Status:** ✅ Complete and ready to use  
**Last Updated:** Today
