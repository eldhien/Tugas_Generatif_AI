from openai import OpenAI, APIConnectionError, APIError, RateLimitError
import csv
import os
import time
from dotenv import load_dotenv

load_dotenv()
api_key = os.getenv("OPENROUTER_API_KEY")

if not api_key:
    raise ValueError("OPENROUTER_API_KEY belum diset di environment variable.")
 
client_api = OpenAI(
    base_url="https://openrouter.ai/api/v1",
    api_key=api_key
)


def kirim_prompt_dengan_retry(client, models, messages, max_retry=3):
    """Kirim prompt dengan retry berjenjang saat kena rate limit atau gangguan jaringan."""
    percobaan_total = 0
    total_maks_percobaan = max_retry * len(models)

    for model in models:
        for attempt in range(1, max_retry + 1):
            percobaan_total += 1
            try:
                print(
                    f">>> Mencoba model '{model}' "
                    f"(percobaan {percobaan_total}/{total_maks_percobaan})..."
                )
                return client.chat.completions.create(
                    model=model,
                    messages=messages
                )
            except RateLimitError as err:
                if attempt == max_retry:
                    print(f"Rate limit pada model '{model}'. Pindah ke model berikutnya...")
                    break

                waktu_tunggu = 2 ** attempt
                print(
                    f"Rate limit terdeteksi. Tunggu {waktu_tunggu} detik "
                    f"lalu retry..."
                )
                time.sleep(waktu_tunggu)
            except (APIConnectionError, APIError) as err:
                if attempt == max_retry:
                    print(
                        f"Gagal pada model '{model}' setelah {max_retry} kali percobaan: {err}"
                    )
                    break

                waktu_tunggu = 2 ** attempt
                print(f"Terjadi error API/jaringan. Tunggu {waktu_tunggu} detik lalu retry...")
                time.sleep(waktu_tunggu)

    raise RuntimeError(
        "Semua percobaan ke OpenRouter gagal. "
        "Coba lagi beberapa saat, ganti model, atau gunakan API key BYOK."
    )

#tarif model premium per 1 juta token (USD) model x-ai/grok-4.20-multi-agent-beta
HARGA_INPUT_PER_1M_USD = 2.00
HARGA_OUTPUT_PER_1M_USD = 6.00

# Dummy kurs USD ke IDR
KURS_USD_KE_IDR = 16000

teks_prompt = "belajar bahasa inggrismulai dari mana dulu? Jelaskan secara singkat."

daftar_model = [
    "openai/gpt-oss-20b:free",
    "meta-llama/llama-3.3-70b-instruct:free"
]

messages = [
    {
        "role": "user",
        "content": teks_prompt
    }
]

response = kirim_prompt_dengan_retry(
    client=client_api,
    models=daftar_model,
    messages=messages,
    max_retry=3
)

jawaban_model = response.choices[0].message.content

token_input = response.usage.prompt_tokens
token_output = response.usage.completion_tokens
total_token = response.usage.total_tokens

# Rumus biaya: (jumlah_token / 1_000_000) * harga_per_1M
biaya_input_usd = (token_input / 1_000_000) * HARGA_INPUT_PER_1M_USD
biaya_output_usd = (token_output / 1_000_000) * HARGA_OUTPUT_PER_1M_USD
total_biaya_usd = biaya_input_usd + biaya_output_usd

biaya_input_idr = biaya_input_usd * KURS_USD_KE_IDR
biaya_output_idr = biaya_output_usd * KURS_USD_KE_IDR
total_biaya_idr = total_biaya_usd * KURS_USD_KE_IDR

nama_file = "TRAINING_AI.csv"

header = [
    "No",
    "Prompt",
    "Jawaban",
    "Token Input",
    "Token Output",
    "Total Token",
    "Biaya Input USD",
    "Biaya Output USD",
    "Total Biaya USD",
    "Biaya Input IDR",
    "Biaya Output IDR",
    "Total Biaya IDR"
]

no = 1
if os.path.exists(nama_file):
    with open(nama_file, "r", encoding="utf-8") as file:
        reader = list(csv.reader(file))
        if len(reader) > 1:
            no = len(reader)


with open(nama_file, "a", newline="", encoding="utf-8") as file:
    writer = csv.writer(file)
    if os.path.getsize(nama_file) == 0:
        writer.writerow(header)

    writer.writerow([
        no,
        teks_prompt,
        jawaban_model,
        token_input,
        token_output,
        total_token,
        f"{biaya_input_usd:.8f}",
        f"{biaya_output_usd:.8f}",
        f"{total_biaya_usd:.8f}",
        f"{biaya_input_idr:.2f}",
        f"{biaya_output_idr:.2f}",
        f"{total_biaya_idr:.2f}"
    ])

print("\nData berhasil ditambahkan ke TRAINING_AI.csv")

print("\n" + "=" * 55)
print("RINGKASAN HASIL EKSEKUSI")
print("=" * 55)
print("\n[Respons Model]")
print(jawaban_model)

print("\n[Rincian Penggunaan Token]")
print(f"- Token Input  : {token_input}")
print(f"- Token Output : {token_output}")
print(f"- Total Token  : {total_token}")

print("\n[Estimasi Biaya]")
print("- USD")
print(f"  Input        : ${biaya_input_usd:.6f}")
print(f"  Output       : ${biaya_output_usd:.6f}")
print(f"  Total        : ${total_biaya_usd:.6f}")
print("- IDR")
print(f"  Input        : Rp {biaya_input_idr:,.2f}")
print(f"  Output       : Rp {biaya_output_idr:,.2f}")
print(f"  Total        : Rp {total_biaya_idr:,.2f}")
print("=" * 55)