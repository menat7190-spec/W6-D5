
# W6D5 - Prompt Debugging

## 1. Criteria for Stable Responses

1. The response must follow the same JSON structure.
2. Sentiment labels must use only positive, negative, mixed, or neutral.
3. The explanation must be short and written in Arabic.
4. People, products, and places must be extracted into separate fields.
5. Missing entity categories must be represented by empty arrays.

## 2. Initial Experiment

- Number of original prompts: 5
- Runs per prompt: 3
- Total responses: 15
- Temperature: 0.2
- Model: openai/gpt-oss-20b

## 3. Prompt Problems

1. The original prompt does not define exact sentiment labels, which may cause inconsistent classifications.
2. The original prompt does not specify a fixed output structure, which may cause different response formats.
3. The instruction to keep the response short does not define an approximate length.
4. Entity extraction does not define separate fields for people, products, and places, which may cause inconsistent extraction.

## 4. Repaired Prompt

The repaired prompt separates System, Context, Instruction, and Output Format.
It specifies allowed sentiment labels, fixed JSON keys, and how to represent missing entities.

## 5. JSON Validity Comparison

| Stage | Valid JSON | Invalid JSON | Total |
|---|---:|---:|---:|
| Before repair | Fill after running | Fill after running | 15 |
| After repair | Fill after running | Fill after running | 15 |

## 6. Analysis

Compare the actual responses before and after the repair.
Check JSON validity, sentiment consistency, explanation length, and entity extraction.

## 7. Conclusion

Write what improved after the repair and mention any remaining inconsistencies.
