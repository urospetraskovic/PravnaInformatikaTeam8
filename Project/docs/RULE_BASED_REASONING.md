# Задаци 3, 4 и 5: Расуђивање по правилима

## Преглед имплементације

Овај документ описује имплементацију задатака 3, 4 и 5 пројектног задатка из Правне информатике:

- **Задатак 3**: Правне норме у LegalRuleML формату
- **Задатак 4**: Екстракција метаподатака и чињеница (NLP)
- **Задатак 5**: Расуђивање по правилима (DR-Device)

---

## Задатак 3: LegalRuleML правила

### Локација фајлова
```
rule_reasoning/rules/
├── legal_rules.xml      # 20 правила у LegalRuleML формату
├── rulebase.lrml        # Копија за DR-Device
├── drdevice_rules.ddr   # DR-Device Defeasible Logic правила
├── legal_ontology.n3    # RDF/N3 онтологија и правила
├── facts.xml            # Шаблон за унос чињеница
└── facts_example.xml    # Пример попуњених чињеница
```

### Имплементирана правила (20 правила)

| # | ID | Члан | Опис |
|---|-----|------|------|
| 1 | rule_258_1 | Чл. 258 ст. 1 | Израда лажног новца |
| 2 | rule_258_2 | Чл. 258 ст. 2 | Прибављање/оптицај лажног новца |
| 3 | rule_258_3 | Чл. 258 ст. 3 | Квалификовани облик (>15.000€) |
| 4 | rule_260_1 | Чл. 260 ст. 1 | Основни облик злоупотребе картица |
| 5 | rule_260_2 | Чл. 260 ст. 2 | Злоупотреба са имовинском коришћу |
| 6 | rule_260_3 | Чл. 260 ст. 3 | Имовинска корист >3.000€ |
| 7 | rule_260_4 | Чл. 260 ст. 4 | Имовинска корист >30.000€ |
| 8 | rule_mitigating_confession | - | Признање кривице |
| 9 | rule_mitigating_first_offense | - | Раније неосуђиваност |
| 10 | rule_mitigating_restitution | - | Накнада штете |
| 11 | rule_aggravating_prior | - | Раније осуђиваност |
| 12 | rule_aggravating_organized | - | Организована група |
| 13 | rule_suspended_sentence | - | Условна осуда |
| 14 | rule_sentence_reduction | - | Смањење казне |
| 15 | rule_sentence_increase | - | Повећање казне |
| 16 | rule_sticaj | - | Стицај дјела |
| 17 | rule_confiscation_258 | Чл. 258 ст. 5 | Одузимање лажног новца |
| 18 | rule_268_1 | Чл. 268 ст. 1 | Основни облик прања новца |
| 19 | rule_268_3 | Чл. 268 ст. 3 | Прање новца >40.000€ |
| 20 | rule_mitigating_cooperation | - | Сарадња са истрагом |

### Пример правила (LegalRuleML)

```xml
<lrml:ConstitutiveStatement key="rule_260_2">
  <lrml:Rule>
    <lrml:Paraphrase>
      Ако је учинилац дјела из става 1 овог члана употребом картице 
      прибавио противправну имовинску корист, казниће се затвором 
      од шест мјесеци до пет година.
    </lrml:Paraphrase>
    <ruleml:if>
      <ruleml:And>
        <ruleml:Atom>
          <ruleml:Rel>zloupotrebljava_karticu</ruleml:Rel>
          <ruleml:Var>Okrivljeni</ruleml:Var>
        </ruleml:Atom>
        <ruleml:Atom>
          <ruleml:Rel>pribavio_imovinsku_korist</ruleml:Rel>
          <ruleml:Var>Okrivljeni</ruleml:Var>
          <ruleml:Var>Iznos</ruleml:Var>
        </ruleml:Atom>
      </ruleml:And>
    </ruleml:if>
    <ruleml:then>
      <ruleml:Atom>
        <ruleml:Rel>kazna_zatvora</ruleml:Rel>
        <ruleml:Var>Okrivljeni</ruleml:Var>
        <ruleml:Data>6_mjeseci</ruleml:Data>
        <ruleml:Data>5</ruleml:Data>
      </ruleml:Atom>
    </ruleml:then>
  </lrml:Rule>
  <lrml:LegalReference refersTo="/akn/me/act/criminal-code#art_260__para_2"/>
</lrml:ConstitutiveStatement>
```

---

## Задатак 4: NLP екстракција чињеница

### Скрипта за екстракцију
**Фајл**: `scripts/demo_reasoning.py` (NLP екстракција је интегрисана у главну скрипту)

### Функционалности

1. **Екстракција метаподатака** из Akoma Ntoso XML фајлова:
   - Број предмета
   - Суд
   - Датум пресуде
   - Име/иницијали окривљеног
   - Тип кривичног дјела
   - Примјењени члан КЗ

2. **NLP екстракција правних чињеница**:
   - Аутоматско препознавање елемената кривичног дјела
   - Препознавање износа (EUR)
   - Препознавање олакшавајућих/отежавајућих околности

### Подржани предикати

#### Члан 258 - Фалсификовање новца
| Предикат | Опис |
|----------|------|
| `pravi_lazan_novac` | Да ли је правио лажан новац |
| `preinacuje_pravi_novac` | Да ли је преиначивао прави новац |
| `pribavlja_lazan_novac` | Да ли је прибављао лажан новац |
| `stavlja_lazan_novac_u_opticaj` | Да ли је ставио у оптицај |
| `iznos_novca` | Износ у EUR |

#### Члан 260 - Злоупотреба картица
| Предикат | Опис |
|----------|------|
| `pravi_laznu_karticu` | Да ли је правио лажну картицу |
| `neovlasceno_pribavlja_karticu` | Да ли је неовлашћено прибавио |
| `upotrebljava_laznu_karticu` | Да ли је употребљавао |
| `pribavio_imovinsku_korist` | Да ли је прибавио корист |
| `iznos_imovinske_koristi` | Износ користи у EUR |

#### Околности
| Предикат | Тип | Опис |
|----------|-----|------|
| `priznaje_krivicu` | Олакшавајуће | Признање |
| `ranije_osudivan` | Отежавајуће | Ранија осуда |
| `nadoknadio_stetu` | Олакшавајуће | Накнада штете |
| `saradjuje_sa_istragom` | Олакшавајуће | Сарадња |
| `clan_organizovane_grupe` | Отежавајуће | Орг. група |

### Употреба

```powershell
# Екстракција из једног случаја
py scripts/demo_reasoning.py --mode single --case "data/cases/akomantoso/Case_K_277_22.xml"

# Групна обрада свих случајева
py scripts/demo_reasoning.py --mode batch
```

### Генерисани facts.xml формат

```xml
<facts xmlns:ruleml="http://ruleml.org/spec">
  <case>
    <caseId>277/22</caseId>
    <court>PODGORICI</court>
    <crimeType>falsifikovanje i zloupotreba kreditnih kartica</crimeType>
  </case>
  
  <ruleml:Atom>
    <ruleml:Rel>neovlasceno_pribavlja_karticu</ruleml:Rel>
    <ruleml:Ind>Okrivljeni1</ruleml:Ind>
    <ruleml:Data xsi:type="xs:boolean">true</ruleml:Data>
  </ruleml:Atom>
  
  <ruleml:Atom>
    <ruleml:Rel>pribavio_imovinsku_korist</ruleml:Rel>
    <ruleml:Ind>Okrivljeni1</ruleml:Ind>
    <ruleml:Data xsi:type="xs:boolean">true</ruleml:Data>
  </ruleml:Atom>
  
  <ruleml:Atom>
    <ruleml:Rel>iznos_imovinske_koristi</ruleml:Rel>
    <ruleml:Ind>Okrivljeni1</ruleml:Ind>
    <ruleml:Data xsi:type="xs:integer">300</ruleml:Data>
  </ruleml:Atom>
</facts>
```

---

## Задатак 5: Расуђивање по правилима

### Скрипта за расуђивање
**Фајл**: интегрисано у `scripts/demo_reasoning.py`

### Демо скрипта
**Фајл**: `scripts/demo_reasoning.py`

### Режими рада

#### 1. Интерактивни режим
```powershell
py scripts/demo_reasoning.py --mode interactive
```
Омогућава ручни унос чињеница кроз конзолни интерфејс.

#### 2. Појединачни случај
```powershell
py scripts/demo_reasoning.py --mode single --case "data/cases/akomantoso/Case_K_277_22.xml"
```

#### 3. Групна обрада
```powershell
py scripts/demo_reasoning.py --mode batch
```

### Пример излаза

```
============================================================
ОБРАЗЛОЖЕЊЕ РАСУЂИВАЊА ПО ПРАВИЛИМА
============================================================

1. УТВРЂЕНЕ ЧИЊЕНИЦЕ:
----------------------------------------
  • Неовлашћено прибавља картицу: ДА
  • Употребљава лажну/туђу картицу: ДА
  • Прибавио имовинску корист: ДА
  • Износ имовинске користи: 300.0 EUR
  • Раније осуђиван: НЕ

2. ПРЕКРШЕНЕ ПРАВНЕ НОРМЕ:
----------------------------------------
  ▸ Чл. 260 ст. 1 КЗ ЦГ
    Основни облик злоупотребе картица
    
  ▸ Чл. 260 ст. 2 КЗ ЦГ
    Злоупотреба картица са имовинском коришћу

3. ПРИМЈЕЊИВЕ САНКЦИЈЕ:
----------------------------------------
  • rule_260_1: 0 до 3 година затвора
  • rule_260_2: 0.5 до 5 година затвора

4. ОКОЛНОСТИ:
----------------------------------------
  Олакшавајуће околности:
    ✓ Раније неосуђиван

5. ПРЕПОРУКЕ СИСТЕМА:
----------------------------------------
  → Примјењив распон казне: 0.5 до 5 година затвора
  → Условна осуда може бити могућа
============================================================
```

### DR-Device интеграција

Систем подржава рад са DR-Device алатом. За покретање:

1. Инсталирајте Java 8
2. Преузмите DR-Device са: http://dr-device.2i2c.eu/
3. Поставите `DR_DEVICE_PATH` environment variable
4. Користите правила из `rule_reasoning/rules/drdevice_rules.ddr`

Ако DR-Device није доступан, систем аутоматски користи Python reasoning engine.

---

## Структура пројекта

```
Project/
├── scripts/
│   └── demo_reasoning.py         # Демо скрипта + NLP екстракција + расуђивање
├── rule_reasoning/
│   ├── dr-device/                # DR-Device алат
│   └── rules/
│       ├── legal_rules.xml       # LegalRuleML правила
│       ├── drdevice_rules.ddr    # Prolog-style правила
│       ├── legal_ontology.n3     # RDF онтологија
│       ├── facts.xml             # Шаблон чињеница
│       ├── facts_example.xml     # Пример чињеница
│       └── output/               # Резултати расуђивања
├── data/
│   └── cases/
│       └── akomantoso/           # 127 Akoma Ntoso случајева
├── web/                          # Express веб апликација
└── docs/
    └── RULE_BASED_REASONING.md   # Овај документ
```

---

## Тестирање

### Покрените демо са примером:
```powershell
cd Project
py scripts/demo_reasoning.py --mode single --case "data\cases\akomantoso\Case_K_277_22.xml"
```

### Интерактивни тест:
```powershell
py scripts/demo_reasoning.py --mode interactive
```

### Групна обрада:
```powershell
py scripts/demo_reasoning.py --mode batch
```

---

## Даљи развој

- [ ] Web интерфејс за унос чињеница
- [ ] API endpoint за расуђивање
- [ ] Интеграција са jCOLIBRI CBR системом
- [ ] Побољшање NLP модела за српски језик
- [ ] Визуелизација резултата расуђивања
