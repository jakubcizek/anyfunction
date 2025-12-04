from __future__ import annotations

from typing import Any, Optional, Type
from openai import OpenAI
import json
import ast

# API key pro OpenAI, svuj fakt nedam ;)
API_KEY = "bla bla bla"

'''
gpt-5.1      - nejdrazsi, ale schopny
gpt-5-mini   - o rad levnejsi, bude stacit
gpt-5-nano   - o dva rady levnejsi, muze stacit az na komplexni ulohy

https://platform.openai.com/docs/models
https://platform.openai.com/docs/pricing

'''
MODEL = "gpt-5.1" # Pozor, ve vychozim stavu nejdrazsi/nejlepsi model

client = OpenAI(api_key=API_KEY)

class Run:
    pass

def anyFunction(*args: Any, model: str = MODEL) -> Any:
    if len(args) < 2:
        raise ValueError("Je potřeba alespoň data a prompt.")

    run_mode = False
    return_type: Optional[Type] = None

    if args[-1] is Run:
        run_mode = True
        prompt = args[-2]
        data_args = args[:-2]
    elif isinstance(args[-1], type) and args[-1] is not Run:
        return_type = args[-1]
        prompt = args[-2]
        data_args = args[:-2]
    else:
        prompt = args[-1]
        data_args = args[:-1]

    if not isinstance(prompt, str):
        raise TypeError("Poslední (ne-typový) argument musí být textový prompt (str).")
    
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

    if run_mode:
        system_prompt = (
            "You are a Python code generator.\n"
            "Given the input data and the user's natural language instruction, "
            "write Python code that performs the requested transformation or computation.\n"
            "The input data is available in the variable `data`.\n"
            "You may import standard libraries, define functions, start servers, etc.\n"
            "If you rely on `if __name__ == '__main__':`, it WILL be true.\n"
            "Store any final value that should be returned in a variable named `result` (optional).\n"
            "Output ONLY raw Python code, without backticks, comments or explanations."
        )
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

    user_prompt = f"""User instruction (natural language):
{prompt}

Input data (format: {data_format}):
{data_repr}
"""
    response = client.responses.create(
        model=model,
        input=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": user_prompt},
        ],
    )

    raw_output = response.output_text

    if run_mode:
        exec_env: dict[str, Any] = {
            "__name__": "__main__",
            "data": data,
        }
        exec(raw_output, exec_env)
        return exec_env.get("result")

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
