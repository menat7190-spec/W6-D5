
import os
import json
import csv
from groq import Groq

api_key = os.getenv("GROQ_API_KEY")

if not api_key:
    raise ValueError("GROQ_API_KEY is missing. Set your API key first.")

client = Groq(api_key=api_key)

MODEL = "openai/gpt-oss-20b"
TEMPERATURE = 0.2
RUNS = 3

reviews = [
    "اشتريت سماعة Anker من أحمد في المعادي، الصوت ممتاز والبطارية بتعدي اليوم كله. التوصيل جه في معاده. أنصح بيها.",
    "موبايل Samsung A54 كاميرته حلوة جداً بس البطارية بتخلص قبل نص اليوم والشاحن بطيء. مش عارف أنصح بيه ولا لأ.",
    "التوصيل اتأخر أسبوع كامل ومحدش رد على الرسايل. الخدمة وحشة جداً.",
    "برافو عليهم، طلبت الشنطة تيجي في يومين فجت بعد تلات أسابيع، وكمان الزرار اتكسر من أول استخدام. خدمة تحفة فعلاً 👏",
    "لابتوب Lenovo IdeaPad اللي استلمته من فرع سيتي ستارز شغال تمام والسعر مناسب، بس مفيش كرتونة أصلية والتغليف كان ضعيف."
]

original_prompts = [
    "قولي رأيك في الريفيو ده وهل هو كويس ولا وحش، ومتطولش، بس اشرح ليه، وطلعلي أي أسماء أو منتجات مذكورة. الريفيو: اشتريت سماعة Anker من أحمد في المعادي، الصوت ممتاز والبطارية بتعدي اليوم كله. التوصيل جه في معاده. أنصح بيها.",
    "قولي رأيك في الريفيو ده وهل هو كويس ولا وحش، ومتطولش، بس اشرح ليه، وطلعلي أي أسماء أو منتجات مذكورة. الريفيو: موبايل Samsung A54 كاميرته حلوة جداً بس البطارية بتخلص قبل نص اليوم والشاحن بطيء. مش عارف أنصح بيه ولا لأ.",
    "قولي رأيك في الريفيو ده وهل هو كويس ولا وحش، ومتطولش، بس اشرح ليه، وطلعلي أي أسماء أو منتجات مذكورة. الريفيو: التوصيل اتأخر أسبوع كامل ومحدش رد على الرسايل. الخدمة وحشة جداً.",
    "قولي رأيك في الريفيو ده وهل هو كويس ولا وحش، ومتطولش، بس اشرح ليه، وطلعلي أي أسماء أو منتجات مذكورة. الريفيو: برافو عليهم، طلبت الشنطة تيجي في يومين فجت بعد تلات أسابيع، وكمان الزرار اتكسر من أول استخدام. خدمة تحفة فعلاً 👏",
    "قولي رأيك في الريفيو ده وهل هو كويس ولا وحش، ومتطولش، بس اشرح ليه، وطلعلي أي أسماء أو منتجات مذكورة. الريفيو: لابتوب Lenovo IdeaPad اللي استلمته من فرع سيتي ستارز شغال تمام والسعر مناسب، بس مفيش كرتونة أصلية والتغليف كان ضعيف."
]

system_prompt = """
You are a review analysis assistant.
Return only one valid JSON object.
Do not add Markdown, code fences, or text outside the JSON.
Use only the following sentiment labels:
positive, negative, mixed, neutral.
Do not invent information.
"""

def build_repaired_prompt(review):
    return f"""
Context:
The following text is a customer review in Egyptian Arabic.
Analyze only the information explicitly stated in the review.

Instruction:
1. Classify the overall sentiment.
2. Explain the classification in one short Arabic sentence.
3. Extract all explicitly mentioned people, products, and places.
4. Do not invent missing information.
5. If a category has no mentioned entities, use an empty array.
6. If the review is positive and negative, use mixed.
7. Return exactly one JSON object and no extra text.

Output Format:
{{
  "sentiment": "positive | negative | mixed | neutral",
  "reason": "short explanation in Arabic",
  "entities": {{
    "people": [],
    "products": [],
    "places": []
  }}
}}

Review:
{review}
"""

def call_model(messages):
    response = client.chat.completions.create(
        model=MODEL,
        messages=messages,
        temperature=TEMPERATURE,
        max_completion_tokens=500
    )
    return response.choices[0].message.content or ""

def is_valid_json(response):
    try:
        parsed = json.loads(response)
        return isinstance(parsed, dict)
    except (json.JSONDecodeError, TypeError):
        return False

def run_experiment(stage):
    results = []

    for index, review in enumerate(reviews):
        for run_number in range(1, RUNS + 1):
            if stage == "before":
                messages = [
                    {"role": "user", "content": original_prompts[index]}
                ]
            else:
                messages = [
                    {"role": "system", "content": system_prompt},
                    {
                        "role": "user",
                        "content": build_repaired_prompt(review)
                    }
                ]

            print(
                f"Stage: {stage} | Review: {index + 1} "
                f"| Run: {run_number}"
            )

            try:
                answer = call_model(messages)
                valid = is_valid_json(answer)
                error = ""
            except Exception as exc:
                answer = ""
                valid = False
                error = str(exc)

            results.append({
                "stage": stage,
                "review_number": index + 1,
                "run_number": run_number,
                "review": review,
                "response": answer,
                "valid_json": valid,
                "error": error
            })

            print(answer)
            print("Valid JSON:", valid)
            print("-" * 60)

    return results

before_results = run_experiment("before")
after_results = run_experiment("after")

all_results = before_results + after_results

with open(
    "W6D5_results.json",
    "w",
    encoding="utf-8"
) as file:
    json.dump(all_results, file, ensure_ascii=False, indent=2)

with open(
    "W6D5_responses.csv",
    "w",
    encoding="utf-8-sig",
    newline=""
) as file:
    fieldnames = [
        "stage",
        "review_number",
        "run_number",
        "review",
        "response",
        "valid_json",
        "error"
    ]

    writer = csv.DictWriter(file, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(all_results)

before_valid = sum(
    result["valid_json"] for result in before_results
)

after_valid = sum(
    result["valid_json"] for result in after_results
)

comparison = [
    {
        "stage": "Before repair",
        "valid_json": before_valid,
        "invalid_json": len(before_results) - before_valid,
        "total": len(before_results)
    },
    {
        "stage": "After repair",
        "valid_json": after_valid,
        "invalid_json": len(after_results) - after_valid,
        "total": len(after_results)
    }
]

with open(
    "W6D5_comparison.csv",
    "w",
    encoding="utf-8-sig",
    newline=""
) as file:
    writer = csv.DictWriter(
        file,
        fieldnames=[
            "stage",
            "valid_json",
            "invalid_json",
            "total"
        ]
    )
    writer.writeheader()
    writer.writerows(comparison)

print("\nFINAL COMPARISON")
print("-" * 40)

for row in comparison:
    print(
        f'{row["stage"]}: '
        f'{row["valid_json"]}/{row["total"]} valid JSON, '
        f'{row["invalid_json"]} invalid'
    )

print("\nFiles saved:")
print("W6D5_results.json")
print("W6D5_responses.csv")
print("W6D5_comparison.csv")
