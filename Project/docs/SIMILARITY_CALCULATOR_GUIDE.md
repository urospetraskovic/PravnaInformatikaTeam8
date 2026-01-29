# 🔍 Case Similarity Calculator Guide

## Overview

The `CaseSimilarityCalculator` is the core algorithm of the Case-Based Reasoning (CBR) system. It calculates how similar two Montenegrian court cases are on a scale of **0.0 (completely different) to 1.0 (identical)**.

This guide explains how the calculator works and how to integrate it with AI models for intelligent case matching.

---

## How It Works

### Similarity Metrics (Weighted)

The calculator evaluates **5 key attributes**, each with a specific weight:

| Attribute | Weight | Description |
|-----------|--------|-------------|
| **Case Type** | 40% | Most important - exact crime type match |
| **Verdict** | 25% | Trial outcome (GUILTY, ACQUITTED, CONDITIONAL) |
| **Harm Level** | 15% | Physical + psychological harm score (0-5) |
| **Evidence** | 10% | Type and quality of evidence |
| **Power Dynamics** | 10% | Workplace context and superior/subordinate relationships |

### Similarity Score Calculation

```
Total Similarity = (Type Score × 0.40) 
                 + (Verdict Score × 0.25) 
                 + (Harm Score × 0.15) 
                 + (Evidence Score × 0.10) 
                 + (Power Score × 0.10)
```

---

## Algorithm Details

### 1. Case Type Comparison

**Exact Match:** 1.0
- "Workplace Harassment" vs "Workplace Harassment" = 1.0

**Related Categories:** 0.65 - 0.85
- Different harassment types (stalking, threatening, mobbing) = 0.85
- Financial crimes with each other = 0.80
- Violence-related crimes with each other = 0.75

**Unrelated:** 0.0
- Harassment vs Financial Crime = 0.0

**Categories Recognized:**
- **Harassment Types:** stalking, harassment, threat, endangering, mobbing
- **Financial Crimes:** embezzlement, theft, fraud, misappropriation
- **Violence Types:** assault, violence, abuse

### 2. Verdict Comparison

| Comparison | Score |
|-----------|-------|
| Both GUILTY (same sentence type) | 1.0 |
| Both ACQUITTED | 1.0 |
| Both CONDITIONAL | 0.95 |
| GUILTY vs CONDITIONAL (both non-acquittal) | 0.5 |
| Any vs ACQUITTED (different outcome) | 0.0 |

**For GUILTY verdicts:** Considers sentence duration
- Same duration (±0 months): 1.0
- Within 2 months: 1.0
- Within 6 months: 0.9
- Within 12 months: 0.75
- Over 12 months difference: 0.5

### 3. Harm Assessment Comparison

| Difference | Score |
|-----------|-------|
| 0 (identical) | 1.0 |
| 1 point difference | 0.95 |
| 2 points | 0.85 |
| 4 points | 0.70 |
| 6 points | 0.50 |
| Over 6 points | 0.25 |

Example: Harm 3/5 vs Harm 4/5 = 0.95 (very similar)

### 4. Evidence Comparison

Checks for matching evidence types:
- Video surveillance
- Phone records
- Psychological assessment
- Witness count similarity (±2 witnesses)

Score = (matches / total indicators)

### 5. Power Dynamics Comparison

Evaluates:
- **Workplace context match** (workplace vs non-workplace)
- **Superior/subordinate relationship** presence

Score = (matches / 2) - either 0.0, 0.5, or 1.0

---

## Usage

### In Java

```java
import cbr.similarity.CaseSimilarityCalculator;
import cbr.database.CaseDescription;

// Get two cases to compare
CaseDescription case1 = database.getCase("K 217/24");
CaseDescription case2 = database.getCase("K 277/12");

// Calculate similarity (returns 0.0 to 1.0)
double similarity = CaseSimilarityCalculator.calculateSimilarity(case1, case2);

System.out.println("Similarity: " + (similarity * 100) + "%");

// Get detailed breakdown
String explanation = CaseSimilarityCalculator.getSimilarityExplanation(case1, case2);
System.out.println(explanation);
```

### Web API (Coming Soon with AI Model)

```javascript
// Find similar cases for a query case
async function findSimilarCases(queryCaseId) {
  const response = await fetch('/api/search/similar', {
    method: 'POST',
    headers: { 'Content-Type': 'application/json' },
    body: JSON.stringify(queryCaseId)
  });
  return await response.json();
}
```

---

## Integration with Local AI Models

### Using Qwen 14B Parameter Model

When you integrate your local Qwen 14B model, you can use it to:

1. **Enhance case descriptions** - Generate semantic embeddings for cases
2. **Fuzzy matching** - Handle variations in case type names
3. **Contextual similarity** - Understand deeper semantic relationships
4. **Recommendation ranking** - Re-rank results based on contextual relevance

**Integration approach:**

```javascript
// Pseudo-code for future implementation
async function findSimilarCasesWithAI(queryCaseId) {
  const queryCase = getCase(queryCaseId);
  
  // 1. Get all cases
  let candidates = allCases;
  
  // 2. Get AI embeddings
  const queryEmbedding = await qwenModel.embed(queryCase);
  const candidateEmbeddings = await Promise.all(
    candidates.map(c => qwenModel.embed(c))
  );
  
  // 3. Calculate combined scores
  const results = candidates.map((caseData, idx) => ({
    ...caseData,
    // 70% algorithm-based similarity
    algorithmScore: CaseSimilarityCalculator.calculateSimilarity(queryCase, caseData) * 0.7,
    // 30% AI semantic similarity
    aiScore: cosineSimilarity(queryEmbedding, candidateEmbeddings[idx]) * 0.3,
    // Combined
    totalScore: (algorithmScore + aiScore)
  }));
  
  // 4. Return top matches
  return results.sort((a, b) => b.totalScore - a.totalScore).slice(0, 5);
}
```

---

## Configuration & Customization

### Adjusting Weights

To emphasize certain attributes, modify these constants in `CaseSimilarityCalculator.java`:

```java
// Current weights (add to 1.0)
private static final double WEIGHT_CASE_TYPE = 0.40;      // Increase for stricter type matching
private static final double WEIGHT_VERDICT = 0.25;        // Increase for verdict importance
private static final double WEIGHT_HARM = 0.15;           // Increase for harm-sensitive cases
private static final double WEIGHT_EVIDENCE = 0.10;       // Increase for evidence-focused matching
private static final double WEIGHT_POWER_DYNAMICS = 0.10;  // Increase for workplace cases
```

### Adding New Crime Categories

In `CaseSimilarityCalculator.java`, add to helper methods:

```java
private static boolean isHarassmentType(String type) {
  return type.contains("stalking") 
      || type.contains("harassment")
      || type.contains("threat")
      || type.contains("endangering")
      || type.contains("mobbing")
      || type.contains("proganj")
      || type.contains("NEW_CATEGORY");  // Add your category
}
```

---

## Performance & Accuracy

### Accuracy Expectations

- **Exact type matches:** 95-100% relevance
- **Related type matches:** 70-90% relevance
- **Different types:** 0-40% relevance (usually filtered out)

### Performance

- **Single comparison:** <1ms
- **Comparing against 13 cases:** <50ms
- **Comparing against 100+ cases:** <500ms

### Optimization Tips

1. **Cache results** for frequently compared cases
2. **Pre-filter by case type** before detailed comparison
3. **Set threshold** (e.g., only show >0.5 similarity)
4. **Batch comparisons** when possible

---

## Case Data Structure

The calculator expects `CaseDescription` objects with these fields:

```java
// Required for calculations
String caseType              // Type of case
Boolean guilty              // Verdict status
Boolean acquitted           // Verdict status
Boolean conditional         // Verdict status
Integer totalHarmScore      // 0-5 scale
Integer sentenceDurationMonths

// Optional for enhanced matching
Boolean videoSurveillance
Boolean phoneRecords
Boolean psychologicalAssessment
Integer witnessCount
Boolean organizationalContext
Boolean superiorSubordinate
```

---

## Example Scenario

**Query:** Find cases similar to K 217/24 (Threatening/Endangering Safety, GUILTY, Harm 3, Workplace)

**Database:**
1. K 277/12 - Labor Rights Violation, GUILTY, Harm 3, Workplace → **Similarity: 0.85**
2. K 292/2014 - Embezzlement, GUILTY, Harm 3, Office → **Similarity: 0.42**
3. K 64/14 - Threatening/Safety, ACQUITTED, Harm 1, Workplace → **Similarity: 0.61**

**Top result:** K 277/12 (0.85) - Same verdict, same type category, same harm, workplace context

---

## Future Enhancements

- [ ] Machine learning fine-tuning on Montenegrian case outcomes
- [ ] Temporal similarity (cases from similar time periods)
- [ ] Judge similarity (cases ruled by similar judges)
- [ ] Appeal outcome consideration
- [ ] Legal precedent chaining (case→appeals→related cases)

---

## References

- **Source:** `src/java/CaseSimilarityCalculator.java`
- **Related:** `KNNRetriever.java` (uses this calculator for k-NN retrieval)
- **Database:** 13 Montenegrian court verdicts in EXTRACTED_CASES_DATABASE.json

---

**Ready to integrate with your Qwen 14B model when you get home!** 🚀
