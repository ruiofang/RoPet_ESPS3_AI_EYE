import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image
import re
import os
import sys

class HToPNGConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RoPet眼部图像H文件转PNG工具 - 批量转换模式")
        self.root.geometry("900x700")
        
        # 初始化变量
        self.output_dir = tk.StringVar(value=os.path.abspath("png_output"))
        self.input_dir = tk.StringVar()
        self.color_format = tk.StringVar(value="RGB565")
        self.auto_detect_size = tk.BooleanVar(value=True)
        
        # 文件路径列表（保留以兼容旧代码）
        self.file_paths = []
        
        # 尺寸定义
        self.size_definitions = {
            'IRIS_MAP_WIDTH': 314,
            'IRIS_MAP_HEIGHT': 50,
            'SCLERA_WIDTH': 250,
            'SCLERA_HEIGHT': 250,
            'SCREEN_WIDTH': 160,
            'SCREEN_HEIGHT': 160,
            'IRIS_WIDTH': 100,
            'IRIS_HEIGHT': 100
        }
        
        # 创建UI组件
        self.create_widgets()
        self.redirect_output()
        self.load_common_definitions()
        
        # 显示欢迎信息
        print("RoPet眼部图像H文件转PNG工具 - 批量转换模式")
        print("=" * 60)
        print("使用说明:")
        print("1. 选择包含H文件的输入目录")
        print("2. 设置输出目录") 
        print("3. 点击'批量转换'开始处理")
        print("4. 图片将按头文件名称分文件夹保存，每个数组生成一张PNG")
        print("=" * 60)
        print()

    def load_common_definitions(self):
        """从用户目录下的common.h文件加载尺寸定义，如果找不到则使用默认值"""
        # 优先搜索用户工作目录和项目目录下的common.h文件
        possible_paths = []
        
        # 1. 首先搜索当前工作目录及其子目录
        current_dir = os.getcwd()
        if os.path.exists(current_dir):
            for root, dirs, files in os.walk(current_dir):
                for file in files:
                    if file == "common.h":
                        possible_paths.append(os.path.join(root, file))
        
        # 2. 搜索项目根目录下的main/eye_data目录
        base_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../main/eye_data")
        if os.path.exists(base_dir):
            # 添加常见路径
            common_paths = [
                os.path.join(base_dir, "240_240/common.h"),
                os.path.join(base_dir, "160_160/common.h"),
                os.path.join(base_dir, "common.h"),
            ]
            for path in common_paths:
                if path not in possible_paths:
                    possible_paths.append(path)
            
            # 搜索所有子目录中的common.h
            for root, dirs, files in os.walk(base_dir):
                for file in files:
                    if file == "common.h":
                        potential_path = os.path.join(root, file)
                        if potential_path not in possible_paths:
                            possible_paths.append(potential_path)
        
        # 3. 搜索用户主目录下的常见位置（如果有输入目录设置的话）
        if hasattr(self, 'input_dir') and self.input_dir.get():
            input_directory = self.input_dir.get()
            if os.path.exists(input_directory):
                for root, dirs, files in os.walk(input_directory):
                    for file in files:
                        if file == "common.h":
                            potential_path = os.path.join(root, file)
                            if potential_path not in possible_paths:
                                possible_paths.append(potential_path)
        
        # 初始化标记
        self.common_h_loaded = False
        loaded_definitions = {}
        
        for common_h_path in possible_paths:
            if os.path.exists(common_h_path):
                try:
                    with open(common_h_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 解析#define语句
                    define_pattern = r'#define\s+(\w+)\s+(\d+)'
                    matches = re.findall(define_pattern, content)
                    
                    temp_definitions = {}
                    for define_name, value in matches:
                        if define_name in self.size_definitions:
                            temp_definitions[define_name] = int(value)
                    
                    # 如果找到了有效的定义，使用这个文件
                    if temp_definitions:
                        # 更新size_definitions
                        for name, value in temp_definitions.items():
                            self.size_definitions[name] = value
                        
                        loaded_definitions = temp_definitions
                        self.common_h_loaded = True
                        self.loaded_common_h_path = common_h_path
                        
                        print(f"✓ 从用户目录找到common.h定义: {os.path.relpath(common_h_path)}")
                        for name, value in loaded_definitions.items():
                            print(f"  {name}: {value}")
                        print("将优先使用common.h中的尺寸定义，未找到的定义将使用默认值")
                        print()
                        return  # 找到有效定义后立即返回
                        
                except Exception as e:
                    print(f"尝试加载 {os.path.relpath(common_h_path)} 失败: {e}")
                    continue
        
        # 如果没有找到任何有效的common.h文件，使用默认值
        print("未在用户目录中找到有效的common.h文件，使用默认尺寸定义")
        print("搜索的路径包括:")
        print("  1. 当前工作目录及其子目录")
        print("  2. 项目main/eye_data目录及其子目录")  
        print("  3. 输入目录及其子目录（如果已设置）")
        print(f"默认尺寸定义:")
        for name, value in self.size_definitions.items():
            print(f"  {name}: {value}")
        print()

    def create_widgets(self):
        # 参数设置框架
        settings_frame = ttk.LabelFrame(self.root, text="转换设置")
        settings_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # 自动检测尺寸选项
        ttk.Checkbutton(settings_frame, text="自动检测图像尺寸", 
                       variable=self.auto_detect_size).grid(row=0, column=0, padx=5, pady=5)

        # 颜色格式
        ttk.Label(settings_frame, text="颜色格式:").grid(row=0, column=1, padx=5, pady=5)
        ttk.Combobox(settings_frame, textvariable=self.color_format,
                    values=["RGB565", "RGB888", "ARGB8888"], width=12).grid(row=0, column=2, padx=5, pady=5)

        # 尺寸信息显示
        size_info_frame = ttk.LabelFrame(self.root, text="当前尺寸定义")
        size_info_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        self.size_info_text = tk.Text(size_info_frame, height=4, width=80)
        self.size_info_text.pack(padx=5, pady=5)
        self.update_size_info()

        # 输入目录框架
        input_frame = ttk.LabelFrame(self.root, text="输入目录")
        input_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        
        self.input_dir = tk.StringVar()
        ttk.Entry(input_frame, textvariable=self.input_dir, width=60).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(input_frame, text="选择目录", command=self.select_input_directory).pack(side=tk.RIGHT, padx=5, pady=5)

        # 输出目录
        output_frame = ttk.LabelFrame(self.root, text="输出目录")
        output_frame.grid(row=3, column=0, padx=10, pady=5, sticky="ew")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=60).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(output_frame, text="浏览", command=self.select_output_dir).pack(side=tk.RIGHT, padx=5, pady=5)

        # 转换按钮
        convert_frame = ttk.Frame(self.root)
        convert_frame.grid(row=4, column=0, padx=10, pady=10)
        ttk.Button(convert_frame, text="批量转换", command=self.start_conversion, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(convert_frame, text="刷新尺寸定义", command=self.refresh_definitions).pack(side=tk.LEFT, padx=5)
        ttk.Button(convert_frame, text="选择common.h", command=self.select_common_h).pack(side=tk.LEFT, padx=5)
        ttk.Button(convert_frame, text="帮助", command=self.show_help).pack(side=tk.RIGHT, padx=5)

        # 日志区域
        log_frame = ttk.LabelFrame(self.root, text="转换日志")
        log_frame.grid(row=5, column=0, padx=10, pady=5, sticky="nsew")
        
        log_btn_frame = ttk.Frame(log_frame)
        log_btn_frame.pack(fill=tk.X, side=tk.BOTTOM)
        ttk.Button(log_btn_frame, text="清空日志", command=self.clear_log).pack(side=tk.RIGHT, padx=5, pady=2)
        
        self.log_text = tk.Text(log_frame, height=12)
        self.log_text.pack(fill=tk.BOTH, expand=True)

        # 布局配置
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(5, weight=1)

    def update_size_info(self):
        """更新尺寸信息显示"""
        self.size_info_text.delete(1.0, tk.END)
        
        # 显示尺寸来源
        source_info = "尺寸来源: "
        if hasattr(self, 'common_h_loaded') and self.common_h_loaded:
            if hasattr(self, 'loaded_common_h_path'):
                relative_path = os.path.relpath(self.loaded_common_h_path, os.path.dirname(os.path.abspath(__file__)))
                source_info += f"common.h文件 ({relative_path})\n"
            else:
                source_info += "common.h文件定义\n"
        else:
            source_info += "默认定义\n"
        
        info_text = source_info
        info_text += f"虹膜贴图: {self.size_definitions['IRIS_MAP_WIDTH']}×{self.size_definitions['IRIS_MAP_HEIGHT']}  "
        info_text += f"巩膜: {self.size_definitions['SCLERA_WIDTH']}×{self.size_definitions['SCLERA_HEIGHT']}  "
        info_text += f"屏幕: {self.size_definitions['SCREEN_WIDTH']}×{self.size_definitions['SCREEN_HEIGHT']}\n"
        info_text += f"虹膜: {self.size_definitions['IRIS_WIDTH']}×{self.size_definitions['IRIS_HEIGHT']}"
        self.size_info_text.insert(1.0, info_text)

    def select_common_h(self):
        """手动选择common.h文件"""
        file_path = filedialog.askopenfilename(
            title="选择common.h文件",
            filetypes=[("头文件", "*.h"), ("所有文件", "*.*")],
            initialdir=os.path.join(os.path.dirname(os.path.abspath(__file__)), "../../main/eye_data")
        )
        
        if file_path:
            self.load_specific_common_h(file_path)
            self.update_size_info()

    def load_specific_common_h(self, file_path):
        """加载指定的common.h文件"""
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # 解析#define语句
            define_pattern = r'#define\s+(\w+)\s+(\d+)'
            matches = re.findall(define_pattern, content)
            
            loaded_definitions = {}
            for define_name, value in matches:
                if define_name in self.size_definitions:
                    self.size_definitions[define_name] = int(value)
                    loaded_definitions[define_name] = int(value)
            
            if loaded_definitions:
                self.common_h_loaded = True
                self.loaded_common_h_path = file_path
                
                print(f"手动加载 {file_path} 中的尺寸定义:")
                for name, value in loaded_definitions.items():
                    print(f"  {name}: {value}")
                print("common.h定义加载成功")
                print()
            else:
                print(f"警告: {file_path} 中未找到有效的尺寸定义")
                messagebox.showwarning("警告", "选择的文件中未找到有效的尺寸定义")
                
        except Exception as e:
            print(f"加载 {file_path} 失败: {e}")
            messagebox.showerror("错误", f"加载文件失败: {str(e)}")

    def refresh_definitions(self):
        """刷新尺寸定义"""
        self.load_common_definitions()
        self.update_size_info()

    def detect_image_type_and_size(self, array_name, data_length):
        """根据数组名称和数据长度检测图像类型和尺寸"""
        array_name_lower = array_name.lower()
        
        # 检查是否加载了common.h的定义
        common_h_loaded = hasattr(self, 'common_h_loaded') and self.common_h_loaded
        
        # 定义可能的尺寸和对应的关键词
        size_mappings = [
            # 虹膜贴图
            (self.size_definitions['IRIS_MAP_WIDTH'] * self.size_definitions['IRIS_MAP_HEIGHT'], 
             self.size_definitions['IRIS_MAP_WIDTH'], self.size_definitions['IRIS_MAP_HEIGHT'], 
             "虹膜贴图", ['iris_map', 'irismap']),
             
            # 巩膜
            (self.size_definitions['SCLERA_WIDTH'] * self.size_definitions['SCLERA_HEIGHT'], 
             self.size_definitions['SCLERA_WIDTH'], self.size_definitions['SCLERA_HEIGHT'], 
             "巩膜", ['sclera']),
             
            # 屏幕/完整眼部图像
            (self.size_definitions['SCREEN_WIDTH'] * self.size_definitions['SCREEN_HEIGHT'], 
             self.size_definitions['SCREEN_WIDTH'], self.size_definitions['SCREEN_HEIGHT'], 
             "屏幕/完整眼部", ['screen', 'eye', 'full']),
             
            # 虹膜
            (self.size_definitions['IRIS_WIDTH'] * self.size_definitions['IRIS_HEIGHT'], 
             self.size_definitions['IRIS_WIDTH'], self.size_definitions['IRIS_HEIGHT'], 
             "虹膜", ['iris'])
        ]
        
        # 如果加载了common.h定义，优先使用精确匹配
        if common_h_loaded:
            # 首先根据数据长度匹配
            exact_matches = []
            for expected_length, width, height, type_name, keywords in size_mappings:
                if data_length == expected_length:
                    exact_matches.append((width, height, type_name))
            
            if len(exact_matches) == 1:
                return exact_matches[0]
            elif len(exact_matches) > 1:
                # 如果有多个匹配，根据名称关键词进一步筛选
                for width, height, type_name in exact_matches:
                    # 找到对应的关键词
                    for _, w, h, tn, keywords in size_mappings:
                        if w == width and h == height and tn == type_name:
                            if any(keyword in array_name_lower for keyword in keywords):
                                return width, height, type_name
                            break
                # 如果没有关键词匹配，返回第一个
                return exact_matches[0]
        
        # 如果没有common.h定义或没有精确匹配，尝试推算
        sqrt_length = int(data_length ** 0.5)
        if sqrt_length * sqrt_length == data_length:
            return sqrt_length, sqrt_length, "推算正方形"
        
        # 尝试常见的宽高比
        common_ratios = [(16, 9), (4, 3), (3, 2), (1, 1)]
        for w_ratio, h_ratio in common_ratios:
            for scale in range(1, 200):
                w = w_ratio * scale
                h = h_ratio * scale
                if w * h == data_length:
                    return w, h, f"推算矩形({w_ratio}:{h_ratio})"
        
        # 如果都不匹配，返回默认值
        if common_h_loaded:
            return self.size_definitions['SCREEN_WIDTH'], self.size_definitions['SCREEN_HEIGHT'], "common.h默认尺寸"
        else:
            # 使用固定的默认尺寸
            return 160, 160, "固定默认尺寸"

    def show_help(self):
        help_text = """RoPet眼部图像H文件转PNG工具

批量转换模式：
• 选择包含H文件的输入目录
• 工具会自动遍历所有子目录中的H文件
• 输出图片按头文件名称建立文件夹分类
• 每个头文件的所有数组都会转换为PNG图片，按数组名称命名

智能尺寸检测：
• 工具会自动搜索用户目录下的common.h文件获取尺寸定义
• common.h搜索顺序：
  1. 当前工作目录及其所有子目录
  2. 项目main/eye_data目录及其子目录
  3. 用户选择的输入目录及其子目录
• 如果找到valid common.h文件，优先使用其中的尺寸定义
• 如果找不到或无有效定义，使用以下默认尺寸：
  - 虹膜贴图：314×50（15700像素）
  - 巩膜：250×250（62500像素）  
  - 屏幕/完整眼部：160×160（25600像素）
  - 虹膜：100×100（10000像素）

支持的数组格式：
• const uint16_t array_name[] = { 0x1234, 0x5678, ... }; (RGB565彩色数据)
• uint16_t array_name[] = { 0x1234, 0x5678, ... }; (RGB565彩色数据)
• static const uint16_t array_name[] = { 0x1234, 0x5678, ... }; (RGB565彩色数据)
• const uint8_t array_name[] = { 0x00, 0x01, 255, ... }; (8位灰度数据)
• uint8_t array_name[] = { 0x00, 0x01, 255, ... }; (8位灰度数据)
• static const uint8_t array_name[] = { 0x00, 0x01, 255, ... }; (8位灰度数据)
• 自动识别数组名称作为PNG文件名，数据类型决定输出格式

使用方法：
1. 选择包含H文件的输入目录
2. 设置输出目录
3. 启用"自动检测图像尺寸"（推荐）
4. 选择颜色格式（通常RGB565）
5. 点击"批量转换"

输出结构：
输出目录/
├── 头文件名1/
│   ├── 数组名1.png
│   ├── 数组名2.png
│   └── ...
├── 头文件名2/
│   ├── 数组名1.png
│   └── ...
└── ...

文件类型识别优先级：
└── ...

文件类型识别优先级：
1. 如果加载了common.h定义，优先根据数据长度精确匹配
2. 根据数组名称关键词识别：
   • 包含"iris_map"的数组 → 虹膜贴图尺寸
   • 包含"sclera"的数组 → 巩膜尺寸
   • 包含"iris"的数组 → 虹膜尺寸
3. 如果无法匹配，尝试推算为正方形或常见比例的矩形
4. 最后使用默认尺寸（common.h定义或固定默认值）

特性说明：
• 支持从用户目录自动搜索common.h文件获取尺寸定义
• 图片按头文件名分文件夹存储，便于管理
• 图片按数组名命名，便于识别
• 智能尺寸检测，减少手工配置需求
"""
        messagebox.showinfo("帮助", help_text)

    def clear_log(self):
        self.log_text.delete(1.0, tk.END)

    def redirect_output(self):
        class StdoutRedirector:
            def __init__(self, text_widget):
                self.text_widget = text_widget

            def write(self, message):
                self.text_widget.insert(tk.END, message)
                self.text_widget.see(tk.END)
                self.text_widget.update()

            def flush(self):
                pass

        sys.stdout = StdoutRedirector(self.log_text)

    def select_input_directory(self):
        """选择输入目录"""
        directory = filedialog.askdirectory(title="选择包含H文件的目录")
        if directory:
            self.input_dir.set(directory)
            # 统计H文件数量
            h_files = []
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.h'):
                        h_files.append(os.path.join(root, file))
            print(f"在目录 {directory} 中找到 {len(h_files)} 个H文件")

    def select_files(self):
        files = filedialog.askopenfilenames(
            title="选择H文件",
            filetypes=[("头文件", "*.h"), ("所有文件", "*.*")]
        )
        for file_path in files:
            if file_path not in self.file_paths:
                self.file_paths.append(file_path)
                self.file_listbox.insert(tk.END, os.path.basename(file_path))

    def select_directory(self):
        directory = filedialog.askdirectory(title="选择包含H文件的目录")
        if directory:
            for root, dirs, files in os.walk(directory):
                for file in files:
                    if file.endswith('.h'):
                        file_path = os.path.join(root, file)
                        if file_path not in self.file_paths:
                            self.file_paths.append(file_path)
                            self.file_listbox.insert(tk.END, os.path.relpath(file_path, directory))

    def clear_files(self):
        self.file_paths.clear()
        self.file_listbox.delete(0, tk.END)

    def select_output_dir(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def start_conversion(self):
        """开始批量转换"""
        input_directory = self.input_dir.get()
        if not input_directory or not os.path.exists(input_directory):
            messagebox.showwarning("警告", "请先选择有效的输入目录")
            return

        output_directory = self.output_dir.get()
        if not output_directory:
            messagebox.showwarning("警告", "请设置输出目录")
            return

        os.makedirs(output_directory, exist_ok=True)
        
        # 在转换前重新加载common.h定义，以便包含新设置的输入目录
        print("重新搜索common.h文件...")
        self.load_common_definitions()
        
        # 收集所有H文件
        h_files = []
        for root, dirs, files in os.walk(input_directory):
            for file in files:
                if file.endswith('.h'):
                    h_files.append(os.path.join(root, file))
        
        if not h_files:
            messagebox.showwarning("警告", "在输入目录中未找到H文件")
            return
        
        print(f"开始批量转换，共找到 {len(h_files)} 个H文件")
        print(f"输入目录: {input_directory}")
        print(f"输出目录: {output_directory}")
        print("=" * 60)
        
        self.convert_all_files(h_files, output_directory)

    def parse_h_file_all_arrays(self, file_path):
        """解析H文件，提取所有数组数据"""
        with open(file_path, 'r', encoding='utf-8') as f:
            content = f.read()

        # 查找所有数组定义，包括uint16_t和uint8_t类型
        patterns = [
            # uint16_t 数组模式
            (r'const\s+uint16_t\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint16_t'),
            (r'uint16_t\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint16_t'),
            (r'static\s+const\s+uint16_t\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint16_t'),
            (r'const\s+unsigned\s+short\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint16_t'),
            
            # uint8_t 数组模式
            (r'const\s+uint8_t\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint8_t'),
            (r'uint8_t\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint8_t'),
            (r'static\s+const\s+uint8_t\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint8_t'),
            (r'const\s+unsigned\s+char\s+(\w+)\s*\[.*?\]\s*=\s*\{([^}]+)\}', 'uint8_t')
        ]
        
        arrays = []
        for pattern, data_type in patterns:
            matches = re.finditer(pattern, content, re.DOTALL)
            for match in matches:
                array_name = match.group(1)
                array_content = match.group(2)

                # 提取数值 - 支持十六进制和十进制
                hex_values = re.findall(r'0x[0-9A-Fa-f]+', array_content)
                dec_values = re.findall(r'\b(?!0x)\d+\b', array_content)
                
                values = []
                if hex_values:
                    # 优先处理十六进制值
                    values = [int(val, 16) for val in hex_values]
                elif dec_values:
                    # 处理十进制值
                    values = [int(val, 10) for val in dec_values]
                
                if values:
                    arrays.append((array_name, values, data_type))
        
        return arrays

    def rgb565_to_rgb888(self, rgb565):
        """将RGB565转换为RGB888"""
        r = (rgb565 >> 11) & 0x1F
        g = (rgb565 >> 5) & 0x3F
        b = rgb565 & 0x1F
        
        # 扩展到8位
        r = (r << 3) | (r >> 2)
        g = (g << 2) | (g >> 4)
        b = (b << 3) | (b >> 2)
        
        return r, g, b

    def convert_all_files(self, h_files, output_directory):
        """批量转换所有H文件"""
        total_files = len(h_files)
        success_files = 0
        total_arrays = 0
        success_arrays = 0
        
        for i, file_path in enumerate(h_files, 1):
            try:
                # 获取文件名（不包含扩展名）作为文件夹名
                filename = os.path.splitext(os.path.basename(file_path))[0]
                file_output_dir = os.path.join(output_directory, filename)
                os.makedirs(file_output_dir, exist_ok=True)
                
                print(f"[{i}/{total_files}] 正在处理: {os.path.basename(file_path)}")
                
                # 解析文件中的所有数组
                arrays = self.parse_h_file_all_arrays(file_path)
                
                if not arrays:
                    print(f"  警告: 未找到有效的数组定义")
                    continue
                
                print(f"  找到 {len(arrays)} 个数组")
                file_success_count = 0
                
                # 转换每个数组
                for array_info in arrays:
                    # 解包数组信息（兼容新旧格式）
                    if len(array_info) == 3:
                        array_name, values, data_type = array_info
                    else:
                        # 兼容旧格式（假设是uint16_t）
                        array_name, values = array_info
                        data_type = 'uint16_t'
                    
                    try:
                        total_arrays += 1
                        print(f"    转换数组: {array_name} ({data_type}, {len(values)} 个数值)")
                        
                        # 检测图像尺寸
                        if self.auto_detect_size.get():
                            width, height, image_type = self.detect_image_type_and_size(array_name, len(values))
                            print(f"      检测类型: {image_type}")
                            print(f"      检测尺寸: {width}×{height}")
                        else:
                            width = self.size_definitions['SCREEN_WIDTH']
                            height = self.size_definitions['SCREEN_HEIGHT']
                            image_type = "手动设置"
                        
                        # 检查数据长度
                        expected_size = width * height
                        if len(values) != expected_size:
                            print(f"      警告: 数据长度 ({len(values)}) 与图像尺寸不匹配 ({expected_size})")
                            # 如果数据太多，截取；如果太少，用0填充
                            if len(values) > expected_size:
                                values = values[:expected_size]
                            else:
                                values.extend([0] * (expected_size - len(values)))
                        
                        # 创建图像
                        img = self.create_image_from_data(values, width, height, data_type)
                        
                        # 保存图像
                        output_filename = f"{array_name}.png"
                        output_path = os.path.join(file_output_dir, output_filename)
                        img.save(output_path)
                        
                        print(f"      保存成功: {output_filename}")
                        file_success_count += 1
                        success_arrays += 1
                        
                    except Exception as e:
                        print(f"      转换失败: {str(e)}")
                
                if file_success_count > 0:
                    success_files += 1
                    print(f"  文件处理完成: 成功转换 {file_success_count}/{len(arrays)} 个数组")
                else:
                    print(f"  文件处理失败: 未能转换任何数组")
                    # 如果没有成功转换任何数组，删除空文件夹
                    try:
                        os.rmdir(file_output_dir)
                    except:
                        pass
                
                print("-" * 50)
                
            except Exception as e:
                print(f"  文件处理出错: {str(e)}")
                print("-" * 50)

        # 显示最终结果
        print("=" * 60)
        print(f"批量转换完成!")
        print(f"处理文件: {success_files}/{total_files}")
        print(f"转换数组: {success_arrays}/{total_arrays}")
        print(f"输出目录: {output_directory}")
        
        messagebox.showinfo("完成", 
            f"批量转换完成!\n\n"
            f"处理文件: {success_files}/{total_files}\n"
            f"转换数组: {success_arrays}/{total_arrays}\n"
            f"输出目录: {output_directory}")

    def create_image_from_data(self, values, width, height, data_type='uint16_t'):
        """根据数据创建图像"""
        color_format = self.color_format.get()
        
        # 对于uint8_t数组，通常是灰度图像数据
        if data_type == 'uint8_t':
            # 创建灰度图像
            img_array = np.array(values, dtype=np.uint8).reshape(height, width)
            img = Image.fromarray(img_array, 'L')
            
        elif data_type == 'uint16_t':
            # 对于uint16_t数组，按照现有逻辑处理
            if color_format == "RGB565":
                # 转换RGB565到RGB888
                rgb_data = []
                for val in values:
                    r, g, b = self.rgb565_to_rgb888(val)
                    rgb_data.extend([r, g, b])
                
                # 创建图像
                img_array = np.array(rgb_data, dtype=np.uint8).reshape(height, width, 3)
                img = Image.fromarray(img_array, 'RGB')
                
            elif color_format == "RGB888":
                # 假设每个值包含RGB888数据
                rgb_data = []
                for val in values:
                    r = (val >> 16) & 0xFF
                    g = (val >> 8) & 0xFF
                    b = val & 0xFF
                    rgb_data.extend([r, g, b])
                
                img_array = np.array(rgb_data, dtype=np.uint8).reshape(height, width, 3)
                img = Image.fromarray(img_array, 'RGB')
                
            elif color_format == "ARGB8888":
                # 假设每个值包含ARGB8888数据
                rgba_data = []
                for val in values:
                    a = (val >> 24) & 0xFF
                    r = (val >> 16) & 0xFF
                    g = (val >> 8) & 0xFF
                    b = val & 0xFF
                    rgba_data.extend([r, g, b, a])
                
                img_array = np.array(rgba_data, dtype=np.uint8).reshape(height, width, 4)
                img = Image.fromarray(img_array, 'RGBA')
        
        return img

def main():
    root = tk.Tk()
    app = HToPNGConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()