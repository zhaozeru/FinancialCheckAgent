from schemas.state_schema import MaingraphState
from utils.LLM_api import zhipu_llm, parse_suggestion_response

def restock_node(state: MaingraphState) -> dict:
    """
    建议补充节点：分析差异项并生成映射规则建议
    """
    print("!!! 开始执行建议补充节点 !!!")

    # 从状态中获取数据
    standardized_table1 = state.get('standardized_pic_tuples_1', [])
    standardized_table2 = state.get('standardized_pic_tuples_2', [])
    analysis_report = state.get('analysis_report', '')

    if not standardized_table1 or not standardized_table2:
        print("❌ 缺少标准化后的表格数据")
        state['restock_error'] = "缺少标准化后的表格数据"
        return state

    # 准备建议生成提示词
    suggestion_prompt = f"""
    作为数据映射专家，请分析两个表格中的差异项，识别可能存在的映射关系。

    ## 数据源：
    **表格1数据:** {standardized_table1}

    **表格2数据:** {standardized_table2}

    ## 前期分析报告：
    {analysis_report}

    ## 任务要求：
    请重点分析以下不匹配项，判断它们是否可能指向相同的业务概念：

    ### 已知差异项：
    1. 20RF在表1中对应YML，在表2中对应MSC
    2. 40RF在表1中MSC=343，在表2中MSC=363，存在20的差异
    3. 40RF在表1中有YML=20，表2中无YML数据
    4. 表2有翻倒统计相关数据，表1无对应项

    ### 输出要求：
    请严格按照以下JSON格式输出，不要包含其他内容：
    {{
        "mapping_suggestions": [
            {{
                "table1_name": "表1中的名称",
                "table2_name": "表2中的名称", 
                "type": "row/column",
                "confidence": "high/medium/low",
                "reason": "判断理由",
                "suggestion": "具体的映射建议"
            }}
        ],
        "need_human_review": true/false
    }}
    """

    print("📋 准备建议生成数据完成，开始调用模型...")

    try:
        # 调用模型获取建议
        suggestion_response = zhipu_llm(suggestion_prompt)
        state['mapping_suggestions_raw'] = suggestion_response
        print("✅ 建议生成完成")

        # 解析建议响应
        suggestions_data = parse_suggestion_response(suggestion_response)

        # 将数据扁平化存储到state中
        state['mapping_suggestions'] = suggestions_data.get('mapping_suggestions', [])
        state['need_human_review'] = suggestions_data.get('need_human_review', False)
        state['suggestions_count'] = len(state['mapping_suggestions'])

        # 判断是否需要人工监督
        if state['need_human_review'] or state['suggestions_count'] > 0:
            print("🚨 检测到映射建议，触发人工监督流程")
            state['needs_human_review'] = True
            state['review_type'] = "mapping_addition"
        else:
            print("✅ 无映射建议，流程正常结束")
            state['needs_human_review'] = False

    except Exception as e:
        print(f"❌ 建议补充节点执行出错: {e}")
        state['restock_error'] = str(e)
        state['needs_human_review'] = False

    return state


