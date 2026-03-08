# extract_cases_to_csv.py

## Опис

Скрипта за **екстракцију података** из свих Akoma Ntoso XML судских одлука и генерисање
CSV фајла (`presude.csv`) који служи као база случајева за jCOLIBRI CBR систем.

Парсира свих 127 XML докумената, нормализује вриједности (суд, врста дјела, запосленост,
образовање, брачни статус итд.) и записује стандардизован CSV формат са 22 атрибута.

## Локација

```
scripts/extract_cases_to_csv.py
```

## Покретање

```powershell
py scripts/extract_cases_to_csv.py
```

## Улаз и излаз

| Тип | Путања | Опис |
|-----|--------|------|
| Улаз | `data/cases/akomantoso/*.xml` | 127 Akoma Ntoso XML судских одлука |
| Излаз | `case_reasoning/presude-cbr/src/main/resources/presude.csv` | CSV база за CBR систем |

## CSV формат

- Сепаратор: `;`
- Кодирање: UTF-8
- Заглавље: коментар (`# id;sud;...`)

### Колоне (22 атрибута)

| # | Колона | Тип | Опис |
|---|--------|-----|------|
| 1 | `id` | int | Секвенцијални идентификатор |
| 2 | `sud` | string | Нормализован назив суда (град) |
| 3 | `brojPredmeta` | string | Број предмета |
| 4 | `tipKrivicnogDjela` | string | "falsifikovanje novca" или "zloupotreba platnih kartica" |
| 5 | `clanKZ` | string | Примијењени члан КЗ |
| 6 | `iznos` | float | Максимални износ једне трансакције (EUR) |
| 7 | `ranijeOsudjivan` | string | "da" / "ne" / "nepoznat" |
| 8 | `uslovnaOsuda` | string | Да ли је изречена условна осуда |
| 9 | `vrstaPresude` | string | "osudjujuca" / "uslovna" / "oslobadjajuca" |
| 10 | `zaposlenost` | string | "zaposlen" / "nezaposlen" / "student" / "penzioner" |
| 11 | `bracniStatus` | string | "ozenjen" / "neozenjen" / "razveden" |
| 12 | `kaznaUMjesecima` | float | Затворска казна у мјесецима |
| 13 | `novcanaKazna` | float | Новчана казна (EUR) |
| 14 | `obrazovanje` | string | "VSS" / "SSS" / "osnovna" / "pismen" |
| 15 | `ukupanIznos` | float | Укупан збир свих износа (EUR) |
| 16 | `brojTransakcija` | int | Број појединачних трансакција |
| 17 | `brojOkrivljenih` | int | Број окривљених лица |
| 18 | `brojSvjedoka` | int | Број свједока |
| 19 | `brojDokaza` | int | Број доказних средстава |
| 20 | `priznanje` | string | "da" / "ne" |
| 21 | `pokusaj` | string | "da" / "ne" |
| 22 | `saizvrsilastvo` | string | "da" / "ne" |

## Кључне функције

| Функција | Опис |
|----------|------|
| `parse_case()` | Парсира појединачни XML и враћа dict са свим атрибутима |
| `normalize_crime_type()` | Нормализује тип кривичног дјела |
| `extract_amounts()` | Екстрахује износе и рачуна макс/укупан/број трансакција |
| `extract_sentence_months()` | Парсира текст казне у мјесеце |
| `detect_confession()` | Детектује признање кривице |
| `detect_attempt()` | Детектује покушај дјела |
| `detect_coperpetration()` | Детектује саизвршилаштво |

## Зависности

- Python 3.8+
- Стандардна библиотека (csv, xml, re, os)
