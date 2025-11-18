import re

def extract_row_col(response: str) -> tuple[list, list]:
    """
    从大模型响应中提取所有行名和列名
    Args:
        response: 大模型返回的响应文本，包含元组数据
    Returns:
        tuple: (行名列表, 列名列表)
    """
    # 类型检查和处理
    if isinstance(response, list):
        response = str(response)
    elif not isinstance(response, str):
        response = str(response)

    # 初始化集合用于去重
    row_names_set = set()
    col_names_set = set()

    # 匹配元组模式 - 改进版，更严格匹配
    pattern = r'\(\s*["\']?([^,"\']+?)["\']?\s*,\s*["\']?([^,"\']+?)["\']?\s*,\s*["\']?(\d+)["\']?\s*\)'
    matches = re.findall(pattern, response)

    for match in matches:
        if len(match) >= 2:
            # 提取行名和列名，去除前后空格和引号
            row_name = match[0].strip().strip("'\"")
            col_name = match[1].strip().strip("'\"")
            value_str = match[2].strip().strip("'\"")

            # 只添加非空的名称，并且数值不为0
            if row_name and col_name:
                try:
                    value = int(value_str)
                    if value != 0:  # 只处理非零值
                        row_names_set.add(row_name)
                        col_names_set.add(col_name)
                except ValueError:
                    # 如果数值转换失败，也添加（保持原有逻辑）
                    row_names_set.add(row_name)
                    col_names_set.add(col_name)

    row_names = sorted(list(row_names_set))  # 排序以便更好查看
    col_names = sorted(list(col_names_set))

    print(f"📊 提取到 {len(row_names)} 个唯一行名: {row_names}")
    print(f"📊 提取到 {len(col_names)} 个唯一列名: {col_names}")

    return row_names, col_names