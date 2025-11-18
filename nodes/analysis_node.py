from schemas.state_schema import MaingraphState
import yaml
from utils.LLM_api import zhipu_llm


# 加载聚合规则
with open('C:\\Users\\13652\\Desktop\\财务智能体\\FinancialCheckAgent\\tools\\aggregation_rules.yaml', 'r', encoding='utf-8') as f:
    aggregation_rules = yaml.safe_load(f)

# 加载映射关系
with open('C:\\Users\\13652\\Desktop\\财务智能体\\FinancialCheckAgent\\tools\\mapping_relations.yaml', 'r', encoding='utf-8') as f:
    mapping_relations = yaml.safe_load(f)


def analysis_node(state: MaingraphState) -> dict:
    """
    分析节点：核对两个图中聚合后的数值是否对应
    """
    print("!!! 开始执行分析节点 !!!")

    # 从状态中获取标准化后的数据
    standardized_table1 = state.get('standardized_pic_tuples_1', [])
    standardized_table2 = state.get('standardized_pic_tuples_2', [])

    if not standardized_table1 or not standardized_table2:
        print("❌ 缺少标准化后的表格数据")
        return state

    # 准备分析提示词
    analysis_prompt = f"""
    作为财务数据分析专家，请系统性地核对两个标准化表格中的数据一致性。
    
    ## 数据源：
    **表格1（标准化后）:** {standardized_table1}
    
    **表格2（标准化后）:** {standardized_table2}
    
    ## 聚合规则参考：
    {aggregation_rules}
    
    ## 映射关系参考：
    {mapping_relations}
    
    ## 详细分析任务：
    
    ### 第一步：基础子项数据核对
    请逐一检查两个表格中相同行名列名组合的基础数据项是否一致：
    - 对比所有基础箱型数据（如20GP、20RF、40GP、40RF等）
    - 检查相同业务概念的数值是否匹配
    - 记录所有发现的不一致项
    
    ### 第二步：汇总项数据核对
    请检查主要汇总项的计算准确性：
    1. **20尺箱汇总核对**
       - 表格1中的"20重箱SUB-TOTAL"与表格2中的"20尺合计"是否一致
       - 检查各自的子项加总是否等于汇总值
    
    2. **40尺箱汇总核对**  
       - 表格1中的"40重箱SUB-TOTAL"与表格2中的"40尺合计"是否一致
       - 检查各自的子项加总是否等于汇总值
    
    3. **其他汇总项核对**
       - 检查其他汇总项（如统计、翻倒统计等）的逻辑一致性
    
    ### 第三步：数据质量评估
    - 计算整体数据匹配率
    - 识别主要差异点和可能的原因
    - 评估数据可靠性和一致性水平
    
    ## 输出格式要求：
    
    ### 📊 数据一致性分析报告
    
    #### 🔍 基础子项核对结果
    **匹配项：**
    - [具体行名+列名]: 表1值 = 表2值 = [数值]
    
    **不匹配项：**
    - [具体行名+列名]: 表1值 = [值1], 表2值 = [值2], 差异 = [差值]
    
    #### 📈 汇总项核对结果
    **20尺箱汇总：**
    - 表1 20重箱SUB-TOTAL: [数值]
    - 表2 20尺合计: [数值] 
    - 状态: [✅匹配/❌不匹配]
    - 子项加总验证: [通过/不通过]
    
    **40尺箱汇总：**
    - 表1 40重箱SUB-TOTAL: [数值]
    - 表2 40尺合计: [数值]
    - 状态: [✅匹配/❌不匹配]  
    - 子项加总验证: [通过/不通过]
       
    请确保分析全面、准确，为后续决策提供可靠依据。
    """
    try:
        print("Prompt总字符数为：", len(analysis_prompt))
        analysis_response = zhipu_llm(analysis_prompt)
        state['analysis_report'] = analysis_response
        print("✅ 分析节点执行完成")
    except Exception as e:
        print(f"❌ 分析节点执行出错: {e}")
        state['analysis_error'] = str(e)
    return state