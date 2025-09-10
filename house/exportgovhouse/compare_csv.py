#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
CSV文件比较脚本
自动读取data目录下的宝安房子数据CSV文件，比较找出不同的条目并导出到新文件
"""

import pandas as pd
import os
from datetime import datetime

def compare_csv_files():
    """
    比较两个CSV文件并导出不同的条目
    """
    # 文件路径
    data_dir = "data"
    
    # 自动查找data目录下的CSV文件
    csv_files = []
    if os.path.exists(data_dir):
        for file in os.listdir(data_dir):
            if file.endswith('.csv'):
                csv_files.append(os.path.join(data_dir, file))
    
    # 检查是否找到足够的CSV文件
    if len(csv_files) < 2:
        print(f"错误：在 {data_dir} 目录下找到的CSV文件数量不足（需要至少2个，找到{len(csv_files)}个）")
        print(f"找到的文件：{csv_files}")
        return
    
    # 按文件名排序，确保比较顺序一致
    csv_files.sort()
    file1, file2 = csv_files[0], csv_files[1]
    
    print(f"将比较以下文件：")
    print(f"文件1: {file1}")
    print(f"文件2: {file2}")
    
    print("正在读取CSV文件...")
    
    try:
        # 读取CSV文件
        df1 = pd.read_csv(file1, encoding='utf-8')
        df2 = pd.read_csv(file2, encoding='utf-8')
        
        print(f"文件1 ({file1}) 包含 {len(df1)} 条记录")
        print(f"文件2 ({file2}) 包含 {len(df2)} 条记录")
        
        # 使用房源编码作为唯一标识符进行比较
        # 因为房源编码应该是唯一的
        df1_set = set(df1['房源编码'].astype(str))
        df2_set = set(df2['房源编码'].astype(str))
        
        # 找出只在文件1中存在的记录
        only_in_file1 = df1[df1['房源编码'].astype(str).isin(df1_set - df2_set)]
        
        # 找出只在文件2中存在的记录
        only_in_file2 = df2[df2['房源编码'].astype(str).isin(df2_set - df1_set)]
        
        # 找出两个文件都存在的记录，但其他字段可能不同
        common_codes = df1_set & df2_set
        different_records = []
        
        for code in common_codes:
            record1 = df1[df1['房源编码'].astype(str) == code].iloc[0]
            record2 = df2[df2['房源编码'].astype(str) == code].iloc[0]
            
            # 比较除了房源编码之外的所有字段
            if not record1.equals(record2):
                # 记录有差异，将两个版本都加入
                different_records.append({
                    '差异类型': '内容变更',
                    '房源编码': code,
                    '文件1记录': record1.to_dict(),
                    '文件2记录': record2.to_dict()
                })
        
        # 生成输出文件名（带时间戳）
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        
        # 导出只在文件1中的记录
        if not only_in_file1.empty:
            output_file1 = f"data/只在8月18日文件中的记录_{timestamp}.csv"
            only_in_file1.to_csv(output_file1, index=False, encoding='utf-8-sig')
            print(f"只在8月18日文件中的记录已导出到: {output_file1} ({len(only_in_file1)} 条)")
        
        # 导出只在文件2中的记录
        if not only_in_file2.empty:
            output_file2 = f"data/只在9月7日文件中的记录_{timestamp}.csv"
            only_in_file2.to_csv(output_file2, index=False, encoding='utf-8-sig')
            print(f"只在9月7日文件中的记录已导出到: {output_file2} ({len(only_in_file2)} 条)")
        
        # 导出所有差异记录到一个文件
        all_differences = []
        
        # 添加只在文件1中的记录
        if not only_in_file1.empty:
            only_in_file1_copy = only_in_file1.copy()
            only_in_file1_copy['差异类型'] = '只在8月18日文件中'
            all_differences.append(only_in_file1_copy)
        
        # 添加只在文件2中的记录
        if not only_in_file2.empty:
            only_in_file2_copy = only_in_file2.copy()
            only_in_file2_copy['差异类型'] = '只在9月7日文件中'
            all_differences.append(only_in_file2_copy)
        
        # 合并所有差异记录
        if all_differences:
            combined_differences = pd.concat(all_differences, ignore_index=True)
            output_file_combined = f"data/所有差异记录_{timestamp}.csv"
            combined_differences.to_csv(output_file_combined, index=False, encoding='utf-8-sig')
            print(f"所有差异记录已导出到: {output_file_combined} ({len(combined_differences)} 条)")
        
        # 打印统计信息
        print("\n=== 比较结果统计 ===")
        print(f"只在8月18日文件中的记录: {len(only_in_file1)} 条")
        print(f"只在9月7日文件中的记录: {len(only_in_file2)} 条")
        print(f"两个文件都存在的记录: {len(common_codes)} 条")
        print(f"内容有差异的记录: {len(different_records)} 条")
        
        # 如果有内容差异的记录，也导出到单独文件
        if different_records:
            print(f"\n注意：发现 {len(different_records)} 条记录在两个文件中都存在但内容不同")
            print("这些记录需要手动检查，因为可能涉及价格、委托期限等字段的更新")
            
            # 创建内容差异的详细报告
            diff_report = []
            for diff in different_records:
                diff_report.append({
                    '房源编码': diff['房源编码'],
                    '差异类型': '内容变更',
                    '项目名称': diff['文件1记录']['项目名称'],
                    '8月18日价格': diff['文件1记录']['意向售价(万元)'],
                    '9月7日价格': diff['文件2记录']['意向售价(万元)'],
                    '8月18日委托期限': diff['文件1记录']['委托期限'],
                    '9月7日委托期限': diff['文件2记录']['委托期限']
                })
            
            diff_df = pd.DataFrame(diff_report)
            diff_output_file = f"data/内容变更记录_{timestamp}.csv"
            diff_df.to_csv(diff_output_file, index=False, encoding='utf-8-sig')
            print(f"内容变更记录已导出到: {diff_output_file}")
        
    except Exception as e:
        print(f"处理文件时发生错误: {str(e)}")
        import traceback
        traceback.print_exc()

if __name__ == "__main__":
    print("开始比较房子数据CSV文件...")
    compare_csv_files()
    print("比较完成！")
