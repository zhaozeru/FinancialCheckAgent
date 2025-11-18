import re

def extract_tuples(response):
    """从响应文本中提取两个元组列表"""
    if isinstance(response, list):
        response = str(response)
    elif hasattr(response, 'content'):
        response = response.content
    else:
        response = str(response)

    # 查找完整的双重列表结构
    list_match = re.search(r'\[\[.*?\]\s*,\s*\[.*?\]\]', response, re.DOTALL)
    if list_match:
        list_str = list_match.group(0)

        # 提取两个子列表的内容
        sublists = re.findall(r'\[(.*?)\]', list_str, re.DOTALL)
        if len(sublists) >= 2:
            detail_items = _extract_from_sublist(sublists[0])
            summary_items = _extract_from_sublist(sublists[1])
            return [detail_items, summary_items]

    # 如果没有找到明确的双重列表，提取所有元组
    all_items = _extract_from_sublist(response)
    return [all_items, []]


def _extract_from_sublist(text):
    """从文本中提取所有有效的元组"""
    items = []
    # 匹配 (行标签, 列标签, 数值) 格式
    matches = re.findall(r'\(\s*["\']?([^,"\']+?)["\']?\s*,\s*["\']?([^,"\']+?)["\']?\s*,\s*["\']?(\d+)["\']?\s*\)',
                         text)

    for row_name, col_name, value_str in matches:
        row_name = row_name.strip().strip("'\"")
        col_name = col_name.strip().strip("'\"")

        if row_name and col_name:
            try:
                value = int(value_str)
                if value != 0:
                    items.append((row_name, col_name, value))
            except ValueError:
                continue

    return items