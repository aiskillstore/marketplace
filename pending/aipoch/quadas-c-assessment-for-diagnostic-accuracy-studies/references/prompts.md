# QUADAS-C Prompts

## Parameter Extractor

**Role**: Top medical expert.
**Task**:
- Determine how many diagnostic methods are compared in the input paper.
- List the diagnostic methods being compared.
**Output**: Array of strings.

## Patient Selection (Domain 1)

### Signaling Questions
**Role**: Top medical expert
**Task**: Answer the following signaling questions based on the paper and QUADAS-2 results.

**Questions**:
1. C1.1 Was the risk of bias for each index test judged ‘low’ for this domain?
2. C1.2 Was a fully paired or randomized design used?
3. C1.3 Was the allocation sequence random? (Only for randomized)
4. C1.4 Was the allocation sequence concealed? (Only for randomized)

### Risk of Bias
**Rule**: If C1.1-C1.4 are "Yes" -> Low. If any "No" -> High. C1.2 "No" -> Strongly consider High.
**Output**: Low/High/Unclear

## Index Test (Domain 2)

### Signaling Questions
**Questions**:
1. C2.1 Was the risk of bias for each index test judged ‘low’ for this domain?
2. C2.2 Were index test results interpreted without knowledge of other index test results?
3. C2.3 Is undergoing one index test unlikely to affect the performance of the other?
4. C2.4 Were index tests conducted/interpreted without advantaging one test?

### Risk of Bias
**Rule**: All "Yes" -> Low. Any "No" -> High. Unclear -> Unclear.
**Output**: Low/High/Unclear

## Reference Standard (Domain 3)

### Signaling Questions
**Questions**:
1. C3.1 Was the risk of bias for each index test judged ‘low’ for this domain?
2. C3.2 Did the reference standard avoid incorporating any of the index tests?

### Risk of Bias
**Rule**: C3.1 and C3.2 "Yes" -> Low. Any "No" -> High.
**Output**: Low/High/Unclear

## Flow and Timing (Domain 4)

### Signaling Questions
**Questions**:
1. C4.1 Was the risk of bias for each index test judged ‘low’ for this domain?
2. C4.2 Was there an appropriate interval between index tests?
3. C4.3 Was the same reference standard used for all index tests?
4. C4.4 Are proportions and reasons for missing data similar across index tests?

### Risk of Bias
**Rule**: C4.1-C4.4 "Yes" -> Low. Any "No" -> High.
**Output**: Low/High/Unclear
