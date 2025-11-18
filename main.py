from dotenv import load_dotenv
load_dotenv()
from graph.graph_built import create_audit_graph
from langgraph.types import Command
import uuid
from langsmith import traceable
import os


# 检查是否启用追踪
if os.getenv("LANGCHAIN_TRACING_V2") != "true":
    print("⚠️ 提示: 未启用 LANGCHAIN_TRACING_V2=true，LangSmith 追踪将被禁用")
    print("💡 请在 .env 文件中添加: LANGCHAIN_TRACING_V2=true")
def setup_langsmith():
    """初始化LangSmith配置"""
    try:
        from langsmith import Client
        client = Client()
        # 测试连接（可选）
        list(client.list_projects())  # 触发实际请求
        print("✅ LangSmith 配置成功!")
        project_name = os.getenv("LANGCHAIN_PROJECT", "FinancialCheckAgent-Audit")
        print(f"📊 追踪项目: {project_name}")
        return True
    except Exception as e:
        print(f"⚠️ LangSmith 配置警告: {e} - 继续执行但不追踪")
        return False

# ==================== 追踪装饰的函数 ====================
@traceable(name="financial_agent.run_formatting_process", run_type="chain")
def run_formatting_process(image_path: str, thread_id: str = None):
    config = {"configurable": {"thread_id": thread_id or str(uuid.uuid4())}}
    initial_state = {"image_path": image_path}

    print(f"🎯 开始处理图片: {image_path}")
    final_state = app.invoke(initial_state, config=config)
    print("✅ 图片处理流程执行完成")
    return final_state


@traceable(name="financial_agent.handle_user_decision", run_type="tool")
def handle_user_decision(decision: str, thread_id: str):
    config = {"configurable": {"thread_id": thread_id}}

    print(f"🔄 处理用户决策: {decision}")
    final_state = app.invoke(Command(resume=decision), config=config)
    print("✅ 用户决策已应用，流程继续执行完成")
    return final_state

@traceable(name="financial_agent.get_user_input", run_type="tool")
def get_user_input():
    """获取用户输入 - 被LangSmith追踪"""
    while True:
        user_input = input("请输入你的决定 (y/n): ").lower().strip()
        if user_input in ['y', 'yes', '是', 'add in']:
            return "add in"
        elif user_input in ['n', 'no', '否']:
            return "cancel"
        else:
            print("请输入 y/yes/是/add in 或 n/no/否")


# ==================== 主执行流程 ====================

@traceable(name="financial_agent.main_execution", run_type="chain")
def main_execution():
    """主执行流程 - 被LangSmith追踪"""
    TEST_IMAGE_PATH1 = r"C:\Users\13652\Desktop\财务智能体\FinancialCheckAgent\data\测试-分摊表.png"
    TEST_IMAGE_PATH2 = r"C:\Users\13652\Desktop\财务智能体\FinancialCheckAgent\data\测试-系统数据.jpg"
    image_path = [TEST_IMAGE_PATH1, TEST_IMAGE_PATH2]
    thread_id = str(uuid.uuid4())

    print(f"🚀 开始测试，thread_id: {thread_id}\n")
    print("📊 LangSmith追踪已激活，查看: https://smith.langchain.com/")

    # 第一阶段：初始执行
    try:
        print("🔹 阶段1: 初始执行流程")
        final_state_1 = run_formatting_process(image_path, thread_id)
        print("✅ 阶段1完成")

    except Exception as e:
        print(f"❌ 第一次执行出错: {e}")
        raise

    # 第二阶段：用户决策后继续执行
    try:
        print("\n🔹 阶段2: 等待用户决策")
        decision = get_user_input()
        print(f"🎯 用户决策: {decision}")
        final_state_2 = handle_user_decision(decision, thread_id)
        print("✅ 阶段2完成")

    except Exception as e:
        print(f"❌ 中断后执行出错: {e}")
        raise


# ==================== 全局应用实例 ====================
app = create_audit_graph()
if __name__ == "__main__":
    langsmith_enabled = setup_langsmith()
    if not langsmith_enabled:
        print("💡 提示: 要启用完整追踪，请设置:")
        print("   - LANGCHAIN_API_KEY=your_key")
        print("   - LANGCHAIN_TRACING_V2=true")
        print("   - LANGCHAIN_PROJECT=FinancialCheckAgent-Audit (可选)")

    main_execution()
    print("\n🎉 流程执行完成!")
    if langsmith_enabled:
        print("📊 请访问 https://smith.langchain.com/ 查看详细追踪数据")