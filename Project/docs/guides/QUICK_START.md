# ⚡ 5-MINUTE SETUP GUIDE

## Goal
Get the Legal CBR System running in 5 minutes

---

## 🪟 **Windows Users**

### Step 1: Open PowerShell
Right-click on desktop → "Open PowerShell here"

### Step 2: Run Setup Script
```powershell
.\setup.bat
```

**That's it!** 🎉

The script will:
- ✅ Check for Node.js
- ✅ Install dependencies
- ✅ Start the web server
- ✅ Open browser to http://localhost:3000

---

## 🍎 **Mac Users**

### Step 1: Open Terminal
`Command` + `Space` → type "terminal" → Enter

### Step 2: Navigate to Project
```bash
cd /path/to/Project
```

### Step 3: Make Script Executable
```bash
chmod +x setup.sh
```

### Step 4: Run Setup
```bash
./setup.sh
```

**That's it!** 🎉

---

## 🐧 **Linux Users**

### Step 1: Open Terminal

### Step 2: Navigate to Project
```bash
cd /path/to/Project
```

### Step 3: Make Script Executable
```bash
chmod +x setup.sh
```

### Step 4: Run Setup
```bash
./setup.sh
```

**That's it!** 🎉

---

## Manual Setup (If Scripts Don't Work)

### Step 1: Install Node.js
Download from: https://nodejs.org/

### Step 2: Open Terminal/PowerShell in Project Folder

### Step 3: Install Dependencies
```bash
npm install
```

### Step 4: Start Server
```bash
npm start
```

### Step 5: Open Browser
Go to: http://localhost:3000

---

## 🎯 What You'll See

### Dashboard
- 📊 Statistics (13 cases, guilty verdicts, etc.)
- 🔍 Search interface
- 📋 Results panel

### Search
- Search by type (e.g., "Workplace Harassment")
- View all cases
- Click any case for details

### Case Details
- Complete case information
- Verdict, sentence, evidence
- Articles, harm level, year

---

## ✨ Features

✅ Beautiful web interface  
✅ Search 13 Montenegrian cases  
✅ Intelligent matching  
✅ Real-time results  
✅ Statistics dashboard  
✅ Works on desktop and mobile  

---

## 🐛 Troubleshooting

### "Port 3000 already in use"
```bash
PORT=3001 npm start
# Opens http://localhost:3001 instead
```

### "Node not found"
- Install Node.js from nodejs.org
- Close and reopen terminal
- Try again

### "npm command not found"
- Restart computer (Node install may need it)
- Or manually install from nodejs.org

### Page won't load
- Make sure server is running
- Check URL: http://localhost:3000
- Refresh browser (Ctrl+R or Cmd+R)

---

## 📱 Mobile Access

If you want to access from another device:

1. Find your computer's IP:
   ```bash
   ipconfig          # Windows
   ifconfig          # Mac/Linux
   ```

2. Use: `http://YOUR_IP:3000`

Example: `http://192.168.1.5:3000`

---

## 💾 Alternatives

### Want to use Java CLI instead?

```bash
cd src/java
javac *.java
java MontenegrianLegalCBR
```

Then use the menu.

---

## 🎓 Next Steps

1. **Explore the system:**
   - Search for "Workplace Harassment"
   - View K 98/2018 (stalking case)
   - Check statistics

2. **Read documentation:**
   - `docs/START_HERE.md` (5 min)
   - `docs/QUICK_REFERENCE_GUIDE.md` (20 min)

3. **Integration (optional):**
   - `docs/JCOLIBRI_INTEGRATION_MANUAL.md`

---

## 📞 Help

### Quick Questions
→ `docs/QUICK_REFERENCE_GUIDE.md`

### How It Works
→ `docs/JCOLIBRI_IMPLEMENTATION_COMPLETE.md`

### All Files
→ `ORGANIZATION_GUIDE.md`

---

## ✅ Success Indicators

✅ Server starts without errors  
✅ Browser opens automatically  
✅ Dashboard loads with statistics  
✅ Search finds cases  
✅ Case details display  

If all work → **You're ready to go!** 🚀

---

**That's it! Enjoy the system.** ✨

*Setup time: ~5 minutes*  
*Running time: Forever (or until you stop it)*
