import tkinter as tk
from tkinter import ttk, scrolledtext, messagebox
from ijp import IncrementalJSONParser  # Assuming IJP library is installed
import threading

class JSONParserDemo:
    def __init__(self, root):
        self.root = root
        self.root.title("Incremental JSON Parser Demo")

        # Configure grid layout
        self.root.rowconfigure(0, weight=1)
        self.root.rowconfigure(1, weight=0)
        self.root.rowconfigure(2, weight=1)
        self.root.columnconfigure(0, weight=1)

        # Top Text Box for JSON Input
        self.json_input = scrolledtext.ScrolledText(root, height=15, wrap=tk.WORD)
        self.json_input.grid(row=0, column=0, sticky='nsew', padx=10, pady=10)
        self.json_input.insert(tk.END, self.get_default_json())

        # Center Frame for Controls
        control_frame = ttk.Frame(root)
        control_frame.grid(row=1, column=0, pady=10)

        # Chunk Size Control
        ttk.Label(control_frame, text="Chunk Size (bytes):").grid(row=0, column=0, padx=5, pady=5, sticky='e')
        self.chunk_size_var = tk.IntVar(value=4)
        self.chunk_size_spin = ttk.Spinbox(control_frame, from_=1, to=1024, textvariable=self.chunk_size_var, width=10)
        self.chunk_size_spin.grid(row=0, column=1, padx=5, pady=5, sticky='w')

        # Interval Control
        ttk.Label(control_frame, text="Interval (ms):").grid(row=0, column=2, padx=5, pady=5, sticky='e')
        self.interval_var = tk.IntVar(value=500)
        self.interval_spin = ttk.Spinbox(control_frame, from_=10, to=10000, textvariable=self.interval_var, width=10)
        self.interval_spin.grid(row=0, column=3, padx=5, pady=5, sticky='w')

        # Go Button
        self.go_button = ttk.Button(control_frame, text="Go", command=self.start_parsing)
        self.go_button.grid(row=0, column=4, padx=10, pady=5)

        # Bottom Text Box for Parser Output
        self.output_box = scrolledtext.ScrolledText(root, height=15, wrap=tk.WORD, state='disabled')
        self.output_box.grid(row=2, column=0, sticky='nsew', padx=10, pady=10)

        # Initialize variables for highlighting
        self.current_highlight = None
        self.json_length = 0

    def get_default_json(self):
        return '''{
"very_long_string": "The quick brown fox jumps over the lazy dog.",
"even_longer_string": "624562 435276 34576345 254362 54625 6457 6537 65734567235 6772546725 446754 76546 435634 653462346 2465234 624356 24562 62346"
}'''

    def start_parsing(self):
        json_data = self.json_input.get("1.0", tk.END).strip()
        if not json_data:
            messagebox.showerror("Input Error", "Please provide JSON data to parse.")
            return

        try:
            chunk_size = int(self.chunk_size_var.get())
            interval = int(self.interval_var.get())
            if chunk_size <= 0 or interval < 0:
                raise ValueError
        except ValueError:
            messagebox.showerror("Input Error", "Please enter valid numeric values for chunk size and interval.")
            return

        # Disable controls during parsing
        self.go_button.config(state='disabled')
        self.chunk_size_spin.config(state='disabled')
        self.interval_spin.config(state='disabled')
        self.json_input.config(state='disabled')
        self.output_box.config(state='normal')
        self.output_box.delete("1.0", tk.END)
        self.output_box.config(state='disabled')

        # Remove previous highlights
        self.json_input.tag_remove("highlight", "1.0", tk.END)

        # Start parsing in a separate thread to keep UI responsive
        threading.Thread(target=self.parse_json, args=(json_data, chunk_size, interval), daemon=True).start()

    def parse_json(self, json_data, chunk_size, interval):
        parser = IncrementalJSONParser()
        self.json_length = len(json_data)
        chunks = [json_data[i:i + chunk_size] for i in range(0, len(json_data), chunk_size)]
        total_chunks = len(chunks)
        sent_chars = 0

        for index, chunk in enumerate(chunks):
            # Send chunk to parser
            parser.send(chunk)
            sent_chars += len(chunk)

            # Update parser output
            self.update_output(parser)

            # Highlight the sent chunk
            self.highlight_text(sent_chars - len(chunk), sent_chars)

            # Wait for the specified interval
            if interval > 0 and index < total_chunks - 1:
                self.root.after(interval)

        # Re-enable controls after parsing
        self.root.after(0, self.enable_controls)

    def update_output(self, parser):
        for token in parser:
            self.append_output(str(token))

    def append_output(self, text):
        def append():
            self.output_box.config(state='normal')
            self.output_box.insert(tk.END, text + "\n")
            self.output_box.see(tk.END)
            self.output_box.config(state='disabled')
        self.root.after(0, append)

    def highlight_text(self, start, end):
        def highlight():
            start_index = self.index_to_position(start)
            end_index = self.index_to_position(end)
            # Remove previous highlight
            if self.current_highlight:
                self.json_input.tag_remove("highlight", self.current_highlight[0], self.current_highlight[1])
            # Add new highlight
            self.json_input.tag_add("highlight", start_index, end_index)
            self.json_input.tag_config("highlight", background="yellow")
            self.current_highlight = (start_index, end_index)
        self.root.after(0, highlight)

    def index_to_position(self, index):
        # Convert character index to Tkinter Text widget position
        lines = self.json_input.get("1.0", tk.END).split('\n')
        current = 0
        for line_num, line in enumerate(lines, 1):
            if current + len(line) + 1 > index:
                char_index = index - current
                return f"{line_num}.{char_index}"
            current += len(line) + 1
        return tk.END

    def enable_controls(self):
        self.go_button.config(state='normal')
        self.chunk_size_spin.config(state='normal')
        self.interval_spin.config(state='normal')
        self.json_input.config(state='normal')

def main():
    root = tk.Tk()
    app = JSONParserDemo(root)
    root.mainloop()

if __name__ == "__main__":
    main()