import yaml
from schemas.state_schema import MaingraphState

# 加载映射关系
with open('C:\\Users\\13652\\Desktop\\财务智能体\\FinancialCheckAgent\\tools\\mapping_relations.yaml', 'r', encoding='utf-8') as f:
    mapping_relations = yaml.safe_load(f)
def get_equivalent_row(table1_row):
    return mapping_relations['row_equivalences'].get(table1_row)
def standardize_table_data(table_tuples, table_type):
    """
    标准化表格数据，将行列名转换为标准名称

    Args:
        table_tuples: 表格的元组列表，可能是嵌套结构 [[子数据], [汇总数据]]
        table_type: 表格类型 ('table1' 或 'table2')

    Returns:
        list: 标准化后的元组列表
    """
    standardized_tuples = []

    # 处理嵌套的列表结构
    if (isinstance(table_tuples, list) and len(table_tuples) == 2 and
            isinstance(table_tuples[0], list) and isinstance(table_tuples[1], list)):
        # 如果是 [[子数据], [汇总数据]] 的结构，展平
        flattened_tuples = []
        for sublist in table_tuples:
            if isinstance(sublist, list):
                flattened_tuples.extend(sublist)
            else:
                flattened_tuples.append(sublist)
        table_tuples = flattened_tuples

    # 现在处理扁平的元组列表
    for item in table_tuples:
        if isinstance(item, tuple) and len(item) == 3:
            row_name, col_name, value = item

            # 标准化行名
            standardized_row = row_name
            if table_type == 'table1':
                # table1 作为基准，查找是否有对应的 table2 名称
                equivalent = get_equivalent_row(row_name)
                if equivalent:
                    standardized_row = equivalent
            else:  # table2
                # table2 转换为 table1 的标准名称
                for base_row, equiv_row in mapping_relations['row_equivalences'].items():
                    if row_name == base_row:
                        standardized_row = equiv_row
                        break

            # 标准化列名（类似逻辑）
            standardized_col = col_name
            if table_type == 'table2':
                # table2 列名转换为 table1 标准列名
                for base_col, equiv_col in mapping_relations.get('column_equivalences', {}).items():
                    if col_name == equiv_col:
                        standardized_col = base_col
                        break

            standardized_tuples.append((standardized_row, standardized_col, value))
        else:
            print(f"⚠️ 跳过无效数据项: {item}")

    return standardized_tuples

def combine_node(state: MaingraphState) -> dict:
    """
    对两个图片各自的元组列表做行列名的归一化处理
    """
    print("!!! 开始执行归一化节点 !!!")

    # 从状态中获取两个表的元组数据
    table1_tuples = state.get('pic_tuples_1', [])
    table2_tuples = state.get('pic_tuples_2', [])

    if not table1_tuples and not table2_tuples:
        print("❌ 没有找到表格数据")
        return state

    print(f"📊 图片1原始数据: {len(table1_tuples)} 个元组")
    print(f"📊 图片2原始数据: {len(table2_tuples)} 个元组")

    # 分别对两个图片的数据进行归一化处理
    standardized_table1 = standardize_table_data(table1_tuples, 'table1')
    standardized_table2 = standardize_table_data(table2_tuples, 'table2')

    print(f"✅ 图片1归一化后: {len(standardized_table1)} 个元组")
    print(f"✅ 图片2归一化后: {len(standardized_table2)} 个元组")

    # 打印归一化前后的变化
    print_standardization_changes(table1_tuples, standardized_table1, "图片1")
    print_standardization_changes(table2_tuples, standardized_table2, "图片2")

    return {'standardized_pic_tuples_1': standardized_table1,
            'standardized_pic_tuples_2': standardized_table2}


def print_standardization_changes(original_tuples, standardized_tuples, table_name):
    """打印标准化前后的变化"""
    print(f"\n=== {table_name} 标准化变化 ===")
    changes_found = False

    # 展平原始数据结构
    def flatten_tuples(data):
        flattened = []
        for item in data:
            if isinstance(item, list):
                flattened.extend(flatten_tuples(item))
            elif isinstance(item, tuple) and len(item) == 3:
                flattened.append(item)
        return flattened

    original_flat = flatten_tuples(original_tuples)
    standardized_flat = flatten_tuples(standardized_tuples)

    # 确保两个列表长度相同
    min_len = min(len(original_flat), len(standardized_flat))

    for i in range(min_len):
        orig = original_flat[i]
        std = standardized_flat[i]

        if orig != std:
            changes_found = True
            orig_row, orig_col, orig_val = orig
            std_row, std_col, std_val = std

            row_change = f"{orig_row} -> {std_row}" if orig_row != std_row else f"{orig_row} (不变)"
            col_change = f"{orig_col} -> {std_col}" if orig_col != std_col else f"{orig_col} (不变)"

            print(f"  元组 {i + 1}: 行[{row_change}], 列[{col_change}], 值{orig_val}")

    if not changes_found:
        print(f"  无变化")
