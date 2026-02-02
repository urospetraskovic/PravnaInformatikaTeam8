# ТЕХНИЧКА ДОКУМЕНТАЦИЈА - СИСТЕМА ЗА ФАЛСИФИКОВАЊЕ

**Датум:** 1. фебруар 2026  
**Верзија:** 1.0  
**Статус:** Активна

---

## 📋 АРХИТЕКТУРА СИСТЕМА

### Слојеви:

```
┌─────────────────────────────────┐
│   Frontend (HTML/CSS/JS)        │ ← index.html (Сербски)
│   - Два панела (Cases/Glava23)  │
│   - Интерактивна навигација     │
└──────────────┬──────────────────┘
               ↑
┌──────────────┴──────────────────┐
│   Backend (Node.js/Express)     │ ← server.js
│   - API endpoints               │
│   - JSON cache                  │
└──────────────┬──────────────────┘
               ↑
┌──────────────┴──────────────────┐
│   Data Layer                    │
│   - JSON базе случајних         │
│   - XML (AkomaNtoso)            │
│   - CSV (табели)               │
└─────────────────────────────────┘
```

---

## 🔧 ИЗВЛАЧЕЊЕ И ПАРСИРАЊЕ

### Главни Парсер: `data/exports/advanced_verdict_parser.py`

#### Улаз:
- Текстуалне датотеке са суђењима из `archive/presude/`
- Два типа: фалсификовање новца vs. картица

#### Процес:

```python
1. Учитај текстуалне датотеке
   └─ Подели по "P R E S U D U" маркерима

2. За свако суђење:
   ├─ Екстрахуј основне податкe:
   │  ├─ Број случаја (K XXX/YYYY)
   │  ├─ Суд
   │  ├─ Датум
   │  └─ Врста случаја
   │
   ├─ Екстрахуј лица:
   │  ├─ Име окривљеног
   │  ├─ Место рођења
   │  ├─ Статус запослености
   │  └─ Финансијски статус
   │
   ├─ 🔑 КРИТИЧНО: Екстрахуј чланове:
   │  │  ← САМО артиклови из "čime je izvršio krivično djelo"
   │  │  ← ФИЛТРИРАЊЕ proceduralni артиклова (2,4,5,13...)
   │  └─ Резултат: 1-2 артиклова максимално
   │
   ├─ Екстрахуј детаље:
   │  ├─ Износ novčanice (20, 50, 200 EUR)
   │  ├─ Серијски бројеви
   │  ├─ Место случаја
   │  └─ Наративу
   │
   └─ Генериши три формата:
      ├─ AkomaNtoso XML
      ├─ JSON
      └─ CSV

3. Спај све в EXTRACTED_CASES_DATABASE.*
```

#### Кључна логика за артиклове:

```python
# Паттерн за детектовање правог артиклова:
crime_pattern = r'čime je izvršio (?:produženo )?krivično djelo\s+(?:falsifikovanje|..+?)\s+iz\s+čl\.?\s*(\d+)(?:\s+st\.?\s*(\d+))?'

# Пример суђења:
# "- čime je izvršio krivično djelo falsifikovanje novca iz čl.258 st.2 Krivičnog Zakonika."
# ↓ ИЗВУЧИ:
# Član 258 st.2 KZ CG ✅

# ИГНОРИШИ:
# "primjenom čl. 2,4,5,13,15,32,36,42,45,46 Krivičnog zakonika"
# ← То су proceduralni артиклови, НЕ криме
```

---

## 🗄️ ФОРМАТИ ЕКСПОРТА

### 1. AkomaNtoso XML

**Стандард:** Legal Document Markup Language  
**Верзија:** 3.0  
**Намена:** Архивирање и валидација

**Структура:**
```xml
<?xml version="1.0" encoding="UTF-8"?>
<judgment xmlns="http://docs.oasis-open.org/legaldocml/ns/akn/3.0">
  <meta>
    <identification>
      <FRBRWork>
        <!-- Метаподаци суђења -->
        <FRBRnumber value="K 258/12"/>
        <FRBRdate date="2012"/>
      </FRBRWork>
      <references>
        <!-- Хипервеза на чланове -->
        <TLCReference eId="ref_art_258" href="/akn/me/act/criminal-code/glava-23#258"/>
      </references>
    </identification>
  </meta>
  <body>
    <background><!-- Лица --></background>
    <narrative><!-- Инцидент --></narrative>
    <motivation><!-- Анализа --></motivation>
    <decision><!-- Пресуда --></decision>
  </body>
</judgment>
```

### 2. JSON

**Намена:** Апликациона база  
**Схема:**
```json
{
  "case_id": "Case_258_12",
  "case_number": "K 258/12",
  "court": "Osnovni Sud u Beogradu",
  "verdict_date": "2012",
  "defendant": { /* име, старост, статус */ },
  "incident": { /* наративу, место, дата */ },
  "legal": {
    "articles_charged": ["Član 258 st.2 KZ CG"],
    /* НЕ proceduralni артиклови! */
  },
  "verdict": { /* guilty, sentence */ }
}
```

### 3. CSV

**Намена:** Табелирни приказ  
**Редови:** Сваког суђења  
**Колоне:** case_id, court, verdict_date, articles_charged, guilty, sentence...

---

## 🌐 ФРОНТЕНД АРХИТЕКТУРА

### Два Панела:

#### Панел 1: Случајни суђења
```
┌─────────────────────────────────────┐
│ Случајни суђења      Глава 23 ← Tab │
└─────────────────────────────────────┘
┌──────────────┬─────────────────────┐
│   Sidebar    │   Main Content      │
│              │                     │
│ • Filter     │ ┌─────────────────┐ │
│ • Cases list │ │ Case K 258/12   │ │
│              │ │ Guilty          │ │
│              │ │ Court: Suva      │ │
│              │ │ Articles:        │ │
│              │ │ [Član 258 st.2] ← CLICKABLE
│              │ │                 │ │
│              │ └─────────────────┘ │
└──────────────┴─────────────────────┘
```

#### Панел 2: Глава 23
```
┌─────────────────────────────────────┐
│ Случајни суђења      Глава 23 ← Tab │
└─────────────────────────────────────┘
┌─────────────────────────────────────┐
│ ГЛАВА 23                            │
│ Чланови 258-263                     │
│                                     │
│ Члан 258 - Фалсификовање новца    │ ← ID="258"
│ (1) Ко направи лажан новац...     │
│                                     │
│ Члан 259 - Хартије од вредности   │ ← ID="259"
│ ...                                 │
│                                     │
│ [Scroll down to see more]          │
└─────────────────────────────────────┘
```

### Навигација:

```javascript
// Кад кориснику кликне артиклу:
function navigateToArticle(articleNum) {
  showPanel('glava23');           // Промени на Глава 23 панел
  
  setTimeout(() => {
    const element = document.getElementById(articleNum);  // Нађи члан
    element.scrollIntoView();      // Скролуј до њега
    element.highlight(2000);       // Хајлајти 2сек
  }, 100);
}
```

---

## 📡 API Endpoints

### Серверу (Node.js):

```
GET /api/cases
  Врати све случајне из JSON базе
  Резултат: Array[22 objects]

GET /api/statistics
  Врати агрегиране статистике
  Резултат: { totalCases, guiltyCount, acquittedCount, ... }

GET /api/search/type/:type
  Филтрирај по типу
  Резултат: Array[filtered cases]

GET /api/case/:id
  Врати детаље једног случаја
  Резултат: { case object with full data }
```

---

## 🔄 ПРОЦЕС ДОДАВАЊА НОВИХ СУЂЕЊА

### Ако имаш нове текстуалне датотеке:

1. **Постави текстуалне датотеке:**
   ```
   archive/presude/falsifikovanje novca/3.txt
   ```

2. **Покрени парсер:**
   ```bash
   cd data/exports
   python3 advanced_verdict_parser.py
   ```

3. **Проверить излаз:**
   - Нова XML фајла в `data/cases/akomantoso/`
   - Обновљени JSON и CSV в `data/exports/`

4. **Обнови базу:**
   ```bash
   cp data/exports/FALSIFICATION_CASES.json \
      data/cases/DB/EXTRACTED_CASES_DATABASE.json
   ```

5. **Рестартуј сервер:**
   ```bash
   npm start  # Аутоматски учитава нову базу
   ```

---

## 🎨 КОДИРАЊЕ И ЛОКАЛИЗАЦИЈА

### UTF-8 Суппорт:

```html
<!-- HTML Head: -->
<meta charset="UTF-8">
<meta http-equiv="Content-Type" content="text/html; charset=utf-8">

<!-- Резултат: -->
Član 258 ✅ (не "Clen")
Глава 23 ✅
Фалсификовање ✅
```

### Сербски Превод:

```javascript
// Пре:
"Filter by Type" → "Филтрирај по типу"
"Total Cases" → "Укупно случајних"
"Guilty" → "Крив"
"Acquitted" → "Ослобођен"
"Articles Charged" → "Члан/и по коме је окривљени кривичан"
```

---

## ⚠️ Могућа Питања и Решења

### П1: Парсер не екстрахује чланове
**Проблем:** Текст има другачиј формат  
**Решење:** Примени регекс и додај нови паттерн

```python
# Додај нови паттерн ако је потребно:
crime_pattern = r'вашИнови_паттерн_овде'
```

### П2: "Membre 258" место "Član 258"
**Проблем:** Кодирање није UTF-8  
**Решење:** Провери мету и читање датотеке

```python
with open(filepath, 'r', encoding='utf-8') as f:  # ← utf-8!
```

### П3: Хипервеза не ради
**Проблем:** HTML ID не постоји  
**Решење:** Проверити да ли су сви чланови у Главе 23:

```html
<div class="article" id="258">...</div>  <!-- мора ID -->
<div class="article" id="259">...</div>
```

---

## 📊 Статистике Система

```
Укупно суђења: 22
├─ Фалсификовање новца: 14
└─ Фалсификовање картица: 8

Чланови у Главе 23: 6
├─ Član 258: Фалсификовање новца
├─ Član 259: Хартије од вредности
├─ Član 260: Кредитне картице ← Захтева!
├─ Član 261: Знакови за вредност
├─ Član 262: Средства за фалсификовање
└─ Član 263: Чекови без покрића

Просечан број артиклова по суђењу: 1.2
```

---

## 📚 Референце

- **AkomaNtoso:** http://docs.oasis-open.org/legaldocml/akn/v3.0/
- **CSV:** RFC 4180
- **JSON:** RFC 8259
- **HTML5:** W3C Specification
- **JavaScript:** ES6+
- **Node.js:** v18+
- **Express:** v4+

---

**ДОКУМЕНТАЦИЈА ЗАВРШЕНА** ✅
