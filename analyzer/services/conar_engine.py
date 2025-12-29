import os
import base64
import mimetypes
import json
from openai import OpenAI

from .conar_schema import CONAR_SCHEMA

OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
if not OPENAI_API_KEY:
    raise RuntimeError("OPENAI_API_KEY not found. Check your .env loading.")

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

def _image_path_to_data_url(image_path: str) -> str:
    mime_type, _ = mimetypes.guess_type(image_path)
    if not mime_type:
        mime_type = "image/png"

    with open(image_path, "rb") as f:
        b64 = base64.b64encode(f.read()).decode("utf-8")

    return f"data:{mime_type};base64,{b64}"

def analyze_conar_image_from_file(image_path: str, model: str) -> dict:
    image_data_url = _image_path_to_data_url(image_path)

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
                    {"type": "input_image", "image_url": image_data_url},
                ],
            },
        ],
        text={
            "format": {
                "type": "json_schema",
                "name": "conar_image_compliance_result",
                "strict": True,
                "schema": CONAR_SCHEMA["schema"],
            }
        },
    )

    return json.loads(response.output_text)
