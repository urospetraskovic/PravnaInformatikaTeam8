# Montenegrin Legal Case-Based Reasoning System

A web-based legal case analysis system featuring 127 Montenegrin court verdicts related to money falsification and credit card fraud (Glava 23, Criminal Code).

## Project Structure

```
├── src/web/                    # Main web application
│   ├── server.js              # Express.js server
│   └── public/                # Frontend UI
├── data/
│   ├── cases/
│   │   └── akomantoso/        # 127 case files in Akoma Ntoso XML format
│   ├── glava23/                # Criminal Code Chapter 23 excerpts
│   └── rules/                  # Rule base for reasoning engine
├── docs/                        # Documentation
├── archive/                     # Original source text files
├── dr-device/                   # AI reasoning infrastructure (untouched)
├── demo_reasoning.py           # Rule-based reasoning engine
├── package.json                # Node.js dependencies
└── node_modules/               # Installed dependencies
```

## Getting Started

### Prerequisites
- Node.js 14+
- npm (Node Package Manager)
- Python 3.6+ (optional, for reasoning engine)

### Installation

```bash
# Install dependencies
npm install
```

### Running the Application

```bash
# Start the server
npm start
```

The application will be available at `http://localhost:3000`

## Features

### Case Browser
- Browse all 127 Montenegrin court verdicts
- Filter by crime type (falsification vs. credit card fraud)
- Detailed case information including:
  - Court and judge information
  - Court clerk (Zapisničar)
  - Verdict type (Prison/Suspended/Acquitted/Warning)
  - Sentence details
  - Applicable Criminal Code articles
  - Evidence and case description

### Statistics Dashboard
- Total cases: 127
- Breakdown by verdict type:
  - **Zatvor** (Prison): 67 cases
  - **Uslovna** (Suspended/Conditional): 52 cases
  - **Oslobođen** (Acquitted): 7 cases
  - **Opomena** (Judicial Warning): 1 case

### Glava 23 Reference
- Browse Criminal Code Chapter 23 articles
- Link articles to relevant cases
- Reference legal framework

### Rule-Based Reasoning
- Analyze cases using defined legal rules
- Connect case facts to applicable articles
- Identify precedent cases

## API Endpoints

- `GET /api/cases` - List all cases
- `GET /api/cases/:id` - Get single case details
- `GET /api/statistics` - Get verdict statistics
- `GET /api/case-types` - Get case type categories
- `POST /api/reasoning` - Run reasoning engine on a case

## Data Format

Cases are stored in **Akoma Ntoso XML** format with Serbian legal metadata:
- Court names and judge information
- Verdict type classification
- Court clerk name
- Personal defendant information
- Applied Criminal Code articles
- Monetary amounts and sentences
- Evidence and case descriptions

## Development

The project consists of:
- **Frontend**: Vanilla JavaScript + HTML/CSS
- **Backend**: Express.js for API
- **Reasoning**: Python-based rule engine
- **Data Format**: Akoma Ntoso XML with custom Serbian extensions

## Notes

- Archive folder contains original source .txt files from court verdicts
- DR Device infrastructure is preserved but not currently integrated
- All scripts needed for initial data processing have been removed
- Project is optimized for displaying and analyzing court case data
