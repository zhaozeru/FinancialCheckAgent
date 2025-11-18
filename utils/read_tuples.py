import ast

def load_tuples_from_txt(file_name):
    """从txt文件安全地读取元组数据"""
    try:
        file_path = f'C:\\Users\\13652\\Desktop\\财务智能体\\FinancialCheckAgent\\Test\\{file_name}.txt'

        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read().strip()
        data = ast.literal_eval(content)
        print(f"已从 {file_name}.txt 文件读取元组数据")
        return data
    except FileNotFoundError:
        print(f"文件 {file_name}.txt 不存在")
        return None
    except (SyntaxError, ValueError) as e:
        print(f"文件内容格式错误: {e}")
        return None
    except Exception as e:
        print(f"读取元组数据时出错: {e}")
        return None