import os
from openai import OpenAI

from .conar_schema import CONAR_SCHEMA


OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")

if not OPENAI_API_KEY:
    raise RuntimeError(
        "OPENAI_API_KEY not found. Check your .env file and load_dotenv configuration."
    )

client = OpenAI(api_key=OPENAI_API_KEY)

SYSTEM_RULES = """
Você é um analisador de conformidade para publicidade de apostas esportivas no Brasil.
Objetivo: identificar riscos de não conformidade com boas práticas de publicidade responsável e princípios do CONAR.
Você NÃO fornece aconselhamento jurídico. Você fornece alertas educativos e sugestões práticas.

Regras principais para checar em criativos (imagem):
- Promessas de ganho fácil/rápido/garantido, “renda”, “lucro certo”, “sem risco”.
- Associação de apostar com sucesso financeiro, status, luxo, riqueza, vida perfeita.
- Minimização de riscos (“é só diversão” sem aviso claro), glamourização.
- Pressão emocional / urgência enganosa (“última chance”, “agora ou nunca”, contagem agressiva).
- Apelo a menores: estética infantil, linguagem juvenil, personagens infantis, idade aparente muito jovem.
- Avisos essenciais: “Aposte com responsabilidade” e “Proibido para menores de 18 anos”.
- Clareza de que se trata de apostas e que envolve risco.

Saída: responda SOMENTE no formato JSON conforme o schema fornecido.
"""

def analyze_conar_image(image_url: str, model: str) -> dict:
    """
    image_url: URL acessível da imagem (em dev: MEDIA_URL com DEBUG; em prod: URL pública/S3/R2).
    Returns: dict conforme CONAR_SCHEMA
    """
    prompt = """
Analise a imagem como criativo publicitário de casa de apostas.
1) Identifique texto e mensagens implícitas.
2) Marque flags em checks (true/false).
3) Liste findings com severidade (high/medium/low) e descreva:
   - what: o problema encontrado
   - why: por que é risco
   - fix: como corrigir objetivamente

Critérios de status:
- green: sem riscos relevantes e avisos presentes.
- yellow: pequenos/médios ajustes recomendados (ex: aviso faltando, linguagem ambígua).
- red: violações fortes (promessa de ganho garantido, apelo a menores, minimização grave de risco).
"""

    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": SYSTEM_RULES},
            {
                "role": "user",
                "content": [
                    {"type": "input_text", "text": prompt},
                    {"type": "input_image", "image_url": image_url},
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "json_schema": CONAR_SCHEMA,
            }
        },
    )

    # The SDK returns structured content; safest is to read output_text then json-load is unnecessary
    # because structured outputs are guaranteed to match schema.
    # Still, response.output_text is JSON string. We'll parse it.
    import json
    return json.loads(response.output_text)
