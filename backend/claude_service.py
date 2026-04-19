import anthropic
import json
import os
from duckduckgo_search import DDGS
from dotenv import load_dotenv

load_dotenv()

client = anthropic.Anthropic(api_key=os.getenv("ANTHROPIC_API_KEY"))
MODEL = "claude-sonnet-4-6"


def _parse_json(raw: str) -> dict:
    raw = raw.strip()
    # Strip markdown code blocks
    if "```" in raw:
        for part in raw.split("```"):
            part = part.strip()
            if part.startswith("json"):
                part = part[4:].strip()
            if part.startswith("{"):
                raw = part
                break
    # Extract just the JSON object (first { to last })
    start = raw.find("{")
    end = raw.rfind("}") + 1
    if start != -1 and end > start:
        raw = raw[start:end]
    return json.loads(raw.strip())


def extract_cv_data(cv_text: str) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=1024,
        messages=[{"role": "user", "content": f"""Extrae la siguiente información del CV y responde SOLO con JSON válido:

{{
  "name": "nombre completo",
  "email": "email o vacío",
  "phone": "teléfono o vacío",
  "years_experience": 0,
  "education": ["título 1"],
  "skills": ["skill 1"],
  "languages": ["idioma 1"],
  "previous_positions": ["cargo en empresa (años)"],
  "main_profession": "profesión principal del candidato"
}}

CV:
{cv_text[:4000]}"""}],
    )
    return _parse_json(msg.content[0].text)


def evaluate_cv(cv_text: str, job_title: str, job_description: str, job_requirements: str) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": f"""Eres un experto en recursos humanos. Evalúa este CV para el puesto indicado.

PUESTO: {job_title}
DESCRIPCIÓN: {job_description}
REQUISITOS: {job_requirements}

CV:
{cv_text[:4000]}

Responde SOLO con JSON válido:
{{
  "score": 85,
  "resumen": "Resumen ejecutivo de 2-3 oraciones",
  "fortalezas": ["fortaleza 1", "fortaleza 2"],
  "debilidades": ["debilidad 1"],
  "requisitos_cumplidos": ["requisito cumplido 1"],
  "requisitos_faltantes": ["requisito faltante 1"],
  "recomendacion": "CONTRATAR | CONSIDERAR | RECHAZAR",
  "comentario_final": "Comentario detallado para el reclutador"
}}

Score de 0 a 100. Sé objetivo y específico."""}],
    )
    return _parse_json(msg.content[0].text)


def evaluate_atc(cv_text: str) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=2048,
        messages=[{"role": "user", "content": f"""Eres un psicólogo organizacional experto en evaluaciones ATC (Assessment Center) y tests de selección de personal en Chile.

Analiza este CV y estima la probabilidad de que el candidato pase los siguientes tipos de tests de selección:

CV:
{cv_text[:4000]}

Responde SOLO con JSON válido:
{{
  "score_general": 78,
  "resumen": "Evaluación general del candidato para pruebas ATC en 2-3 oraciones",
  "tests": {{
    "aptitud_verbal": {{
      "score": 80,
      "nivel": "Alto | Medio | Bajo",
      "fundamento": "Razón basada en el CV"
    }},
    "aptitud_numerica": {{
      "score": 70,
      "nivel": "Alto | Medio | Bajo",
      "fundamento": "Razón basada en el CV"
    }},
    "razonamiento_logico": {{
      "score": 75,
      "nivel": "Alto | Medio | Bajo",
      "fundamento": "Razón basada en el CV"
    }},
    "personalidad_laboral": {{
      "score": 85,
      "nivel": "Alto | Medio | Bajo",
      "fundamento": "Razón basada en el CV"
    }},
    "competencias_conductuales": {{
      "score": 72,
      "nivel": "Alto | Medio | Bajo",
      "fundamento": "Razón basada en el CV"
    }}
  }},
  "fortalezas_atc": ["fortaleza 1", "fortaleza 2"],
  "areas_riesgo": ["área de riesgo 1"],
  "recomendaciones_preparacion": ["consejo práctico para prepararse 1", "consejo 2"],
  "veredicto": "MUY PROBABLE PASAR | PROBABLE PASAR | INCIERTO | POCO PROBABLE"
}}"""}],
    )
    return _parse_json(msg.content[0].text)


def hr_review(cv_text: str) -> dict:
    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": f"""Eres un experto en Recursos Humanos y selección de personal con 20 años de experiencia en el mercado laboral chileno. Tienes conocimiento actualizado del mercado laboral chileno en 2026.

Realiza una revisión profesional completa de este CV como si fuera a presentarse a empresas en Chile:

CV:
{cv_text[:4000]}

Responde SOLO con JSON válido:
{{
  "score_cv": 72,
  "nivel_cv": "Excelente | Bueno | Regular | Deficiente",
  "resumen_profesional": "Evaluación general del CV en 3 oraciones",
  "puntuacion_por_seccion": {{
    "formato_presentacion": {{ "score": 80, "comentario": "..." }},
    "experiencia_laboral": {{ "score": 75, "comentario": "..." }},
    "educacion_formacion": {{ "score": 70, "comentario": "..." }},
    "habilidades_competencias": {{ "score": 65, "comentario": "..." }},
    "logros_resultados": {{ "score": 60, "comentario": "..." }}
  }},
  "aspectos_positivos": ["punto positivo 1", "punto positivo 2"],
  "mejoras_urgentes": ["mejora urgente 1", "mejora urgente 2"],
  "mejoras_opcionales": ["mejora opcional 1"],
  "keywords_faltantes": ["keyword importante que no aparece en el CV"],
  "perfil_ideal_para": ["tipo de empresa o cargo donde encajaría bien"],
  "consejo_entrevista": "Consejo principal para la entrevista de trabajo",
  "recomendacion_salarial": "Rango salarial estimado en CLP para el mercado chileno 2026"
}}"""}],
    )
    return _parse_json(msg.content[0].text)


def improve_cv(cv_text: str, hr_data: dict) -> str:
    mejoras_urgentes  = hr_data.get("mejoras_urgentes", [])
    mejoras_opcionales = hr_data.get("mejoras_opcionales", [])
    keywords          = hr_data.get("keywords_faltantes", [])
    scores            = hr_data.get("puntuacion_por_seccion", {})
    consejo           = hr_data.get("consejo_entrevista", "")
    perfil_ideal      = hr_data.get("perfil_ideal_para", [])

    secciones_bajas = [
        f"- {k.replace('_',' ').title()}: {v.get('score',0)}/100 → {v.get('comentario','')}"
        for k, v in scores.items() if v.get("score", 100) < 75
    ]

    msg = client.messages.create(
        model=MODEL,
        max_tokens=4096,
        messages=[{"role": "user", "content": f"""Eres un experto en redacción de CVs con 15 años de experiencia en el mercado laboral chileno.

Un reclutador HR analizó este CV y entregó el siguiente diagnóstico detallado. Tu tarea es reescribir el CV completo aplicando CADA corrección indicada.

━━━ DIAGNÓSTICO HR ━━━

MEJORAS URGENTES (OBLIGATORIO corregir todas):
{chr(10).join(f"• {m}" for m in mejoras_urgentes)}

MEJORAS OPCIONALES (aplicar si es posible):
{chr(10).join(f"• {m}" for m in mejoras_opcionales)}

SECCIONES CON PUNTAJE BAJO (mejorar especialmente):
{chr(10).join(secciones_bajas) if secciones_bajas else "• Todas las secciones están bien puntuadas"}

KEYWORDS QUE FALTAN (incorporar naturalmente en el texto):
{chr(10).join(f"• {k}" for k in keywords)}

PERFIL IDEAL PARA:
{chr(10).join(f"• {p}" for p in perfil_ideal)}

━━━ CV ORIGINAL ━━━
{cv_text[:5000]}

━━━ INSTRUCCIONES DE REESCRITURA ━━━
1. Mantén TODOS los datos reales del candidato (nombre, empresas, fechas, títulos)
2. En cada cargo de la experiencia laboral, REEMPLAZA las responsabilidades genéricas por 2-3 logros con impacto medible. Cada punto debe seguir la fórmula: ACCIÓN + RESULTADO + IMPACTO EN LA EMPRESA. Ejemplos del formato correcto:
   - "Automaticé el proceso de nóminas en Excel, reduciendo errores en un 40% e impactando directamente en la satisfacción del equipo"
   - "Desarrollé estrategia de retención para cartera de 45 clientes, logrando 95% de renovación y aumentando ingresos recurrentes en $2M CLP mensual"
   - "Lideré equipo de 8 personas en rediseño de procesos internos, reduciendo tiempos de entrega en 25% y mejorando la productividad del área"
   Si no tienes el dato exacto, usa cifras coherentes y realistas para el cargo y sector (ej: "más del 20%", "ahorrando sobre 10 horas semanales al equipo")
3. Reestructura las secciones con puntaje bajo según sus comentarios
4. Incorpora las keywords faltantes de forma natural dentro de los logros y habilidades
5. Agrega sección "Perfil Profesional" al inicio: 3-4 oraciones que resuman experiencia, especialidad y propuesta de valor
6. Usa formato Markdown profesional: ## para secciones, • para bullets
7. Escribe en español formal chileno
8. Devuelve SOLO el CV mejorado completo, sin explicaciones ni comentarios antes o después"""}],
    )
    return msg.content[0].text


def search_jobs_chile(profession: str, skills: list[str], years_exp: int) -> list[dict]:
    top_skills = " ".join(skills[:3]) if skills else ""
    nivel = "junior" if years_exp < 2 else ("senior" if years_exp > 5 else "")

    queries = [
        f'{profession} oferta empleo Chile 2026 postular requisitos',
        f'{profession} {top_skills} vacante Santiago Chile contrato',
        f'{profession} {nivel} trabajo Chile laborum bumeran trabajando',
        f'{profession} empleo Chile funciones sueldo renta',
        f'{profession} hiring Chile computrabajo indeed linkedin',
    ]

    job_signals = [
        'postular', 'oferta', 'vacante', 'empleo', 'trabajo', 'hiring',
        'requisitos', 'funciones', 'cargo', 'contrato', 'sueldo', 'renta',
        'laborum', 'bumeran', 'trabajando', 'computrabajo', 'indeed',
    ]

    results = []
    seen_urls = set()

    with DDGS() as ddgs:
        for query in queries:
            if len(results) >= 10:
                break
            try:
                for r in ddgs.text(query, region="cl-es", max_results=6):
                    url = r.get("href", "")
                    if url in seen_urls:
                        continue
                    combined = (r.get("title", "") + " " + r.get("body", "")).lower()
                    if sum(1 for s in job_signals if s in combined) < 2:
                        continue
                    seen_urls.add(url)
                    results.append({
                        "titulo": r.get("title", ""),
                        "descripcion": r.get("body", "")[:250],
                        "url": url,
                        "fuente": _extract_domain(url),
                    })
            except Exception:
                continue

    return results[:10]


def _extract_domain(url: str) -> str:
    try:
        from urllib.parse import urlparse
        domain = urlparse(url).netloc.replace("www.", "")
        return domain
    except Exception:
        return url
