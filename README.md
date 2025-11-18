# FinancialCheckAgent - 财务数据自动核对工具

[![Python](https://img.shields.io/badge/Python-3.9%2B-blue?logo=python)](https://www.python.org/)
[![LangChain](https://img.shields.io/badge/LangChain-%E2%9C%93-brightgreen)](https://www.langchain.com/)
[![LangGraph](https://img.shields.io/badge/LangGraph-%E2%9C%93-00a67e?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQTEwIDEwIDAgMCAwIDIgMTJhMTAgMTAgMCAwIDAgMTAgMTAgMTAgMTAgMCAwIDAtMTAtMTBtMCAxOGMtNC40MSAwLTgtMy41OS04LThzMy41OS04IDgtOCA4IDMuNTkgOCA4LTMuNTkgOC04IDh6Ii8+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xNi41IDEybC00LjUgNC41VjE1SDl2LTRoMnYxLjVsMy41LTMuNUwxNi41IDEyeiIvPjwvc3ZnPg==)](https://python.langchain.com/docs/langgraph)
[![LangSmith](https://img.shields.io/badge/LangSmith-%E2%9C%93-3b82f6?logo=data:image/svg+xml;base64,PHN2ZyB4bWxucz0iaHR0cDovL3d3dy53My5vcmcvMjAwMC9zdmciIHZpZXdCb3g9IjAgMCAyNCAyNCI+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xMiAyQTEwIDEwIDAgMCAwIDIgMTJhMTAgMTAgMCAwIDAgMTAgMTAgMTAgMTAgMCAwIDAtMTAtMTBtMCAxOGMtNC40MSAwLTgtMy41OS04LThzMy41OS04IDgtOCA4IDMuNTkgOCA4LTMuNTkgOC04IDh6Ii8+PHBhdGggZmlsbD0id2hpdGUiIGQ9Ik0xNSA5LjVhLjUuNSAwIDAgMC0uNS0uNUg5LjVhLjUuNSAwIDAgMC0uNS41djRoYS41LjUgMCAwIDAgLjUuNWg0LjVhLjUuNSAwIDAgMCAuNS0uNVY5LjV6Ii8+PC9zdmc+)](https://smith.langchain.com/)

### 🎯 项目介绍
> 🤖 基于 LangGraph + 大语言模型（LLM）的财务数据自动核对 Agent，支持跨表字段映射、差异识别、
> 人工审核与规则学习，让繁琐的对账工作自动化、智能化。

本工具可自动比对两份结构不同但业务相关的表格（例如：“进口箱量统计表” vs “结算船公司统计表”），
识别命名差异、数量偏差，并生成可解释的映射建议。用户确认后，系统会自动更新规则配置，实现持续优化。
---

### 🌊 LangGraph流程图
![LangGraph流程图](流程图.svg)

---

### 📝 Features说明
- ✅ **两个规则表**：一是聚合规则表，记录哪些字段和哪个字段是等价的；二是行列名称映射规则表，记录同一指代的不同名称
- ✅ **智能字段映射**：自动匹配不同命名下的相同业务项（如 `20尺合计` ↔ `20重箱SUB-TOTAL`）
- ✅ **人机协同审核**：模型在执行完当前流程后会提出补充规则库的建议，等待人工确认（比如输入 `add in`）
- ✅ **规则持久化**：用户确认的映射关系自动写入 `config/mapping_rules.yaml`
- ✅ **全链路追踪**：集成 [LangSmith](https://smith.langchain.com/)，每一步推理过程可审计、可复现，追踪节点流转、用时与消耗情况。
---
### 📂 项目结构
```
FinancialCheckAgent/
├── main.py                 # 主执行入口
├── requirements.txt        # Python 依赖列表
├── .env                    # 环境变量（⚠️ 请勿提交到 Git！）
├── .gitignore              # 忽略敏感文件
├── LICENSE                 # MIT 开源协议
├── config/
│   └── mapping_rules.yaml  # 映射规则与验证逻辑（会自动更新）
├── data/
│   ├── 测试-分摊表.png     # 示例输入文件
│   └── 测试-系统数据.jpg
├── nodes/                  # LangGraph 节点逻辑（预处理、审核等）
├── utils/                  # 工具模块（LLM 调用、图像解析等）
└── graph/                  # 状态图构建逻辑
🔧 自定义规则
编辑 config/mapping_rules.yaml 即可扩展映射关系：
```
---

### 🚀 快速开始

#### 1. 克隆项目
```bash
    git clone https://github.com/zhaozeru/FinancialCheckAgent.git
    cd FinancialCheckAgent
```
#### 2. 创建并激活虚拟环境

```bash
    # 创建虚拟环境（默认 .venv）
    uv venv
    # 激活虚拟环境
    .venv\Scripts\activate       # Windows
```
#### 3. 安装依赖
```bash
  uv pip install -e .
  # 或
  uv sync
```
#### 4. 配置 API 密钥
```
在项目根目录创建 .env 文件：
ZHIPUAI_API_KEY={填入钥匙}
# LANGCHAIN_API_KEY={填入钥匙}  # 用于 LangSmith 追踪
# LANGCHAIN_TRACING_V2=true
# LANGCHAIN_PROJECT=FinancialCheckAgent-Demo
🔑 获取智谱 API Key：https://open.bigmodel.cn/usercenter/apikeys
```
#### 5. 运行示例
```bash
    python main.py
````
```
程序将：
加载 data/ 目录中的测试图片（或表格）
执行自动预处理与核对流程
在“人工审核”节点暂停，提示你输入 y（接受建议）或 n（跳过）
输出最终结果，并更新映射规则（如适用）
```

---
📊 LangSmith 追踪（可选但推荐）
启用 LangSmith 后，所有运行记录将自动上传至 [LangSmith](https://smith.langchain.com/)，便于:
- 查看 LLM 输入/输出
- 分析决策路径
- 复现与调试问题
- 只需在 .env 中取消注释相关配置即可。

---

