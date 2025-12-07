from __future__ import annotations
from typing import Any, Optional, Type
import json
import ast
from openai import OpenAI # github.com/openai/openai-python

# Konfigurace poskytovatelů API
# Je třeba nastavit vlastní klíč API / API key

API_CONFIG_OPENAI = {
    "url": "https://api.openai.com/v1",
    "key": "Váš API klíč pro používání služeb OpenAI",
    "model": "gpt-5.1",
}

API_CONFIG_GEMINI = {
    "url": "https://generativelanguage.googleapis.com/v1beta/openai/",
    "key": "Váš API klíč pro používání služeb Google Gemini",
    "model": "models/gemini-2.5-flash",
}

API_CONFIG_GROK = {
    "url": "https://api.x.ai/v1",
    "key": "Váš API klíč pro používání služeb xAI Grok",
    "model": "grok-4-latest",
}

# Zdarma, ale slabší
API_CONFIG_MISTRAL = {
    "url": "https://api.mistral.ai/v1",
    "key": "Váš API klíč pro používání služeb Mistral",
    "model": "mistral-large-latest",
}

# Výchozí provider, pokud jej nevybereme až za běhu
API_CONFIG = API_CONFIG_OPENAI

# Pomocná funkce pro nastavení aktuálního poskytovatele API
def setProvider(provider: dict):
    global API_CONFIG
    API_CONFIG = provider

# Pomocná funkce pro vytvoření instance OpenAI s aktuálním poskytovatelem API
def getProvider() -> OpenAI:
    return OpenAI(api_key=API_CONFIG["key"], base_url=API_CONFIG["url"])

# Pomocná funkce pro získání dostupných modelů aktuálního poskytovatele API
# Vracíme pole textových názvů modelů, které používáme i v anyFunction
def getAvailableModels() -> list[str]:
    client = getProvider()
    models = []
    try:
        resp = client.models.list()
    except Exception:
        return models

    for m in getattr(resp, "data", []):
        mid = getattr(m, "id", None)
        if isinstance(mid, str):
            models.append(mid)
    return models

# A toto je už naše univerzální funkce anyFunction
# Základní signatura je odpověď = anyFunction(vstupní data (buď jedna položka, nebo více promenných za sebou), prompt, datový typ odpovědi)
# Následují volitlené argumenty:
# - model (str) pro explicitní určení modelu aktuálního poskytovatele API
# - run (bool) pro určení, jestli hledáme konečnou odpvoěď, nebo AI generuje kód v Pythonu, který se spustí až na našem počítači (režim primitivního agenta)
def anyFunction(*args: Any, model: Optional[str] = None, run: bool = False) -> Any:

    if len(args) < 2:
        raise ValueError("Jsou potřeba alespoň vstupní data (případně None), prompt a typ odpovědi")
    return_type: Optional[Type] = None

    # Rozlišíme vstupní data a prompt z listu argumentů
    # Opět připomenu: Data mohou bát první argument, anebo řada argumentů:
    # Obě tato volání jsou správná:
    # - anyFunction(cisla, "Zjisti nejvetsi cislo")
    # - anyFunction(cislo1, cislo2, cislo3, "Zjisti nejvetsi cislo")

    if isinstance(args[-1], type):
        return_type = args[-1]
        prompt = args[-2]
        data_args = args[:-2]
    else:
        prompt = args[-1]
        data_args = args[:-1]

    if not isinstance(prompt, str):
        raise TypeError("Chybí prompt")
    
    if len(data_args) == 0:
        data = None
    elif len(data_args) == 1:
        data = data_args[0]
    else:
        data = list(data_args)

    try:
        data_repr = json.dumps(data, ensure_ascii=False, default=repr)
        data_format = "JSON"
    except TypeError:
        data_repr = repr(data)
        data_format = "Python repr"

    # A tady už začíná magie. Pokud spouštíme funkci v režimu lokálního interpretra/agenta,
    # připravíme systémový prompt, ve kterém modelu říkáme, že má podle uživatelského promptu 
    # vytvořit kód v Pythonu s patřičnými náležitostmi

    if run:
        system_prompt = (
            "You are a Python code generator.\n"
            "Given the input data and the user's natural language instruction, "
            "write Python code that performs the requested transformation or computation.\n"
            "The input data is available in the variable `data`.\n"
            "You may import standard libraries, define functions, start servers, etc.\n"
            "If you rely on `if __name__ == '__main__':`, it WILL be true.\n"
            "Store any final value that should be returned in a variable named `result` (optional).\n"
            "Output ONLY raw Python code, without backticks, markdown fences, comments or explanations.\n"
            "Do not use ``` or ```python anywhere in the response."
        )

    # Pokud funkci spouštíme v režimu hledání konečné odpovědi, systémový prompt se liší a my model pobízíme,
    # aby vracel data ve správném formátu bez další omáčky

    else:
        if return_type is None:
            type_instruction = (
                "Choose the most suitable Python data type for the answer. "
                "Respond with ONE valid Python literal expression only, "
                "without any explanation or comments."
            )
        else:
            type_name = getattr(return_type, "__name__", str(return_type))
            type_instruction = (
                f"Respond with ONE valid Python literal expression of type `{type_name}` "
                f"(or something that can be directly cast to `{type_name}`), "
                "without any explanation or comments."
            )

        system_prompt = (
            "You are a Python assistant that transforms input data according to the user's instructions.\n"
            "Always respond with a SINGLE valid Python literal expression that can be parsed by ast.literal_eval.\n"
            "Do not add any prose, comments or backticks.\n"
            + type_instruction
        )

    # Příprava uživatelského promptu, ve kterém spojíme samotný prompt se vstupními daty
    user_prompt = f"""User instruction (natural language):
    {prompt}

    Input data (format: {data_format}):
    {data_repr}
    """

    # Zkonsturujeme dotaz na model pomocí OpenAI API
    client = getProvider()
    used_model = model or API_CONFIG["model"]

    response = client.chat.completions.create(
        model=used_model,
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    # Získáme surovou odpověď
    raw_output = response.choices[0].message.content

    # Pokud jsme v režimu agenta, pokusíme se ji interpretovat jako kód Pythonu
    # Pozor, nebezpečné – kód bude mít stejná práva jako my a může cokoliv smazat
    if run:
        exec_env: dict[str, Any] = {
            "__name__": "__main__",
            "data": data,
        }
        # Některé modely ignorují systémový prompt, ve kterém žádáme, aby vrcely kód bez jakékoliv obálky
        # Proto se pokusíme odstranit typickou hlavičku ```python na začátku odpovědi
        if raw_output.startswith("```"):
            lines = raw_output.splitlines()
            if lines and lines[0].lstrip().startswith("```"):
                lines = lines[1:]
            while lines and lines[0].strip() == "":
                lines = lines[1:]
            if lines and lines[-1].lstrip().startswith("```"):
                lines = lines[:-1]
            raw_output = "\n".join(lines)
        # Interpretace/spuštění kódu
        exec(raw_output, exec_env)
        # Pokud kód vrací odpověď, vrátíme ji také
        return exec_env.get("result")

    # Převedení odpovědi modelu do správného datového typu, který požadujeme
    try:
        value = ast.literal_eval(raw_output)
    except Exception:
        value = raw_output

    if return_type is not None and not isinstance(value, return_type):
        try:
            if return_type in (list, tuple, set) and isinstance(value, str):
                items = [x.strip() for x in value.split(",") if x.strip()]
                if return_type is list:
                    value = items
                elif return_type is tuple:
                    value = tuple(items)
                else:
                    value = set(items)
            else:
                value = return_type(value)
        except Exception:
            pass

    return value
