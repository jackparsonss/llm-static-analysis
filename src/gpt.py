import os
import json
from openai import OpenAI
from dotenv import load_dotenv

load_dotenv()

client = OpenAI(api_key=os.getenv("OPENAI_API_KEY"), organization=os.getenv("ORG_ID"))


def query(model, content, prompt):
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {"role": "user", "content": prompt},
            {"role": "user", "content": content},
        ],
    )

    return json.loads(response.choices[0].message.content)["modified_python_file"]


def rank(model, original_file, modified_file, prompt):
    response = client.chat.completions.create(
        model=model,
        response_format={"type": "json_object"},
        messages=[
            {
                "role": "system",
                "content": "You are a helpful assistant designed to output JSON.",
            },
            {"role": "user", "content": prompt},
            {"role": "user", "content": original_file},
            {"role": "user", "content": modified_file}
        ],
    )

    return json.loads(response.choices[0].message.content)["ranking"]
