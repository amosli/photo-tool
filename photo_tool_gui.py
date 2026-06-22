import os
import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PIL import Image, ImageTk
from photo_tool import create_photo_layout

# 照片尺寸信息: label -> (mm_tuple, 用途说明, 英寸说明)
PHOTO_SIZE_INFO = {
    "1寸 (25x35 mm)": ((25, 35), "身份证、驾驶证、工作证、简历", "0.98x1.38 in"),
    "小2寸 (33x48 mm)": ((33, 48), "护照、港澳通行证、部分签证", "1.30x1.89 in"),
    "2寸 (35x49 mm)": ((35, 49), "毕业证、学位证、资格证书", "1.38x1.93 in"),
    "大2寸 (35x53 mm)": ((35, 53), "部分国家签证、留学申请", "1.38x2.09 in"),
    "3寸 (55x84 mm)": ((55, 84), "部分证件照需求", "2.17x3.31 in"),
    "35x45 mm": ((35, 45), "日本/申根/英国常用规格", "1.38x1.77 in"),
    "35x50 mm": ((35, 50), "加拿大签证常用规格", "1.38x1.97 in"),
    "51x51 mm": ((51, 51), "美国签证/绿卡（2x2 in）", "2x2 in"),
    "US Visa (51x51 mm)": ((51, 51), "美国签证、绿卡申请", "2x2 in"),
    "Japan (35x45 mm)": ((35, 45), "日本签证、在留资格", "1.38x1.77 in"),
    "Schengen (35x45 mm)": ((35, 45), "欧洲申根国家签证", "1.38x1.77 in"),
    "UK (35x45 mm)": ((35, 45), "英国签证", "1.38x1.77 in"),
    "Canada (35x50 mm)": ((35, 50), "加拿大签证", "1.38x1.97 in"),
    "Thailand (35x45 mm)": ((35, 45), "泰国签证", "1.38x1.77 in"),
}

# 相纸尺寸信息: label -> (mm_tuple, 用途说明, 英寸说明)
PAPER_SIZE_INFO = {
    "3R 89x127 mm": ((89, 127), "小型照片、钱包照", "3.5x5 in"),
    "4R 102x152 mm": ((102, 152), "最常用，日常照片、旅行照", "4x6 in"),
    "5R 127x178 mm": ((127, 178), "桌面摆台、小幅装饰", "5x7 in"),
    "6R 152x203 mm": ((152, 203), "稍大照片、家庭合影", "6x8 in"),
    "8R 203x254 mm": ((203, 254), "大幅照片、装裱相框", "8x10 in"),
    "10R 254x305 mm": ((254, 305), "大幅装饰、艺术照", "10x12 in"),
    "A4 210x297 mm": ((210, 297), "文档、海报、大幅照片", "8.27x11.69 in"),
    "A5 148x210 mm": ((148, 210), "小型海报、手账照片", "5.83x8.27 in"),
    "6寸相纸 102x152 mm": ((102, 152), "6寸相纸（竖版）", "4x6 in"),
}

SIZE_OPTIONS = list(PHOTO_SIZE_INFO.keys()) + ["自定义"]
PAPER_OPTIONS = list(PAPER_SIZE_INFO.keys()) + ["自定义"]


class PhotoToolGUI:
    def __init__(self, root):
        self.root = root
        root.title("证件照排版打印工具")

        frm = ttk.Frame(root, padding=12)
        frm.grid()

        ttk.Label(frm, text="输入图片:").grid(column=0, row=0, sticky="w")
        self.input_var = tk.StringVar()
        ttk.Entry(frm, width=40, textvariable=self.input_var).grid(column=1, row=0)
        ttk.Button(frm, text="选择", command=self.select_image).grid(column=2, row=0)

        ttk.Label(frm, text="照片尺寸:").grid(column=0, row=1, sticky="w")
        self.size_var = tk.StringVar(value=SIZE_OPTIONS[0])
        self.size_cb = ttk.Combobox(frm, values=SIZE_OPTIONS, textvariable=self.size_var, state="readonly", width=30)
        self.size_cb.grid(column=1, row=1, sticky="w")
        self.size_cb.bind('<<ComboboxSelected>>', self.on_size_change)

        # 显示尺寸用途说明
        self.size_info = ttk.Label(frm, text="", wraplength=360)
        self.size_info.grid(column=1, row=2, columnspan=2, sticky="w")

        # 自定义尺寸输入
        self.custom_w_var = tk.StringVar()
        self.custom_h_var = tk.StringVar()
        ttk.Label(frm, text="自定义宽 (mm):").grid(column=0, row=3, sticky="w")
        self.custom_w_entry = ttk.Entry(frm, textvariable=self.custom_w_var, width=10)
        self.custom_h_entry = ttk.Entry(frm, textvariable=self.custom_h_var, width=10)
        ttk.Label(frm, text="高 (mm):").grid(column=1, row=3, sticky="w")
        self.custom_h_entry.grid(column=2, row=3, sticky="w")
        self.custom_w_entry.grid(column=1, row=3, sticky="e")

        # 默认隐藏自定义输入
        self.custom_w_entry.grid_remove()
        self.custom_h_entry.grid_remove()

        ttk.Label(frm, text="相纸:").grid(column=0, row=4, sticky="w")
        self.paper_var = tk.StringVar(value=PAPER_OPTIONS[0])
        self.paper_cb = ttk.Combobox(frm, values=PAPER_OPTIONS, textvariable=self.paper_var, state="readonly", width=30)
        self.paper_cb.grid(column=1, row=4, sticky="w")
        self.paper_cb.bind('<<ComboboxSelected>>', self.on_paper_change)

        self.paper_info = ttk.Label(frm, text="", wraplength=360)
        self.paper_info.grid(column=1, row=5, columnspan=2, sticky="w")

        # 自定义相纸输入
        self.custom_p_w = tk.StringVar()
        self.custom_p_h = tk.StringVar()
        ttk.Label(frm, text="自定义相纸宽 (mm):").grid(column=0, row=6, sticky="w")
        self.custom_p_w_entry = ttk.Entry(frm, textvariable=self.custom_p_w, width=10)
        self.custom_p_h_entry = ttk.Entry(frm, textvariable=self.custom_p_h, width=10)
        ttk.Label(frm, text="高 (mm):").grid(column=1, row=6, sticky="w")
        self.custom_p_h_entry.grid(column=2, row=6, sticky="w")
        self.custom_p_w_entry.grid(column=1, row=6, sticky="e")
        self.custom_p_w_entry.grid_remove()
        self.custom_p_h_entry.grid_remove()

        ttk.Label(frm, text="间距 (mm):").grid(column=0, row=7, sticky="w")
        self.spacing_var = tk.IntVar(value=2)
        ttk.Spinbox(frm, from_=0, to=20, textvariable=self.spacing_var, width=5).grid(column=1, row=7, sticky="w")

        ttk.Label(frm, text="DPI:").grid(column=0, row=8, sticky="w")
        self.dpi_var = tk.IntVar(value=300)
        ttk.Spinbox(frm, from_=72, to=1200, textvariable=self.dpi_var, width=7).grid(column=1, row=8, sticky="w")

        ttk.Button(frm, text="生成排版并保存", command=self.generate).grid(column=1, row=10, pady=8)

        # 初始化说明文字
        self.on_size_change()
        self.on_paper_change()

    def select_image(self):
        p = filedialog.askopenfilename(filetypes=[("Images", "*.jpg;*.jpeg;*.png;*.bmp")])
        if p:
            self.input_var.set(p)

    def on_size_change(self, event=None):
        choice = self.size_var.get()
        if choice == "自定义":
            self.size_info.config(text="自定义尺寸：请输入宽和高（毫米）。")
            self.custom_w_entry.grid()
            self.custom_h_entry.grid()
        else:
            self.custom_w_entry.grid_remove()
            self.custom_h_entry.grid_remove()
            info = PHOTO_SIZE_INFO.get(choice)
            if info:
                mm, use, inch = info
                self.size_info.config(text=f"尺寸: {mm[0]} x {mm[1]} mm ({inch}) — 用途: {use}")
            else:
                self.size_info.config(text="")

    def on_paper_change(self, event=None):
        choice = self.paper_var.get()
        if choice == "自定义":
            self.paper_info.config(text="自定义相纸：请输入宽和高（毫米）。")
            self.custom_p_w_entry.grid()
            self.custom_p_h_entry.grid()
        else:
            self.custom_p_w_entry.grid_remove()
            self.custom_p_h_entry.grid_remove()
            info = PAPER_SIZE_INFO.get(choice)
            if info:
                mm, use, inch = info
                self.paper_info.config(text=f"相纸: {mm[0]} x {mm[1]} mm ({inch}) — 用途: {use}")
            else:
                self.paper_info.config(text="")

    def generate(self):
        img = self.input_var.get()
        if not img or not os.path.exists(img):
            messagebox.showerror("错误", "请选择有效的输入图片")
            return

        size_choice = self.size_var.get()
        if size_choice == "自定义":
            try:
                w = float(self.custom_w_var.get())
                h = float(self.custom_h_var.get())
                photo_type = (w, h)
            except Exception:
                messagebox.showerror("错误", "请输入有效的自定义照片尺寸（数字，毫米）。")
                return
        else:
            photo_type = PHOTO_SIZE_INFO.get(size_choice, (None,))[0]

        paper_choice = self.paper_var.get()
        if paper_choice == "自定义":
            try:
                pw = float(self.custom_p_w.get())
                ph = float(self.custom_p_h.get())
                paper_size = (pw, ph)
            except Exception:
                messagebox.showerror("错误", "请输入有效的自定义相纸尺寸（数字，毫米）。")
                return
        else:
            paper_size = PAPER_SIZE_INFO.get(paper_choice, (None,))[0]

        try:
            create_photo_layout(img, output_path=None, photo_type=photo_type, spacing_mm=self.spacing_var.get(), dpi=self.dpi_var.get(), paper_size_mm=paper_size)
            src_dir, src_name = os.path.split(img)
            stem, ext = os.path.splitext(src_name)
            if isinstance(photo_type, str):
                tag = photo_type
            elif isinstance(photo_type, (tuple, list)):
                tag = f"{int(photo_type[0])}x{int(photo_type[1])}mm"
            else:
                tag = "output"
            out_path = os.path.join(src_dir, f"{stem}_{tag}{ext}")
            messagebox.showinfo("完成", f"已保存：{out_path}")
        except Exception as e:
            messagebox.showerror("错误", str(e))


def main():
    root = tk.Tk()
    app = PhotoToolGUI(root)
    root.mainloop()


if __name__ == '__main__':
    main()
