from schemas.state_schema import MaingraphState
from utils.LLM_api import zhipu_llm_vison
from utils.save_tuples import save_tuples_to_txt
from utils.extract_tuples import extract_tuples
from utils.collect_rows_and_columns import extract_row_col
from utils.read_tuples import load_tuples_from_txt

def pretreatment_node1(state: MaingraphState) -> dict:
    print("!!! 开始执行预处理节点1 !!!")
    pic_path = state['image_path'][0]

    tuple_prompt = """
    作为表格数据提取专家，请准确识别并输出图片中表格的所有有效数据。

    ## 表格结构说明：
    这是一个标准的二维表格：
    - 行：表示具体的箱型分类（20GP, 20RF, 40GP等）
    - 列：表示结算船公司（MSC, YML, 进口合计）
    - 数据：表示对应的箱量数值

    ## 任务说明：
    扫描整个表格，识别出：
    1. 数据行标签（通常在数据的左边一列，紧挨着数据区域）
    2. 数据列标签（通常在数据的上一行，紧挨着数据区域） 
    3. 行列交叉点的数值数据

    ## 提取策略：
    - 只提取有效数据，不提取数据为0或为空值的单元格
    - 图片中有子项数据和汇总数据两类，对于行、列名中若出现“总体”、“总计”、“合计”、“小计”、“SUB-TOTAL”等表示汇总意思的关键词，则将他们单独提取出来
    - 若出现相同行名或列名，则将上一级标签与下一级标签组合，形成唯一标识，如"20重箱SUB-TOTAL", "40重箱SUB-TOTAL"
    - 以元组形式输出，如(数据行文本, 数据列文本, 整数值)

    ## 输出要求：
    1、输出格式：一个包含两个列表的列表 [[子数据项列表], [汇总数据项列表]]
        - 第一个子列表：包含所有非汇总数据的元组，如 [("20GP", "MSC", 100), ("20RF", "YML", 50), ...]
        - 第二个子列表：包含所有汇总数据的元组，如 [("20重箱SUB-TOTAL", "MSC", 300), ("总体合计", "进口合计", 1000), ...]
    2、每个数据项格式：(行标签, 列标签, 数值)
        - 行标签：如 "20GP", "20RF", "20重箱SUB-TOTAL"
        - 列标签：如 "MSC", "YML", "进口合计"  
        - 数值：整数，如 100, 50, 300
    3、严格只输出数据，不包含任何其他描述文字、解释或注释

    ## 特别注意：
    - 图片中所有数据点都有对应元组，数量要准确
    - 不要创建复杂的层级组合
    - 严格按照表格中数值的实际位置提取
    - 确保数值与行列标签正确对应
    """
    # pic_response = load_tuples_from_txt('pic_tuples_1')
    pic_response = zhipu_llm_vison(pic_path, tuple_prompt, model="glm-4.5v", enable_thinking=False)
    # print("----------------------------图片1表格数据模型返回结果-----------------------")
    # print(pic_response)
    pic_tuples = extract_tuples(pic_response)
    # print("图片1元组数量：",len(pic_tuples))
    # 收集图片中所有行列名
    row_names, col_names = extract_row_col(pic_response)
    # print("图片1行数量：",len(row_names))
    # print("图片1列数量：",len(col_names))
    # 保存元组到txt文件
    save_tuples_to_txt(pic_tuples, file_name="pic_tuples_1")

    print("!!! ✅ 预处理节点1执行完成 !!!")
    return {
        "pic_tuples_1": pic_tuples,
        "row_names_1": row_names,
        "col_names_1": col_names
    }


def pretreatment_node2(state: MaingraphState) -> dict:
    print("!!! 开始执行预处理节点2 !!!")
    pic_path = state['image_path'][1]
    tuple_prompt = """
    作为表格数据提取专家，请准确识别并输出图片中表格的所有有效数据。

    ## 表格结构说明：
    这是一个标准的二维表格：
    - 行：表示具体的箱型分类（20GP, 20RF, 40GP等）
    - 列：表示结算船公司（MSC, YML, 进口合计）
    - 数据：表示对应的箱量数值

    ## 任务说明：
    扫描整个表格，识别出：
    1. 数据行标签（通常在数据的左边一列，紧挨着数据区域）
    2. 数据列标签（通常在数据的上一行，紧挨着数据区域） 
    3. 行列交叉点的数值数据

    ## 提取策略：
    - 只提取有效数据，不提取数据为0或为空值的单元格
    - 图片中有子项数据和汇总数据两类，对于行、列名中若出现“总体”、“总计”、“合计”、“小计”、“SUB-TOTAL”等表示汇总意思的关键词，则将他们单独提取出来
    - 若出现相同行名或列名，则将上一级标签与下一级标签组合，形成唯一标识，如"20重箱SUB-TOTAL", "40重箱SUB-TOTAL"
    - 以元组形式输出，如(数据行文本, 数据列文本, 整数值)

    ## 输出要求：
    1、输出为列表格式，如[ [(),(),...] , [(),(),...] ]，大列表中两个子列表分别对应着图片中的子数据项和汇总数据项
    2、其他描述内容不输出。

    ## 特别注意：
    - 图片中所有数据点都有对应元组，数量要准确
    - 不要创建复杂的层级组合
    - 严格按照表格中数值的实际位置提取
    - 确保数值与行列标签正确对应
    """
    # pic_response = load_tuples_from_txt('pic_tuples_2')
    pic_response = zhipu_llm_vison(pic_path, tuple_prompt, model="glm-4.5v", enable_thinking=False)
    # print("----------------------------图片2表格数据模型返回结果-----------------------")
    # print(pic_response)

    # 收集所有元组
    pic_tuples = extract_tuples(pic_response)
    # print("图片2元组数量：",len(pic_tuples))

    # 收集图片中所有行列名
    row_names, col_names = extract_row_col(pic_response)
    # print("图片2行数量：",len(row_names))
    # print("图片2列数量：",len(col_names))

    # 保存元组到txt文件
    save_tuples_to_txt(pic_tuples, file_name="pic_tuples_2")
    print("!!! ✅ 预处理节点2执行完成 !!!")

    return {
        "pic_tuples_2": pic_tuples,
        "row_names_2": row_names,
        "col_names_2": col_names,
    }