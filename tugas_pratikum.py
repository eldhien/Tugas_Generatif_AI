from openai import OpenAI
import csv
import os

api_key = "" #masukakn API key
 
client_api = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)
teks_prompt = "Bagaimana AI dapat membantu meningkatkan efisiensi dalam bidang kesehatan? Jelaskan secara singkat."

print(">>> Mengirim teks ke model...")

response = client_api.chat.completions.create(
    model="openai/gpt-oss-20b:free",   
    messages=[
        {
            "role": "user",
            "content": teks_prompt
        }
    ]
)

jawaban_model = response.choices[0].message.content

token_input = response.usage.prompt_tokens
token_output = response.usage.completion_tokens
total_token = response.usage.total_tokens

print("\n=== Jawaban Model ===")
print(jawaban_model)

print("\n=== Informasi Token ===")
print("Token Input :", token_input)
print("Token Output:", token_output)
print("Total Token :", total_token)

nama_file = "TRAINING_AI.csv"

no = 1
if os.path.exists(nama_file):
    with open(nama_file, "r", encoding="utf-8") as file:
        reader = list(csv.reader(file))
        if len(reader) > 1:
            no = len(reader)


with open(nama_file, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    writer.writerow([no, teks_prompt, jawaban_model, token_input, token_output, total_token])

print("\nData berhasil ditambahkan ke TRAINING_AI.csv")