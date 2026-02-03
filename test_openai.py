from openai import OpenAI

client = OpenAI()

resp = client.responses.create(
    model="gpt-4.1-mini",
    input="Ответь одним словом: работает"
)

print(resp.output_text)
