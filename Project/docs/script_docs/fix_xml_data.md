# fix_xml_data.py

## Опис

Utility скрипта за **поправку и допуну** Akoma Ntoso XML фајлова. Чита сирове TXT фајлове
судских одлука из `archive/presude/` и аутоматски попуњава поља која недостају у
одговарајућим XML фајловима.

Такође исправља терминологију: "Uslovna osuda" → "Uslovna presuda" у `<vrstaPresude>` таговима.

## Локација

```
scripts/fix_xml_data.py
```

## Покретање

```powershell
py scripts/fix_xml_data.py
```

## Улаз и излаз

| Тип | Путања | Опис |
|-----|--------|------|
| Улаз (XML) | `data/cases/akomantoso/*.xml` | Akoma Ntoso XML фајлови |
| Улаз (TXT) | `archive/presude/falsifikovanje novca/*.txt` | Сирове пресуде (фалсификовање новца) |
| Улаз (TXT) | `archive/presude/falsifikovanje i zloupotreba.../*.txt` | Сирове пресуде (злоупотреба картица) |
| Излаз | `data/cases/akomantoso/*.xml` | Исти XML фајлови — директно ажурирани |

## Поља која се попуњавају

| Поље | Извор | Опис |
|------|-------|------|
| `sudija` | TXT | Име судије |
| `zapisnicar` | TXT | Име записничара |
| `ranijeOsudjivan` | TXT | Статус раније осуђиваности |
| `opisSlucaja` | TXT | Опис чињеничног стања |
| `kazna` | TXT | Текст изречене казне |
| `vrstaPresude` | TXT | Тип пресуде (осуђујућа/ослобађајућа/условна) |
| `dokazi` | TXT | Листа доказа из образложења |

## Кључне функције

| Функција | Опис |
|----------|------|
| `extract_judge()` | NLP екстракција имена судије из TXT текста |
| `extract_clerk()` | NLP екстракција имена записничара (10+ regex шаблона) |
| `extract_prior_convictions()` | Детектује "osuđivan"/"neosuđivan" у тексту |
| `extract_case_description()` | Екстрахује опис кривичног дјела ("Što je:..." секција) |
| `extract_evidence()` | Екстрахује доказе из Образложења (16 врста доказа) |
| `extract_sentence()` | Парсира казну (затвор, новчана, судска опомена) |
| `extract_verdict_type()` | Одређује тип пресуде |

## Напомена

Ово је **utility скрипта** која се покреће ручно када је потребно ажурирати XML податке.
Није дио runtime система — не позива је сервер аутоматски.
