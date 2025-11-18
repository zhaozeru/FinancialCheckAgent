from typing import (TypedDict,List,Dict,Any,)

class MaingraphState(TypedDict, total=False):
    # 图像路径
    image_path: List[str]

    # 预处理节点1：原始表格1的解析结果
    pic_tuples_1: Any          # 表格1的单元格数据
    row_names_1: List[str]     # 表格1的行标识
    col_names_1: List[str]     # 表格1的列标识

    # 预处理节点2：原始表格2的解析结果
    pic_tuples_2: Any          # 表格2的单元格数据
    row_names_2: List[str]     # 表格2的行标识
    col_names_2: List[str]     # 表格2的列标识

    # 归一化节点：标准化后的表格数据
    standardized_pic_tuples_1: Any
    standardized_pic_tuples_2: Any

    # 模型分析节点
    analysis_report: Any       # 自动比对生成的差异分析报告
    analysis_error: Any        # 分析过程中发生的错误

    # 映射建议生成节点
    mapping_suggestions_raw: Any      # 原始建议（未结构化）
    mapping_suggestions: List[Dict[str, Any]]  # 结构化映射建议列表
    needs_human_review: bool          # 是否需要人工复核
    review_type: str                  # 复核类型（如 "mapping", "data_correction"）
    suggestions_count: int            # 建议总数
    restock_error: str                # 映射建议生成时的错误信息

    # 人工复核节点
    mapping_addition_status: str      # 人工操作状态（如 "approved", "rejected", "pending"）

    # 映射执行节点
    added_mappings: List[Dict[str, Any]]    # 已成功添加的映射项
    skipped_mappings: List[Dict[str, Any]]  # 被跳过/忽略的映射项

    # 全局错误字段
    error: str                   # 流程中任意步骤的顶层错误信息