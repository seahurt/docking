import tkinter as tk
from tkinter import ttk, filedialog, messagebox, scrolledtext
import subprocess
import os
import threading
from tool_detector import ToolDetector

class MolecularDockingGUI:
    def __init__(self, root):
        self.root = root
        self.root.title("分子对接程序 - Molecular Docking")
        self.root.geometry("900x700")
        
        self.current_step = 1
        self.total_steps = 6
        
        self.tool_detector = ToolDetector()
        self.tool_paths = {}
        self.tool_entries = {}
        self.tool_status_labels = {}
        self.tool_status_vars = {}
        
        self.setup_ui()
        
    def setup_ui(self):
        main_frame = ttk.Frame(self.root, padding="10")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        main_frame.rowconfigure(6, weight=1)
        
        title_label = ttk.Label(main_frame, text="分子对接程序", font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=2, pady=(0, 10))
        
        self.progress_frame = ttk.Frame(main_frame)
        self.progress_frame.grid(row=1, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=(0, 20))
        
        self.step_labels = []
        for i in range(1, self.total_steps + 1):
            step_text = f"步骤 {i}: {self.get_step_description(i)}"
            label = ttk.Label(self.progress_frame, text=step_text, font=("Arial", 10))
            label.pack(anchor=tk.W, pady=2)
            self.step_labels.append(label)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=2, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        self.content_frame = ttk.Frame(main_frame)
        self.content_frame.grid(row=3, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        self.button_frame = ttk.Frame(main_frame)
        self.button_frame.grid(row=4, column=0, columnspan=2, pady=10)
        
        ttk.Separator(main_frame, orient='horizontal').grid(row=5, column=0, columnspan=2, sticky=(tk.W, tk.E), pady=10)
        
        log_label = ttk.Label(main_frame, text="运行日志:", font=("Arial", 10, "bold"))
        log_label.grid(row=6, column=0, sticky=tk.W)
        
        self.log_text = scrolledtext.ScrolledText(main_frame, height=15, wrap=tk.WORD)
        self.log_text.grid(row=7, column=0, columnspan=2, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        main_frame.rowconfigure(7, weight=1)
        
        self.update_step_display()
        
    def get_step_description(self, step):
        descriptions = {
            1: "检测和配置工具",
            2: "准备受体文件 (PDB格式)",
            3: "准备配体文件 (SMILES格式)",
            4: "转换为SDF格式",
            5: "转换为PDBQT格式",
            6: "运行分子对接"
        }
        return descriptions.get(step, "")
        
    def update_step_display(self):
        for i, label in enumerate(self.step_labels, 1):
            if i == self.current_step:
                label.configure(foreground="blue", font=("Arial", 10, "bold"))
            elif i < self.current_step:
                label.configure(foreground="green", font=("Arial", 10))
            else:
                label.configure(foreground="gray", font=("Arial", 10))
        
        for widget in self.content_frame.winfo_children():
            widget.destroy()
        
        if self.current_step == 1:
            self.setup_step1()
        elif self.current_step == 2:
            self.setup_step2()
        elif self.current_step == 3:
            self.setup_step3()
        elif self.current_step == 4:
            self.setup_step4()
        elif self.current_step == 5:
            self.setup_step5()
        elif self.current_step == 6:
            self.setup_step6()
            
    def setup_step1(self):
        ttk.Label(self.content_frame, text="步骤 1: 检测和配置工具", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        info_text = """
程序需要以下工具才能正常运行：
  - OpenBabel: 用于分子格式转换
  - AutoDock Vina: 用于分子对接

程序会自动检测这些工具，如果未找到，您可以手动指定路径。
        """
        ttk.Label(self.content_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        self.tool_frame = ttk.Frame(self.content_frame)
        self.tool_frame.pack(fill=tk.BOTH, expand=True, pady=10)
        
        for tool_key, tool_info in self.tool_detector.tools.items():
            tool_box = ttk.LabelFrame(self.tool_frame, text=f"{tool_info['name']} {'[必需]' if tool_info['required'] else '[可选]'}")
            tool_box.pack(fill=tk.X, pady=5, padx=5)
            
            desc_label = ttk.Label(tool_box, text=tool_info['description'], font=("Arial", 9))
            desc_label.pack(anchor=tk.W, padx=5, pady=2)
            
            path_frame = ttk.Frame(tool_box)
            path_frame.pack(fill=tk.X, padx=5, pady=5)
            
            path_var = tk.StringVar()
            self.tool_entries[tool_key] = path_var
            
            ttk.Label(path_frame, text="路径:").pack(side=tk.LEFT, padx=5)
            ttk.Entry(path_frame, textvariable=path_var, width=50).pack(side=tk.LEFT, padx=5, fill=tk.X, expand=True)
            ttk.Button(path_frame, text="浏览...", command=lambda k=tool_key: self.browse_tool_path(k)).pack(side=tk.LEFT, padx=5)
            
            status_var = tk.StringVar(value="未检测")
            status_label = ttk.Label(tool_box, textvariable=status_var, font=("Arial", 9))
            status_label.pack(anchor=tk.W, padx=5, pady=2)
            self.tool_status_labels[tool_key] = status_label
            self.tool_status_vars[tool_key] = status_var
        
        ttk.Button(self.content_frame, text="自动检测工具", command=self.auto_detect_tools).pack(pady=10)
        
        self.setup_navigation_buttons()
        
    def setup_step2(self):
        ttk.Label(self.content_frame, text="步骤 2: 准备受体文件", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        info_text = """
请选择受体的晶体结构PDB文件。
程序将自动：
  - 将PDB转换为PDBQT格式
  - 提取晶体结构中的活性位点（配体位置）
  - 生成vina.conf配置文件
        """
        ttk.Label(self.content_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        file_frame = ttk.Frame(self.content_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.step2_pdb_file = tk.StringVar()
        ttk.Label(file_frame, text="PDB文件:").pack(side=tk.LEFT, padx=5)
        ttk.Entry(file_frame, textvariable=self.step2_pdb_file, width=40).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="选择文件", command=self.choose_pdb_file).pack(side=tk.LEFT)
        
        self.setup_navigation_buttons()
        
    def setup_step3(self):
        ttk.Label(self.content_frame, text="步骤 3: 准备配体文件", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        info_text = """
请准备一个SMILES格式的配体文件，格式如下：
  SMILES字符串  配体名称

例如：
  CCO ethanol
  c1ccccc1 benzene
        """
        ttk.Label(self.content_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        file_frame = ttk.Frame(self.content_frame)
        file_frame.pack(fill=tk.X, pady=5)
        
        self.step3_smiles_file = tk.StringVar()
        ttk.Entry(file_frame, textvariable=self.step3_smiles_file, width=50).pack(side=tk.LEFT, padx=5)
        ttk.Button(file_frame, text="选择文件", command=self.choose_smiles_file).pack(side=tk.LEFT)
        
        self.setup_navigation_buttons()
        
    def setup_step4(self):
        ttk.Label(self.content_frame, text="步骤 4: 转换为SDF格式", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        info_text = """
此步骤将使用RDKit将SMILES文件转换为SDF格式，并生成多个构象。
        """
        ttk.Label(self.content_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        self.setup_navigation_buttons()
        
    def setup_step5(self):
        ttk.Label(self.content_frame, text="步骤 5: 转换为PDBQT格式", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        info_text = """
此步骤将使用OpenBabel将SDF文件转换为PDBQT格式，用于分子对接。
        """
        ttk.Label(self.content_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        self.setup_navigation_buttons()
        
    def setup_step6(self):
        ttk.Label(self.content_frame, text="步骤 6: 运行分子对接", font=("Arial", 12, "bold")).pack(anchor=tk.W, pady=5)
        
        info_text = """
此步骤将使用AutoDock Vina进行分子对接。
对接参数已在步骤2中自动生成（vina.conf文件）。
        """
        ttk.Label(self.content_frame, text=info_text, justify=tk.LEFT).pack(anchor=tk.W, pady=10)
        
        self.setup_navigation_buttons()
        
    def setup_navigation_buttons(self):
        for widget in self.button_frame.winfo_children():
            widget.destroy()
        
        if self.current_step > 1:
            ttk.Button(self.button_frame, text="上一步", command=self.prev_step).pack(side=tk.LEFT, padx=5)
        
        if self.current_step < self.total_steps:
            ttk.Button(self.button_frame, text="下一步", command=self.next_step).pack(side=tk.LEFT, padx=5)
        
        ttk.Button(self.button_frame, text="执行当前步骤", command=self.execute_step).pack(side=tk.LEFT, padx=5)
        
        if self.current_step == self.total_steps:
            ttk.Button(self.button_frame, text="完成", command=self.finish).pack(side=tk.LEFT, padx=5)
    
    def auto_detect_tools(self):
        self.log_message("开始自动检测工具...\n")
        
        results = self.tool_detector.detect_all_tools()
        
        for tool_key, info in results.items():
            if info['found']:
                self.tool_entries[tool_key].set(info['path'])
                self.tool_status_vars[tool_key].set("✓ 已找到")
                self.tool_status_labels[tool_key].configure(foreground="green")
                self.log_message(f"✓ {info['name']}: {info['path']}")
            else:
                self.tool_status_vars[tool_key].set("✗ 未找到")
                self.tool_status_labels[tool_key].configure(foreground="red")
                self.log_message(f"✗ {info['name']}: 未找到，请手动指定路径")
        
        self.log_message("\n检测完成!")
    
    def browse_tool_path(self, tool_key):
        filename = filedialog.askopenfilename(
            title=f"选择{self.tool_detector.tools[tool_key]['name']}可执行文件",
            filetypes=[("可执行文件", "*.exe"), ("所有文件", "*.*")]
        )
        if filename:
            self.tool_entries[tool_key].set(filename)
            self.verify_tool_path(tool_key, filename)
    
    def verify_tool_path(self, tool_key, path):
        if os.path.exists(path):
            self.tool_status_vars[tool_key].set("✓ 有效")
            self.tool_status_labels[tool_key].configure(foreground="green")
            self.tool_detector.set_tool_path(tool_key, path)
        else:
            self.tool_status_vars[tool_key].set("✗ 文件不存在")
            self.tool_status_labels[tool_key].configure(foreground="red")
            
    def choose_pdb_file(self):
        filename = filedialog.askopenfilename(
            title="选择PDB文件",
            filetypes=[("PDB files", "*.pdb"), ("All files", "*.*")]
        )
        if filename:
            self.step2_pdb_file.set(filename)
            
    def choose_smiles_file(self):
        filename = filedialog.askopenfilename(
            title="选择SMILES文件",
            filetypes=[("SMILES files", "*.smi"), ("Text files", "*.txt"), ("All files", "*.*")]
        )
        if filename:
            self.step3_smiles_file.set(filename)
            
    def next_step(self):
        if self.current_step < self.total_steps:
            self.current_step += 1
            self.update_step_display()
            
    def prev_step(self):
        if self.current_step > 1:
            self.current_step -= 1
            self.update_step_display()
            
    def execute_step(self):
        self.log_message(f"\n{'='*50}")
        self.log_message(f"开始执行步骤 {self.current_step}")
        self.log_message(f"{'='*50}\n")
        
        thread = threading.Thread(target=self._execute_step_thread)
        thread.daemon = True
        thread.start()
        
    def _execute_step_thread(self):
        try:
            if self.current_step == 1:
                self.execute_step1()
            elif self.current_step == 2:
                self.execute_step2()
            elif self.current_step == 3:
                self.execute_step3()
            elif self.current_step == 4:
                self.execute_step4()
            elif self.current_step == 5:
                self.execute_step5()
            elif self.current_step == 6:
                self.execute_step6()
                
            self.log_message(f"\n步骤 {self.current_step} 完成!\n")
            messagebox.showinfo("完成", f"步骤 {self.current_step} 执行完成!")
            
        except Exception as e:
            self.log_message(f"\n错误: {str(e)}\n")
            messagebox.showerror("错误", f"执行失败: {str(e)}")
            
    def execute_step1(self):
        self.log_message("验证工具配置...")
        
        for tool_key in self.tool_detector.tools:
            path = self.tool_entries[tool_key].get()
            if not path:
                raise Exception(f"{self.tool_detector.tools[tool_key]['name']} 路径未设置")
            
            if not os.path.exists(path):
                raise Exception(f"{self.tool_detector.tools[tool_key]['name']} 路径不存在: {path}")
            
            self.tool_detector.set_tool_path(tool_key, path)
            self.log_message(f"✓ {self.tool_detector.tools[tool_key]['name']}: {path}")
        
        self.log_message("\n所有工具配置完成!")
        
    def execute_step2(self):
        pdb_file = self.step2_pdb_file.get()
        if not pdb_file:
            raise Exception("请先选择PDB文件")
        
        self.log_message(f"检查PDB文件: {pdb_file}")
        if not os.path.exists(pdb_file):
            raise Exception(f"文件不存在: {pdb_file}")
        
        self.log_message("运行 prepare_receptor.py...")
        
        result = subprocess.run(
            ["python", "prepare_receptor.py", pdb_file, "."],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        self.log_message(result.stdout)
        if result.stderr:
            self.log_message(f"警告: {result.stderr}")
            
        if result.returncode != 0:
            raise Exception("受体准备失败")
        
        self.log_message("受体准备完成!")
        
    def execute_step3(self):
        smiles_file = self.step3_smiles_file.get()
        if not smiles_file:
            raise Exception("请先选择SMILES文件")
        
        self.log_message(f"检查SMILES文件: {smiles_file}")
        if not os.path.exists(smiles_file):
            raise Exception(f"文件不存在: {smiles_file}")
        
        self.log_message("准备完成，可以进行下一步")
        
    def execute_step4(self):
        self.log_message("运行 smile_to_sdf.py...")
        
        if not os.path.exists("ligands.smi"):
            raise Exception("找不到 ligands.smi 文件，请先完成步骤3")
        
        result = subprocess.run(
            ["python", "smile_to_sdf.py"],
            capture_output=True,
            text=True,
            cwd=os.getcwd()
        )
        
        self.log_message(result.stdout)
        if result.stderr:
            self.log_message(f"警告: {result.stderr}")
            
        if result.returncode != 0:
            raise Exception("转换失败")
            
    def execute_step5(self):
        self.log_message("运行 sdf_to_pdbqt.bat...")
        
        if not os.path.exists("sdf"):
            raise Exception("找不到 sdf 目录，请先完成步骤4")
        
        result = subprocess.run(
            ["sdf_to_pdbqt.bat"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            shell=True
        )
        
        self.log_message(result.stdout)
        if result.stderr:
            self.log_message(f"警告: {result.stderr}")
            
        if result.returncode != 0:
            raise Exception("转换失败")
            
    def execute_step6(self):
        self.log_message("运行 run_vina.bat...")
        
        if not os.path.exists("vina.conf"):
            raise Exception("找不到 vina.conf 文件，请先完成步骤2")
        if not os.path.exists("pdbqt"):
            raise Exception("找不到 pdbqt 目录，请先完成步骤5")
        
        result = subprocess.run(
            ["run_vina.bat"],
            capture_output=True,
            text=True,
            cwd=os.getcwd(),
            shell=True
        )
        
        self.log_message(result.stdout)
        if result.stderr:
            self.log_message(f"警告: {result.stderr}")
            
        if result.returncode != 0:
            raise Exception("对接失败")
            
    def log_message(self, message):
        self.log_text.insert(tk.END, message + "\n")
        self.log_text.see(tk.END)
        self.root.update_idletasks()
        
    def finish(self):
        messagebox.showinfo("完成", "所有步骤已完成! 对接结果保存在 docking_results 目录中。")
        self.root.quit()

def main():
    root = tk.Tk()
    app = MolecularDockingGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()
