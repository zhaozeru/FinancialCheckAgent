def save_tuples_to_txt(pic_tuples, file_name):
    """将元组数据保存到txt文件"""
    try:
        file_path = f'C:\\Users\\13652\\Desktop\\财务智能体\\FinancialCheckAgent\\Test\\{file_name}.txt'

        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(str(pic_tuples))

        print(f"元组数据已保存到 {file_name}.txt")
        return True

    except Exception as e:
        print(f"保存元组数据时出错: {e}")
        return False