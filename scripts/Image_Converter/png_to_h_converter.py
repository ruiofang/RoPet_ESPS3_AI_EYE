import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import numpy as np
from PIL import Image
import os
import sys
import re

class PNGToHConverterApp:
    def __init__(self, root):
        self.root = root
        self.root.title("RoPet PNG图片转H文件工具 - 逆向转换模式")
        self.root.geometry("900x700")
        
        # 初始化变量
        self.input_dir = tk.StringVar()
        self.output_dir = tk.StringVar(value=os.path.abspath("h_output"))
        self.color_format = tk.StringVar(value="RGB565")
        self.array_prefix = tk.StringVar(value="")
        self.generate_single_file = tk.BooleanVar(value=False)
        self.screen_config = tk.StringVar(value="auto")  # 添加屏幕配置选项
        
        # 创建UI组件
        self.create_widgets()
        self.redirect_output()
        
        # 显示欢迎信息
        print("RoPet PNG图片转H文件工具 - 逆向转换模式")
        print("=" * 60)
        print("使用说明:")
        print("1. 选择包含PNG图片的输入目录")
        print("2. 设置输出目录") 
        print("3. 选择颜色格式和命名选项")
        print("4. 点击'批量转换'开始处理")
        print("5. 每个图片将转换为对应的C数组定义")
        print("6. 尺寸参数将自动写入common.h文件")
        print("=" * 60)
        print()

    def create_widgets(self):
        # 参数设置框架
        settings_frame = ttk.LabelFrame(self.root, text="转换设置")
        settings_frame.grid(row=0, column=0, padx=10, pady=5, sticky="ew")

        # 颜色格式
        ttk.Label(settings_frame, text="颜色格式:").grid(row=0, column=0, padx=5, pady=5)
        ttk.Combobox(settings_frame, textvariable=self.color_format,
                    values=["RGB565", "RGB888", "ARGB8888"], width=12).grid(row=0, column=1, padx=5, pady=5)

        # 数组名前缀
        ttk.Label(settings_frame, text="数组名前缀:").grid(row=0, column=2, padx=5, pady=5)
        ttk.Entry(settings_frame, textvariable=self.array_prefix, width=15).grid(row=0, column=3, padx=5, pady=5)

        # 生成选项
        ttk.Checkbutton(settings_frame, text="合并到单个H文件", 
                       variable=self.generate_single_file).grid(row=1, column=0, columnspan=2, padx=5, pady=5, sticky="w")

        # 屏幕配置选项
        ttk.Label(settings_frame, text="屏幕配置:").grid(row=1, column=2, padx=5, pady=5)
        ttk.Combobox(settings_frame, textvariable=self.screen_config,
                    values=["auto", "160x160", "240x240"], width=12).grid(row=1, column=3, padx=5, pady=5)

        # 输入目录框架
        input_frame = ttk.LabelFrame(self.root, text="输入目录（PNG图片）")
        input_frame.grid(row=1, column=0, padx=10, pady=5, sticky="ew")
        
        ttk.Entry(input_frame, textvariable=self.input_dir, width=60).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(input_frame, text="选择目录", command=self.select_input_directory).pack(side=tk.RIGHT, padx=5, pady=5)

        # 输出目录
        output_frame = ttk.LabelFrame(self.root, text="输出目录")
        output_frame.grid(row=2, column=0, padx=10, pady=5, sticky="ew")
        ttk.Entry(output_frame, textvariable=self.output_dir, width=60).pack(side=tk.LEFT, padx=5, pady=5)
        ttk.Button(output_frame, text="浏览", command=self.select_output_dir).pack(side=tk.RIGHT, padx=5, pady=5)

        # 预览框架
        preview_frame = ttk.LabelFrame(self.root, text="文件预览")
        preview_frame.grid(row=3, column=0, padx=10, pady=5, sticky="nsew")
        
        # 文件列表
        list_frame = ttk.Frame(preview_frame)
        list_frame.pack(fill=tk.BOTH, expand=True, padx=5, pady=5)
        
        # 滚动条
        scrollbar = ttk.Scrollbar(list_frame)
        scrollbar.pack(side=tk.RIGHT, fill=tk.Y)
        
        self.file_listbox = tk.Listbox(list_frame, height=6, yscrollcommand=scrollbar.set)
        self.file_listbox.pack(fill=tk.BOTH, expand=True)
        scrollbar.config(command=self.file_listbox.yview)

        # 转换按钮
        convert_frame = ttk.Frame(self.root)
        convert_frame.grid(row=4, column=0, padx=10, pady=10)
        ttk.Button(convert_frame, text="批量转换", command=self.start_conversion, 
                  style="Accent.TButton").pack(side=tk.LEFT, padx=5)
        ttk.Button(convert_frame, text="刷新文件列表", command=self.refresh_file_list).pack(side=tk.LEFT, padx=5)
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
        self.root.rowconfigure(3, weight=1)
        self.root.rowconfigure(5, weight=1)

    def show_help(self):
        help_text = """RoPet PNG图片转H文件工具

逆向转换模式：
• 将PNG图片转换为C语言数组定义
• 支持文件夹批量处理
• 可生成单独的H文件或合并到一个文件
• 自动更新common.h文件，添加尺寸宏定义

颜色格式支持：
• RGB565：16位颜色，每像素2字节
• RGB888：24位颜色，每像素3字节
• ARGB8888：32位颜色含透明度，每像素4字节

使用方法：
1. 选择包含PNG图片的输入目录
2. 设置输出目录
3. 选择颜色格式
4. 设置数组名前缀（可选）
5. 选择屏幕配置（auto/160x160/240x240）
6. 选择是否合并到单个文件
7. 点击"批量转换"

屏幕配置说明：
• auto：根据图片尺寸自动选择160x160或240x240配置
• 160x160：强制使用160x160屏幕配置
• 240x240：强制使用240x240屏幕配置

输出格式：
• 每个PNG图片转换为const uint16_t数组（RGB565格式）
• 文件格式与项目中big_blue.h保持一致
• 使用宏定义表示数组大小（如ARRAY_NAME_WIDTH*ARRAY_NAME_HEIGHT）
• 尺寸宏定义自动写入common.h文件

注意事项：
• 图片文件名将作为数组名，请确保符合C语言命名规范
• 大尺寸图片可能生成很大的数组
• RGB565格式最适合嵌入式显示应用
• common.h文件会被自动更新，保留系统相关的固定定义
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
        directory = filedialog.askdirectory(title="选择包含PNG图片的目录")
        if directory:
            self.input_dir.set(directory)
            self.refresh_file_list()

    def select_output_dir(self):
        path = filedialog.askdirectory(title="选择输出目录")
        if path:
            self.output_dir.set(path)

    def refresh_file_list(self):
        """刷新文件列表"""
        self.file_listbox.delete(0, tk.END)
        
        input_directory = self.input_dir.get()
        if not input_directory or not os.path.exists(input_directory):
            return
        
        png_files = []
        for root, dirs, files in os.walk(input_directory):
            for file in files:
                if file.lower().endswith('.png'):
                    file_path = os.path.join(root, file)
                    png_files.append(file_path)
        
        for file_path in png_files:
            relative_path = os.path.relpath(file_path, input_directory)
            self.file_listbox.insert(tk.END, relative_path)
        
        print(f"在目录 {input_directory} 中找到 {len(png_files)} 个PNG文件")

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
        
        # 收集所有PNG文件
        png_files = []
        for root, dirs, files in os.walk(input_directory):
            for file in files:
                if file.lower().endswith('.png'):
                    png_files.append(os.path.join(root, file))
        
        if not png_files:
            messagebox.showwarning("警告", "在输入目录中未找到PNG文件")
            return
        
        print(f"开始批量转换，共找到 {len(png_files)} 个PNG文件")
        print(f"输入目录: {input_directory}")
        print(f"输出目录: {output_directory}")
        print("=" * 60)
        
        if self.generate_single_file.get():
            self.convert_to_single_file(png_files, input_directory, output_directory)
        else:
            self.convert_to_separate_files(png_files, input_directory, output_directory)

    def convert_to_separate_files(self, png_files, input_directory, output_directory):
        """转换为单独的H文件"""
        total_files = len(png_files)
        success_count = 0
        image_info_list = []
        
        for i, file_path in enumerate(png_files, 1):
            try:
                print(f"[{i}/{total_files}] 正在处理: {os.path.relpath(file_path, input_directory)}")
                
                # 获取文件信息
                relative_path = os.path.relpath(file_path, input_directory)
                dir_structure = os.path.dirname(relative_path)
                filename = os.path.splitext(os.path.basename(file_path))[0]
                
                # 创建输出目录结构
                if dir_structure:
                    output_subdir = os.path.join(output_directory, dir_structure)
                    os.makedirs(output_subdir, exist_ok=True)
                    output_file_path = os.path.join(output_subdir, f"{filename}.h")
                else:
                    output_file_path = os.path.join(output_directory, f"{filename}.h")
                
                # 转换图片
                array_data, width, height = self.convert_png_to_array(file_path)
                
                # 生成数组名
                array_name = self.generate_array_name(filename)
                
                # 记录图片信息用于更新common.h
                image_info_list.append({
                    'array_name': array_name,
                    'width': width,
                    'height': height,
                    'filename': filename
                })
                
                # 生成H文件内容
                h_content = self.generate_h_file_content(array_name, array_data, width, height, filename)
                
                # 写入文件
                with open(output_file_path, 'w', encoding='utf-8') as f:
                    f.write(h_content)
                
                print(f"  转换成功: {os.path.relpath(output_file_path, output_directory)}")
                print(f"  图片尺寸: {width}×{height}")
                print(f"  数组大小: {len(array_data)} 个元素")
                
                success_count += 1
                
            except Exception as e:
                print(f"  转换失败: {str(e)}")
            
            print("-" * 50)
        
        # 更新common.h文件
        if success_count > 0:
            self.update_common_h_file(output_directory, image_info_list)
        
        print("=" * 60)
        print(f"批量转换完成!")
        print(f"成功转换: {success_count}/{total_files}")
        print(f"输出目录: {output_directory}")
        
        messagebox.showinfo("完成", 
            f"批量转换完成!\n\n"
            f"成功转换: {success_count}/{total_files}\n"
            f"输出目录: {output_directory}\n"
            f"已更新common.h文件")

    def convert_to_single_file(self, png_files, input_directory, output_directory):
        """转换为单个H文件"""
        total_files = len(png_files)
        success_count = 0
        all_arrays = []
        image_info_list = []
        
        print("模式: 合并到单个H文件")
        
        for i, file_path in enumerate(png_files, 1):
            try:
                print(f"[{i}/{total_files}] 正在处理: {os.path.relpath(file_path, input_directory)}")
                
                # 获取文件信息
                relative_path = os.path.relpath(file_path, input_directory)
                filename = os.path.splitext(os.path.basename(file_path))[0]
                
                # 如果有子目录，加入到数组名中
                dir_name = os.path.dirname(relative_path).replace(os.sep, '_')
                if dir_name:
                    full_name = f"{dir_name}_{filename}"
                else:
                    full_name = filename
                
                # 转换图片
                array_data, width, height = self.convert_png_to_array(file_path)
                
                # 生成数组名
                array_name = self.generate_array_name(full_name)
                
                # 记录图片信息用于更新common.h
                image_info_list.append({
                    'array_name': array_name,
                    'width': width,
                    'height': height,
                    'filename': full_name
                })
                
                # 添加到数组列表
                all_arrays.append({
                    'name': array_name,
                    'data': array_data,
                    'width': width,
                    'height': height,
                    'original_file': relative_path
                })
                
                print(f"  处理成功: {array_name}")
                print(f"  图片尺寸: {width}×{height}")
                
                success_count += 1
                
            except Exception as e:
                print(f"  处理失败: {str(e)}")
        
        if all_arrays:
            # 生成合并的H文件
            output_file_path = os.path.join(output_directory, "combined_images.h")
            combined_content = self.generate_combined_h_file(all_arrays)
            
            with open(output_file_path, 'w', encoding='utf-8') as f:
                f.write(combined_content)
            
            # 更新common.h文件
            self.update_common_h_file(output_directory, image_info_list)
            
            print("=" * 60)
            print(f"合并文件生成完成!")
            print(f"输出文件: {output_file_path}")
            print(f"包含数组: {len(all_arrays)} 个")
            
            messagebox.showinfo("完成", 
                f"合并转换完成!\n\n"
                f"成功转换: {success_count}/{total_files}\n"
                f"输出文件: combined_images.h\n"
                f"包含数组: {len(all_arrays)} 个\n"
                f"已更新common.h文件")

    def detect_screen_size_from_images(self, image_info_list):
        """根据图片尺寸检测屏幕大小配置"""
        if not image_info_list:
            return "240x240"  # 默认配置
            
        # 统计图片尺寸，推测屏幕配置
        max_width = max(info['width'] for info in image_info_list)
        max_height = max(info['height'] for info in image_info_list)
        max_size = max(max_width, max_height)
        
        # 根据最大尺寸判断屏幕配置
        if max_size <= 160:
            return "160x160"
        else:
            return "240x240"

    def get_system_config(self, screen_size):
        """获取系统配置定义"""
        if screen_size == "160x160":
            return """#define IRIS_MAP_WIDTH  314
#define IRIS_MAP_HEIGHT 50

#define SCLERA_WIDTH 250
#define SCLERA_HEIGHT 250

#define SCREEN_WIDTH 160
#define SCREEN_HEIGHT 160

#define IRIS_WIDTH  100
#define IRIS_HEIGHT 100

#define SYMMETRICAL_EYELID 

"""
        else:  # 240x240
            return """#define IRIS_MAP_WIDTH  471
#define IRIS_MAP_HEIGHT 75

#define SCLERA_WIDTH 375
#define SCLERA_HEIGHT 375

#define SCREEN_WIDTH 240
#define SCREEN_HEIGHT 240

#define IRIS_WIDTH  150
#define IRIS_HEIGHT 150

#define SYMMETRICAL_EYELID

"""

    def update_common_h_file(self, output_directory, image_info_list):
        """更新common.h文件，添加图片尺寸定义"""
        common_h_path = os.path.join(output_directory, "common.h")
        
        # 确定屏幕配置
        screen_config_setting = self.screen_config.get()
        if screen_config_setting == "auto":
            # 自动检测屏幕尺寸配置
            screen_size = self.detect_screen_size_from_images(image_info_list)
            print(f"自动检测屏幕配置: {screen_size}")
        else:
            # 使用手动选择的配置
            screen_size = screen_config_setting
            print(f"使用手动选择的屏幕配置: {screen_size}")
        
        # 获取系统配置
        system_config = self.get_system_config(screen_size)
        
        # 生成新的图片尺寸定义
        new_definitions = ""
        if image_info_list:
            new_definitions += "// Generated image size definitions\n"
            for info in image_info_list:
                array_name = info['array_name'].upper()
                width = info['width']
                height = info['height']
                new_definitions += f"#define {array_name}_WIDTH  {width}\n"
                new_definitions += f"#define {array_name}_HEIGHT {height}\n"
            new_definitions += "\n"
        
        # 写入更新的common.h文件
        with open(common_h_path, 'w', encoding='utf-8') as f:
            f.write(system_config)
            if new_definitions:
                f.write(new_definitions)
        
        print(f"已更新common.h文件: {common_h_path}")
        print(f"使用配置: {screen_size}")
        if image_info_list:
            print(f"添加了 {len(image_info_list)} 个图片的尺寸定义")

    def load_common_definitions(self):
        """加载common.h文件中的尺寸定义"""
        import re
        import os
        
        # 可能的common.h路径
        possible_paths = [
            os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "main", "eye_data", "160_160", "common.h"),
            os.path.join(os.path.dirname(os.path.dirname(os.getcwd())), "main", "eye_data", "240_240", "common.h"),
            os.path.join(os.getcwd(), "common.h"),
            os.path.join(os.path.dirname(os.getcwd()), "common.h")
        ]
        
        for common_path in possible_paths:
            if os.path.exists(common_path):
                try:
                    with open(common_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # 解析#define宏定义
                    definitions = {}
                    define_pattern = r'#define\s+([A-Z_][A-Z0-9_]*)\s+(\d+)'
                    matches = re.findall(define_pattern, content)
                    
                    for name, value in matches:
                        if 'WIDTH' in name or 'HEIGHT' in name:
                            definitions[name] = int(value)
                    
                    # 计算复合宏（如 IRIS_MAP_WIDTH*IRIS_MAP_HEIGHT）
                    compound_macros = {}
                    for name1, val1 in definitions.items():
                        if 'WIDTH' in name1:
                            base_name = name1.replace('_WIDTH', '')
                            height_name = base_name + '_HEIGHT'
                            if height_name in definitions:
                                compound_name = f"{base_name}_WIDTH*{base_name}_HEIGHT"
                                compound_macros[compound_name] = val1 * definitions[height_name]
                    
                    definitions.update(compound_macros)
                    return definitions
                    
                except Exception as e:
                    continue
        
        return None

    def convert_png_to_array(self, file_path):
        """将PNG图片转换为数组数据"""
        # 加载图片
        img = Image.open(file_path)
        
        # 确保图片是RGB格式
        if img.mode == 'RGBA':
            # 处理透明度
            if self.color_format.get() != 'ARGB8888':
                # 如果不是ARGB8888格式，需要处理透明度
                background = Image.new('RGB', img.size, (255, 255, 255))
                background.paste(img, mask=img.split()[3])  # 使用alpha通道作为mask
                img = background
            # 如果是ARGB8888格式，保持RGBA
        elif img.mode != 'RGB':
            img = img.convert('RGB')
        
        width, height = img.size
        
        # 转换为numpy数组
        if self.color_format.get() == 'ARGB8888' and img.mode == 'RGBA':
            img_array = np.array(img)
            array_data = []
            for y in range(height):
                for x in range(width):
                    r, g, b, a = img_array[y, x]
                    # ARGB8888格式
                    argb_value = (a << 24) | (r << 16) | (g << 8) | b
                    array_data.append(argb_value)
        else:
            img_array = np.array(img)
            array_data = []
            
            if self.color_format.get() == 'RGB565':
                for y in range(height):
                    for x in range(width):
                        r, g, b = img_array[y, x]
                        # 转换为RGB565
                        r565 = (r >> 3) << 11
                        g565 = (g >> 2) << 5
                        b565 = b >> 3
                        rgb565_value = r565 | g565 | b565
                        array_data.append(rgb565_value)
            elif self.color_format.get() == 'RGB888':
                for y in range(height):
                    for x in range(width):
                        r, g, b = img_array[y, x]
                        # RGB888格式
                        rgb888_value = (r << 16) | (g << 8) | b
                        array_data.append(rgb888_value)
        
        return array_data, width, height

    def generate_array_name(self, filename):
        """生成合法的数组名称"""
        # 添加前缀
        prefix = self.array_prefix.get()
        if prefix:
            name = f"{prefix}_{filename}"
        else:
            name = filename
        
        # 清理名称，确保符合C语言标识符规范
        name = re.sub(r'[^a-zA-Z0-9_]', '_', name)
        
        # 确保不以数字开头
        if name and name[0].isdigit():
            name = f"img_{name}"
        
        return name

    def generate_h_file_content(self, array_name, array_data, width, height, original_filename):
        """生成H文件内容 - 参考big_blue.h格式"""
        color_format = self.color_format.get()
        
        # 计算像素总数
        total_pixels = width * height
        
        # 使用尺寸宏定义，格式为 ARRAY_NAME_WIDTH*ARRAY_NAME_HEIGHT
        array_name_upper = array_name.upper()
        size_macro = f"{array_name_upper}_WIDTH*{array_name_upper}_HEIGHT"
        
        # 生成头文件内容 - 完全按照big_blue.h格式
        content = "#include \"common.h\"\n\n"
        
        # 数组声明
        if color_format == 'RGB565':
            data_type = 'uint16_t'
        else:
            data_type = 'uint32_t'
            
        content += f"const {data_type} {array_name}[{size_macro}] = {{\n"
        
        # 数组数据 - 每行8个值，格式与big_blue.h完全一致
        for i in range(0, len(array_data), 8):
            line_data = array_data[i:i+8]
            if color_format == 'RGB565':
                hex_values = [f"0x{val:04X}" for val in line_data]
            else:
                hex_values = [f"0x{val:08X}" for val in line_data]
            
            line_str = "  " + ", ".join(hex_values)
            
            # 最后一行不加逗号
            if i + 8 < len(array_data):
                line_str += ","
            content += line_str + "\n"
        
        content += "};\n"
        
        return content

    def generate_combined_h_file(self, all_arrays):
        """生成合并的H文件内容"""
        color_format = self.color_format.get()
        
        # 文件头 - 简化版本，参考big_blue.h格式
        header = "#include \"common.h\"\n\n"
        
        # 生成所有数组
        arrays_content = ""
        for array_info in all_arrays:
            name = array_info['name']
            data = array_info['data']
            width = array_info['width']
            height = array_info['height']
            original_file = array_info['original_file']
            
            # 数组定义 - 使用宏定义格式
            array_name_upper = name.upper()
            size_macro = f"{array_name_upper}_WIDTH*{array_name_upper}_HEIGHT"
            
            if color_format == 'RGB565':
                arrays_content += f"const uint16_t {name}[{size_macro}] = {{\n"
            else:
                arrays_content += f"const uint32_t {name}[{size_macro}] = {{\n"
            
            # 数组数据 - 每行8个值，与big_blue.h格式一致
            for i in range(0, len(data), 8):
                line_data = data[i:i+8]
                if color_format == 'RGB565':
                    hex_values = [f"0x{val:04X}" for val in line_data]
                else:
                    hex_values = [f"0x{val:08X}" for val in line_data]
                
                line_str = "  " + ", ".join(hex_values)
                if i + 8 < len(data):
                    line_str += ","
                arrays_content += line_str + "\n"
            
            arrays_content += "};\n\n"
        
        return header + arrays_content

def main():
    root = tk.Tk()
    app = PNGToHConverterApp(root)
    root.mainloop()

if __name__ == "__main__":
    main()
