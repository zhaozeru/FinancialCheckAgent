from schemas.state_schema import MaingraphState
import yaml
from datetime import datetime
from typing import Dict, Any

def add_mappings_node(state: MaingraphState) -> dict:
    """
    向映射规则YAML文件中添加新规则，确保不丢失任何已有内容。
    使用 yaml.dump 安全序列化整个结构。
    """
    try:
        mapping_file_path = r'/\tools\mapping_relations.yaml'

        # 加载现有的映射规则
        try:
            with open(mapping_file_path, 'r', encoding='utf-8') as f:
                mapping_rules = yaml.safe_load(f) or {}
        except FileNotFoundError:
            mapping_rules = {}

        # 确保必要的结构存在
        mapping_rules.setdefault('version', '1.0')

        row_eq = mapping_rules.get('row_equivalences')
        if not isinstance(row_eq, dict):
            mapping_rules['row_equivalences'] = {}
        else:
            mapping_rules['row_equivalences'] = row_eq

        col_eq = mapping_rules.get('column_equivalences')
        if not isinstance(col_eq, dict):
            mapping_rules['column_equivalences'] = {}
        else:
            mapping_rules['column_equivalences'] = col_eq

        if 'table_references' not in mapping_rules:
            mapping_rules['table_references'] = {
                'table1': {'name': '进口箱量统计表', 'description': '进口业务箱量统计'},
                'table2': {'name': '结算船公司统计表', 'description': '结算船公司业务统计'}
            }
        # 注意：这里不再覆盖 table_references，只初始化缺失时

        mapping_rules.setdefault('validation_rules', [])
        mapping_rules.setdefault('update_history', [])

        # 获取映射建议
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
            mapping_type = suggestion.get('type', 'row')
            confidence = suggestion.get('confidence', 'medium')
            reason = suggestion.get('reason', '')
            suggestion_text = suggestion.get('suggestion', '')

            # 验证
            if not table1_name or not table2_name or table1_name == '无对应项' or table2_name == '无对应项':
                print(f"⚠️ 跳过无效建议：表名为空或为'无对应项'")
                skipped_mappings.append({'reason': '无效表名', 'suggestion': suggestion})
                continue

            if table1_name == table2_name:
                print(f"⚠️ 跳过相同名称：{table1_name}")
                skipped_mappings.append({'reason': '表名相同', 'from': table2_name, 'to': table1_name})
                continue

            # 选择目标区域
            if mapping_type == 'row':
                target_section = mapping_rules['row_equivalences']
            elif mapping_type == 'column':
                target_section = mapping_rules['column_equivalences']
            else:
                print(f"⚠️ 未知映射类型：{mapping_type}，默认为行映射")
                target_section = mapping_rules['row_equivalences']

            # 双向重复检查
            if table2_name in target_section:
                existing = target_section[table2_name]
                print(f"⚠️ 映射已存在：{table2_name} -> {existing}")
                skipped_mappings.append({
                    'reason': '映射已存在',
                    'from': table2_name,
                    'to': table1_name,
                    'existing_mapping': f"{table2_name} -> {existing}"
                })
                continue

            for key, val in target_section.items():
                if val == table1_name:
                    print(f"⚠️ 反向映射已存在：{key} -> {table1_name}")
                    skipped_mappings.append({
                        'reason': '反向映射已存在',
                        'from': table2_name,
                        'to': table1_name,
                        'existing_mapping': f"{key} -> {table1_name}"
                    })
                    break
            else:  # only add if no reverse found
                # 添加新映射
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
                continue  # 已处理，跳过后续

            # 如果 break 触发（即存在反向），则跳过添加，继续下一条
            continue

        # 处理结果
        if added_mappings:
            update_record = {
                'timestamp': datetime.now().isoformat(),
                'action': 'auto_added_mappings',
                'added_count': len(added_mappings),
                'skipped_count': len(skipped_mappings),
                'added_mappings': added_mappings,
                'skipped_mappings': skipped_mappings  # 不再丢弃！
            }
            mapping_rules['update_history'].append(update_record)

            # 安全保存：使用 yaml.dump，保留所有字段和结构
            try:
                with open(mapping_file_path, 'w', encoding='utf-8') as f:
                    yaml.dump(
                        mapping_rules,
                        f,
                        allow_unicode=True,
                        indent=2,
                        default_flow_style=False,
                        sort_keys=False  # 保持 key 顺序（如 row/column 顺序）
                    )

                print(f"🎯 成功添加 {len(added_mappings)} 条映射规则到YAML文件")
                print(f"⏰ 跳过 {len(skipped_mappings)} 条无效或重复的映射")

                state['mapping_addition_status'] = f"success_added_{len(added_mappings)}"
                state['added_mappings'] = added_mappings
                state['skipped_mappings'] = skipped_mappings

            except Exception as save_error:
                print(f"❌ 保存YAML文件失败: {save_error}")
                state['mapping_addition_status'] = f"save_error: {str(save_error)}"

        else:
            print("⚠️ 未添加任何新的映射规则")
            state['mapping_addition_status'] = "no_new_mappings_added"
            state['skipped_mappings'] = skipped_mappings

    except Exception as e:
        print(f"❌ 添加映射规则到YAML文件失败: {e}")
        state['mapping_addition_status'] = f"error: {str(e)}"

    return state