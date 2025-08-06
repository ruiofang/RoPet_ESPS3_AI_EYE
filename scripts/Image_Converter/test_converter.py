#!/usr/bin/env python3
"""
简单测试脚本，用于验证H文件转PNG工具是否能正确处理upper_lower_common.h文件
"""

import os
import sys

# 添加当前目录到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

from h_to_png_converter import HToPNGConverterApp
import tkinter as tk

def test_parse_file():
    """测试解析upper_lower_common.h文件"""
    
    # 创建一个简化的应用实例来测试解析功能
    root = tk.Tk()
    root.withdraw()  # 隐藏主窗口
    
    app = HToPNGConverterApp(root)
    
    # 测试文件路径
    test_file = r"c:\Users\RUIO\Desktop\RoPet_ESPS3_AI_EYE\main\eye_data\160_160\upper_lower_common.h"
    
    if not os.path.exists(test_file):
        print(f"测试文件不存在: {test_file}")
        return False
    
    print(f"正在解析文件: {test_file}")
    
    try:
        # 解析文件
        arrays = app.parse_h_file_all_arrays(test_file)
        
        print(f"找到 {len(arrays)} 个数组:")
        for i, array_info in enumerate(arrays, 1):
            if len(array_info) == 3:
                array_name, values, data_type = array_info
                print(f"  {i}. {array_name} ({data_type}): {len(values)} 个值")
                
                # 显示前10个值作为示例
                if len(values) > 0:
                    sample = values[:10] if len(values) >= 10 else values
                    print(f"     前几个值: {sample}")
                    
                    # 检测尺寸
                    width, height, image_type = app.detect_image_type_and_size(array_name, len(values))
                    print(f"     检测尺寸: {width}×{height} ({image_type})")
            else:
                array_name, values = array_info
                print(f"  {i}. {array_name} (未知类型): {len(values)} 个值")
        
        return True
        
    except Exception as e:
        print(f"解析文件时出错: {e}")
        return False
    finally:
        root.destroy()

if __name__ == "__main__":
    print("H文件转PNG工具 - 测试脚本")
    print("=" * 50)
    
    success = test_parse_file()
    
    if success:
        print("\n测试完成: 解析成功！")
    else:
        print("\n测试失败: 请检查错误信息")
