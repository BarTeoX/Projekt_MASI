import tkinter as tk
from tkinter import ttk, messagebox, font

class UnitermTransformerApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("Transformator Unitermów - Styl Schematyczny")
        self.geometry("600x750")
        self.term_a = tk.StringVar(value="A")
        self.term_b = tk.StringVar(value="B")
        self.term_c = tk.StringVar(value="C")
        self.term_d = tk.StringVar(value="D")
        self.h_separator = tk.StringVar(value=";")
        self.choice_to_replace = tk.IntVar(value=0)
        self.create_widgets()
        self._update_dynamic_labels()

    def create_widgets(self):
        main_frame = ttk.Frame(self, padding="20")
        main_frame.pack(fill="both", expand=True)
        input_frame = ttk.LabelFrame(main_frame, text="Dane wejściowe", padding="15")
        input_frame.pack(fill="x", pady=10)
        input_frame.columnconfigure(1, weight=1)
        labels_vars = [
            ("Uniterm A (z wyrażenia poziomego):", self.term_a),
            ("Uniterm B (z wyrażenia poziomego):", self.term_b),
            ("Uniterm C (z wyrażenia pionowego):", self.term_c),
            ("Uniterm D (z wyrażenia pionowego):", self.term_d),
            ("Separator operacji poziomej:", self.h_separator)
        ]
        for i, (text, var) in enumerate(labels_vars):
            ttk.Label(input_frame, text=text).grid(row=i, column=0, sticky="w", pady=3)
            ttk.Entry(input_frame, textvariable=var, width=30).grid(row=i, column=1, sticky="ew")
        self.term_a.trace_add("write", self._update_dynamic_labels)
        self.term_b.trace_add("write", self._update_dynamic_labels)
        self.h_separator.trace_add("write", self._update_dynamic_labels)
        choice_frame = ttk.LabelFrame(main_frame, text="Wybór transformacji", padding="15")
        choice_frame.pack(fill="x", pady=10)
        self.dynamic_choice_label = ttk.Label(choice_frame, text="")
        self.dynamic_choice_label.pack(anchor="w", pady=5)
        self.radio_a = ttk.Radiobutton(choice_frame, text="", variable=self.choice_to_replace, value=0)
        self.radio_a.pack(anchor="w", padx=20)
        self.radio_b = ttk.Radiobutton(choice_frame, text="", variable=self.choice_to_replace, value=1)
        self.radio_b.pack(anchor="w", padx=20)
        transform_button = ttk.Button(main_frame, text="Wygeneruj transformację", command=self.perform_transformation)
        transform_button.pack(pady=20, ipady=5, fill="x")
        result_frame = ttk.LabelFrame(main_frame, text="Wynik Graficzny", padding="15")
        result_frame.pack(fill="both", expand=True, pady=10)
        self.canvas = tk.Canvas(result_frame, bg="white", highlightthickness=0)
        self.canvas.pack(fill="both", expand=True)

    def _update_dynamic_labels(self, *args):
        a, b, sep = self.term_a.get() or "A", self.term_b.get() or "B", self.h_separator.get() or ";"
        self.dynamic_choice_label.config(text=f"Który uniterm z wyrażenia [{a} {sep} {b}] zamienić?")
        self.radio_a.config(text=f"Zamień {a}")
        self.radio_b.config(text=f"Zamień {b}")

    def perform_transformation(self):
        a, b, c, d, h_sep = self.term_a.get(), self.term_b.get(), self.term_c.get(), self.term_d.get(), self.h_separator.get()
        choice_index = self.choice_to_replace.get()
        if not all([a, b, c, d, h_sep]):
            messagebox.showerror("Błąd", "Wszystkie pola muszą być wypełnione!")
            return
        vertical_unit = {'type': 'v', 'sep': ',', 'terms': [c, d]}
        final_structure = {'type': 'h', 'sep': h_sep, 'terms': [a, b]}
        final_structure['terms'][choice_index] = vertical_unit
        self.canvas.delete("all")
        self.draw_structure(self.canvas, final_structure)

    def get_structure_bbox(self, data, font_style):
        if not isinstance(data, dict): return (font_style.measure(data), font_style.metrics('linespace'))
        padding = 20
        bracket_padding = 20

        if data['type'] == 'h':
            total_width, max_height = 0, 0
            sep_width = font_style.measure(data['sep']) if len(data['terms']) > 1 else 0
            for term in data['terms']:
                w, h = self.get_structure_bbox(term, font_style)
                total_width += w
                max_height = max(max_height, h)
            total_width += (len(data['terms']) - 1) * (sep_width + padding)
            return (total_width + bracket_padding, max_height + bracket_padding)

        if data['type'] == 'v':
            max_width, total_height = 0, 0
            sep_height = font_style.metrics('linespace') / 2
            for term in data['terms']:
                w, h = self.get_structure_bbox(term, font_style)
                max_width = max(max_width, w)
                total_height += h
            total_height += (len(data['terms']) - 1) * sep_height
            return (max_width + bracket_padding, total_height + bracket_padding)
        return (0, 0)

    def draw_structure(self, canvas, data):
        canvas.update_idletasks()
        cx, cy = canvas.winfo_width() / 2, canvas.winfo_height() / 2
        font_style = font.Font(family="Arial", size=20, weight="bold")
        self._draw_recursive(canvas, data, cx, cy, font_style)

    def _draw_recursive(self, canvas, data, cx, cy, font_style):
        if not isinstance(data, dict):
            canvas.create_text(cx, cy, text=data, font=font_style, fill="darkblue")
            return
        
        total_w, total_h = self.get_structure_bbox(data, font_style)
        x1, y1 = cx - total_w / 2, cy - total_h / 2
        x2, y2 = cx + total_w / 2, cy + total_h / 2
        
        padding, sep_char, terms = 20, data['sep'], data['terms']
        tick_size = 15 

        if data['type'] == 'h':
            canvas.create_line(x1, y1, x2, y1, width=3, fill="darkgreen")
            canvas.create_line(x1, y1, x1, y1 + tick_size, width=3, fill="darkgreen")
            canvas.create_line(x2, y1, x2, y1 + tick_size, width=3, fill="darkgreen")
            
            term_widths = [self.get_structure_bbox(t, font_style)[0] for t in terms]
            sep_width = font_style.measure(sep_char)
            content_width = sum(term_widths) + (len(terms) - 1) * (sep_width + padding)
            current_x = cx - content_width / 2
            for i, term in enumerate(terms):
                term_w, term_h = self.get_structure_bbox(term, font_style)
                self._draw_recursive(canvas, term, current_x + term_w / 2, cy + tick_size/2, font_style)
                current_x += term_w
                if i < len(terms) - 1:
                    canvas.create_text(current_x + (sep_width + padding) / 2, cy + tick_size/2, text=sep_char, font=font_style)
                    current_x += sep_width + padding

        elif data['type'] == 'v':
            canvas.create_line(x1, y1, x1, y2, width=3, fill="darkgreen")
            canvas.create_line(x1, y1, x1 + tick_size, y1, width=3, fill="darkgreen")
            canvas.create_line(x1, y2, x1 + tick_size, y2, width=3, fill="darkgreen")

            term_heights = [self.get_structure_bbox(t, font_style)[1] for t in terms]
            sep_height = font_style.metrics('linespace') / 2
            content_height = sum(term_heights) + (len(terms) - 1) * sep_height
            current_y = cy - content_height / 2
            content_cx = cx + tick_size/2 
            for i, term in enumerate(terms):
                term_w, term_h = self.get_structure_bbox(term, font_style)
                self._draw_recursive(canvas, term, content_cx, current_y + term_h / 2, font_style)
                current_y += term_h
                if i < len(terms) - 1:
                    canvas.create_text(content_cx, current_y + sep_height / 2, text=sep_char, font=font_style)
                    current_y += sep_height

if __name__ == "__main__":
    app = UnitermTransformerApp()
    app.mainloop()