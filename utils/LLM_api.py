import base64
from typing import Union, List
from zai import ZhipuAiClient
from config.setting import ZHIPUAI_API_KEY
import json
import re


def zhipu_llm(prompt):
    """
    调用智谱AI模型进行分析
    """
    client = ZhipuAiClient(api_key=ZHIPUAI_API_KEY)

    response = client.chat.completions.create(
        model="glm-4.6",
        messages=[
            {"role": "user", "content": prompt}
        ],
        thinking={
            "type": "disabled",
        },
        max_tokens=65536,
        temperature=0.1
    )
    return response.choices[0].message.content

def zhipu_llm_vison(
        image_paths: Union[str, List[str]],
        text: str,
        model: str = "glm-4.5v",
        enable_thinking: bool = True
) -> str:

    if isinstance(image_paths, str):
        image_paths = [image_paths]

    content = []

    for path in image_paths:
        with open(path, "rb") as img_file:
            img_base64 = base64.b64encode(img_file.read()).decode("utf-8")

        content.append({
            "type": "image_url",
            "image_url": {
                "url": img_base64
            }
        })

    content.append({
        "type": "text",
        "text": text
    })

    client = ZhipuAiClient(api_key=ZHIPUAI_API_KEY)

    response = client.chat.completions.create(
        model=model,
        messages=[
            {
                "role": "user",
                "content": content
            }
        ],
        thinking={
            "type": "enabled" if enable_thinking else "disabled"
        }
    )
    return response.choices[0].message.content


def parse_suggestion_response(response):
    """
    解析模型返回的建议响应
    """
    try:
        json_match = re.search(r'{[\s\S]*}', response)
        if json_match:
            json_str = json_match.group()
            return json.loads(json_str)
    except Exception as e:
        print(f"❌ 解析建议响应失败: {e}")

    return {
        "mapping_suggestions": [],
        "need_human_review": False
    }

