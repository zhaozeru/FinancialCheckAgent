from langgraph.graph import StateGraph, END, START
from schemas.state_schema import MaingraphState
from langgraph.checkpoint.memory import InMemorySaver
from nodes.pretreatment_node import pretreatment_node1, pretreatment_node2
from nodes.combine_node import combine_node
from nodes.analysis_node import analysis_node
from nodes.restock_node import restock_node
from nodes.human_review_node import human_review_node
from nodes.add_mappings_node import add_mappings_node

def should_trigger_human_review(state: MaingraphState) -> str:
    """
    判断是否触发人工监督
    """
    needs_review = state.get('needs_human_review', False)
    has_suggestions = len(state.get('mapping_suggestions', [])) > 0
    if needs_review and has_suggestions:
        return "human_review"
    else:
        return END

def create_audit_graph():
    # 主图
    workflow = StateGraph(MaingraphState)

    # 创建Nodes
    workflow.add_node("pretreatment1", pretreatment_node1)
    workflow.add_node("pretreatment2", pretreatment_node2)
    workflow.add_node("combine", combine_node)
    workflow.add_node("analysis", analysis_node)
    workflow.add_node("restock", restock_node)
    workflow.add_node("human_review", human_review_node)
    workflow.add_node("add_mappings", add_mappings_node)

    # 创建edges
    workflow.add_edge(START, "pretreatment1")
    workflow.add_edge(START, "pretreatment2")
    workflow.add_edge("pretreatment1", "combine")
    workflow.add_edge("pretreatment2", "combine")
    workflow.add_edge("combine", "analysis")
    workflow.add_edge("analysis", "restock")
    workflow.add_conditional_edges(
        "restock",
        should_trigger_human_review,
        [END, "human_review"],
    )
    workflow.add_edge("add_mappings", END)

    checkpointer = InMemorySaver()
    graph = workflow.compile(checkpointer=checkpointer)

    return graph