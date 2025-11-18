import sqlite3
from typing import Literal, Optional, TypedDict

from langgraph.checkpoint.memory import MemorySaver
from langgraph.graph import StateGraph, START, END
from langgraph.types import Command, interrupt


def add_mappings_node2(state: MaingraphState) -> dict:
    """
    向映射规则YAML文件中添加新规则
    """
    try:
        mapping_file_path = 'C:\\Users\\13652\\Desktop\\财务智能体\\FinancialCheckAgent\\tools\\mapping_relations.yaml'

        # 加载现有的映射规则
        try:
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                mapping_rules = yaml.safe_load(f) or {}
        except FileNotFoundError:
            mapping_rules = {}

        # 确保必要的结构存在
        if 'row_equivalences' not in mapping_rules:
            mapping_rules['row_equivalences'] = {}

        if 'column_equivalences' not in mapping_rules:
            mapping_rules['column_equivalences'] = {}

        # 直接从state获取扁平化的建议数据（restock_node返回的是扁平结构）
        mapping_suggestions = state.get('mapping_suggestions', [])

        if not mapping_suggestions:
            print("⚠️ 没有可用的映射建议")
            state['mapping_addition_status'] = "no_suggestions_available"
            return state

        print(f"📋 开始处理 {len(mapping_suggestions)} 条映射建议...")

        added_mappings = []
        skipped_mappings = []

        for suggestion in mapping_suggestions:
            table1_name = suggestion.get('table1_name', '').strip()
            table2_name = suggestion.get('table2_name', '').strip()
            mapping_type = suggestion.get('type', 'row')  # row 或 column
            confidence = suggestion.get('confidence', 'medium')
            reason = suggestion.get('reason', '')
            suggestion_text = suggestion.get('suggestion', '')

            # 验证必要字段
            if not table1_name or not table2_name:
                print(f"⚠️ 跳过无效建议：缺少表名")
                skipped_mappings.append({
                    'reason': '缺少表名',
                    'suggestion': suggestion
                })
                continue

            if table1_name == table2_name:
                print(f"⚠️ 跳过相同名称：{table1_name}")
                skipped_mappings.append({
                    'reason': '表名相同',
                    'from': table2_name,
                    'to': table1_name
                })
                continue

            # 根据映射类型处理
            target_section = None
            if mapping_type == 'row':
                target_section = mapping_rules['row_equivalences']
            elif mapping_type == 'column':
                target_section = mapping_rules['column_equivalences']
            else:
                print(f"⚠️ 未知映射类型：{mapping_type}，默认为行映射")
                target_section = mapping_rules['row_equivalences']

            # 检查是否已存在映射（避免覆盖）
            existing_mapping = None
            for existing_key, existing_value in target_section.items():
                if existing_key == table2_name or existing_value == table1_name:
                    existing_mapping = {
                        'key': existing_key,
                        'value': existing_value,
                        'type': mapping_type
                    }
                    break

            if existing_mapping:
                print(
                    f"⚠️ 映射已存在：{table2_name} -> {table1_name} (已有: {existing_mapping['key']} -> {existing_mapping['value']})")
                skipped_mappings.append({
                    'reason': '映射已存在',
                    'from': table2_name,
                    'to': table1_name,
                    'existing_mapping': existing_mapping
                })
                continue

            # 添加新的映射规则
            target_section[table2_name] = table1_name
            added_mappings.append({
                'from': table2_name,
                'to': table1_name,
                'type': mapping_type,
                'confidence': confidence,
                'reason': reason,
                'suggestion': suggestion_text,
                'added_time': datetime.now().isoformat()
            })
            print(f"✅ 添加{mapping_type}映射: {table2_name} -> {table1_name} (置信度: {confidence})")

        # 处理结果
        if added_mappings:
            # 添加更新记录
            if 'update_history' not in mapping_rules:
                mapping_rules['update_history'] = []

            update_record = {
                'timestamp': datetime.now().isoformat(),
                'action': 'auto_added_mappings',
                'added_count': len(added_mappings),
                'skipped_count': len(skipped_mappings),
                'added_mappings': added_mappings,
                'skipped_mappings': skipped_mappings
            }
            mapping_rules['update_history'].append(update_record)

            # 保存更新后的规则（不会覆盖原有规则）
            with open(mapping_file_path, 'w', encoding='utf-8') as f:
                yaml.dump(mapping_rules, f,
                          allow_unicode=True,
                          indent=2,
                          default_flow_style=False,
                          sort_keys=False)  # 保持原有顺序

            print(f"🎯 成功添加 {len(added_mappings)} 条映射规则到YAML文件")
            print(f"⏰ 跳过 {len(skipped_mappings)} 条无效或重复的映射")
            state['mapping_addition_status'] = f"success_added_{len(added_mappings)}"
            state['added_mappings'] = added_mappings
            state['skipped_mappings'] = skipped_mappings
        else:
            print("⚠️ 未添加任何新的映射规则")
            state['mapping_addition_status'] = "no_new_mappings_added"
            state['skipped_mappings'] = skipped_mappings

    except Exception as e:
        print(f"❌ 添加映射规则到YAML文件失败: {e}")
        state['mapping_addition_status'] = f"error: {str(e)}"

    return state
class ApprovalState(TypedDict):
    action_details: str
    status: Optional[Literal["pending", "approved", "rejected"]]


def approval_node(state: ApprovalState) -> Command[Literal["proceed", "cancel"]]:
    # Expose details so the caller can render them in a UI
    decision = interrupt({
        "question": "Approve this action?",
        "details": state["action_details"],
    })

    # Route to the appropriate node after resume
    return Command(goto="proceed" if decision else "cancel")


def proceed_node(state: ApprovalState):
    return {"status": "approved"}


def cancel_node(state: ApprovalState):
    return {"status": "rejected"}


builder = StateGraph(ApprovalState)
builder.add_node("approval", approval_node)
builder.add_node("proceed", proceed_node)
builder.add_node("cancel", cancel_node)
builder.add_edge(START, "approval")
builder.add_edge("proceed", END)
builder.add_edge("cancel", END)

# Use a more durable checkpointer in production
checkpointer = MemorySaver()
graph = builder.compile(checkpointer=checkpointer)

config = {"configurable": {"thread_id": "approval-123"}}
initial = graph.invoke(
    {"action_details": "Transfer $500", "status": "pending"},
    config=config,
)
print(initial["__interrupt__"])  # -> [Interrupt(value={'question': ..., 'details': ...})]

# Resume with the decision; True routes to proceed, False to cancel
resumed = graph.invoke(Command(resume=True), config=config)
print(resumed["status"])  # -> "approved"
