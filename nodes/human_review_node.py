from schemas.state_schema import MaingraphState
from langgraph.types import Command, interrupt
from langgraph.graph import END

def human_review_node(state: MaingraphState) -> Command:
    """
    人工监督节点：等待用户确认是否添加映射规则
    """
    print("👤 触发人工监督流程")
    decision = interrupt({
        "question": f"检测到 {len(state['mapping_suggestions'])} 条映射建议，是否同意添加到映射规则文件？\n输入 'add in' 确认添加，输入其他内容取消。",
    })

    if decision and decision.strip().lower() == "add in":
        print("✅ 用户确认添加映射规则")
        return Command(goto="add_mappings")
    else:
        print("❌ 用户取消添加映射规则")
        return Command(goto=END, update={"mapping_addition_status": "cancelled_by_user"})


