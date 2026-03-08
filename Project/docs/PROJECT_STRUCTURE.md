# Структура пројекта

```
Project/
├── web/                              # Express веб апликација
│   ├── server.js                     # Node.js сервер (порт 3000)
│   ├── package.json                  # npm зависности
│   └── public/                       # Статички фајлови (index.html)
│
├── scripts/                          # Python скрипте
│   ├── demo_reasoning.py             # Расуђивање по правилима (NLP + DR-Device)
│   ├── extract_cases_to_csv.py       # Генерише presude.csv из XML случајева
│   ├── fix_xml_data.py               # Поправка XML фајлова
│   ├── audit_and_fix_xml.py          # Аудит и поправка XML структуре
│   └── mine_archive_data.py          # Екстракција података из архиве
│
├── rule_reasoning/                   # Расуђивање по правилима
│   ├── dr-device/                    # DR-Device алат (CLIPS-based)
│   └── rules/                        # LegalRuleML правила и онтологија
│       ├── legal_rules.xml           # 20 правила у LegalRuleML формату
│       ├── drdevice_rules.ddr        # DR-Device Defeasible Logic правила
│       ├── legal_ontology.n3         # RDF/N3 онтологија
│       ├── facts.xml                 # Шаблон за унос чињеница
│       └── facts_example.xml         # Примјер попуњених чињеница
│
├── case_reasoning/                   # Расуђивање по случајевима
│   └── presude-cbr/                  # jCOLIBRI CBR Java пројекат
│       ├── pom.xml                   # Maven конфигурација
│       └── src/main/
│           ├── java/                 # CBR изворни кôд
│           └── resources/presude.csv # База случајева (127 записа)
│
├── data/                             # Подаци
│   ├── cases/akomantoso/             # 127 Akoma Ntoso XML судских одлука
│   └── glava23/criminal_code.xml     # Текст Главе 23 КЗ ЦГ
│
├── archive/                          # Архивски материјали (вјежбе, пресуде)
│
├── docs/                             # Документација
│   ├── PROJECT_STRUCTURE.md          # Овај документ
│   ├── RULE_BASED_REASONING.md       # Расуђивање по правилима
│   |── CASE_BASED_REASONING.md       # Расуђивање по случајевима
|   └── scrip_docs/
│       ├── demo_reasoning          # main rule based reasoning engine
│       ├── extract_cases_to_csv    # generates presude.csv for CBR system
│       ├── fix_xml_data            # fills missing XML data from archive txt files
│       ├── audit_and_fix_xml       # Diagnostic audit of XML data quality
│       └── mine_archive_data       # mines peresonal data from archive texts into XML
|        
└── .gitignore
```

## Покретање

### Веб апликација
```powershell
cd web
npm install
npm start
```
Апликација је доступна на http://localhost:3000

### Python скрипте
```powershell
# Расуђивање по правилима (покреће се аутоматски из web сервера)
py scripts/demo_reasoning.py

# Генерисање CSV базе из XML случајева
py scripts/extract_cases_to_csv.py
```
