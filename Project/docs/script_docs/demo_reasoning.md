# demo_reasoning.py

## Опис

Главна скрипта за **расуђивање по правилима** (rule-based reasoning) над кривичним предметима
из Главе 23 КЗ ЦГ (Кривична дјела против платног промета). Интегрише NLP екстракцију
чињеница, парсирање LegalRuleML правила, рачунање казни и опционалну интеграцију
са DR-Device алатом за дефизибилну логику.

## Локација

```
scripts/demo_reasoning.py
```

## Како се позива

Ова скрипта се **аутоматски покреће** из веб сервера (`web/server.js`) преко `child_process.spawn`
при сваком захтјеву за расуђивање по правилима. Може се покренути и ручно.

### Из веб сервера (аутоматски)
```
POST /api/reasoning  { "caseId": "100/10" }
```
Сервер пронађе XML фајл и покрене: `py scripts/demo_reasoning.py --case <path> --json`

### Ручно покретање
```powershell
# Појединачни случај
py scripts/demo_reasoning.py --case "data/cases/akomantoso/K 100_2010.xml" --json

# Са ручно задатим чињеницама (JSON формат)
py scripts/demo_reasoning.py --facts '{"tipKrivicnogDjela": "falsifikovanje novca"}' --json

# Са додатним правилима
py scripts/demo_reasoning.py --case <path> --rules "rule_reasoning/rules/legal_rules.xml" --json
```

## Аргументи

| Аргумент | Опис |
|----------|------|
| `--case` | Путања до Akoma Ntoso XML фајла предмета |
| `--facts` | JSON стринг са чињеницама (алтернатива XML фајлу) |
| `--rules` | Путања до LegalRuleML XML фајла са правилима |
| `--json` | Излаз у JSON формату (за интеграцију са сервером) |

## Кључне класе

| Класа | Опис |
|-------|------|
| `ArchiveFactsExtractor` | NLP екстракција додатних чињеница из архивских TXT фајлова |
| `RuleParser` | Парсирање LegalRuleML правила из `legal_rules.xml` |
| `CaseFactsExtractor` | Екстракција чињеница из Akoma Ntoso XML предмета |
| `SentenceCalculator` | Рачунање распона казни на основу утврђених чињеница и правила |
| `PenaltyRange` | Модел распона казне (минимум–максимум) |
| `DrDeviceReasoner` | Интеграција са DR-Device алатом за дефизибилну логику |

## Излаз (JSON)

```json
{
  "facts": { ... },
  "violated_rules": [ ... ],
  "penalties": [ ... ],
  "mitigating_circumstances": [ ... ],
  "aggravating_circumstances": [ ... ],
  "recommended_sentence": "...",
  "conditional_sentence_possible": true
}
```

## Зависности

- Python 3.8+
- Стандардна библиотека (xml, re, json, argparse, subprocess)
- DR-Device (опционално, за дефизибилну логику)
