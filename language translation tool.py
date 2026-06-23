import os
import tempfile
import tkinter as tk
from tkinter import ttk, messagebox

from deep_translator import GoogleTranslator
from gtts import gTTS

try:
    from playsound import playsound
    AUDIO_AVAILABLE = True
except Exception:
    AUDIO_AVAILABLE = False


class TranslatorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Language Translation Tool")
        self.root.geometry("640x560")
        self.root.resizable(False, False)

        # ---- Get supported languages: {'english': 'en', 'french': 'fr', ...}
        self.languages = GoogleTranslator().get_supported_languages(as_dict=True)
        # Display names, capitalized, sorted alphabetically
        self.lang_names = sorted(name.title() for name in self.languages.keys())

        self._build_ui()

    # ------------------------------------------------------------------ UI
    def _build_ui(self):
        pad = {"padx": 12, "pady": 6}

        title = tk.Label(
            self.root, text="🌍 Language Translation Tool",
            font=("Segoe UI", 16, "bold")
        )
        title.pack(pady=(15, 5))

        # ---- Input box
        tk.Label(self.root, text="Enter text:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=15
        )
        self.input_text = tk.Text(self.root, height=6, width=70, wrap="word",
                                   font=("Segoe UI", 10))
        self.input_text.pack(padx=15, pady=(0, 10))

        # ---- Language selectors
        lang_frame = tk.Frame(self.root)
        lang_frame.pack(**pad)

        tk.Label(lang_frame, text="From:", font=("Segoe UI", 10)).grid(row=0, column=0, padx=5)
        self.source_lang = ttk.Combobox(
            lang_frame, values=["Auto Detect"] + self.lang_names,
            state="readonly", width=20
        )
        self.source_lang.set("Auto Detect")
        self.source_lang.grid(row=0, column=1, padx=5)

        tk.Label(lang_frame, text="To:", font=("Segoe UI", 10)).grid(row=0, column=2, padx=15)
        self.target_lang = ttk.Combobox(
            lang_frame, values=self.lang_names, state="readonly", width=20
        )
        self.target_lang.set("French")
        self.target_lang.grid(row=0, column=3, padx=5)

        # ---- Translate button
        translate_btn = tk.Button(
            self.root, text="Translate ➜", font=("Segoe UI", 11, "bold"),
            bg="#4CAF50", fg="white", padx=10, pady=5,
            command=self.translate_text
        )
        translate_btn.pack(pady=10)

        # ---- Output box
        tk.Label(self.root, text="Translated text:", font=("Segoe UI", 10, "bold")).pack(
            anchor="w", padx=15
        )
        self.output_text = tk.Text(self.root, height=6, width=70, wrap="word",
                                    font=("Segoe UI", 10), state="disabled",
                                    bg="#f4f4f4")
        self.output_text.pack(padx=15, pady=(0, 10))

        # ---- Optional buttons: Copy & Speak
        btn_frame = tk.Frame(self.root)
        btn_frame.pack(pady=5)

        tk.Button(btn_frame, text="📋 Copy", width=15,
                  command=self.copy_text).grid(row=0, column=0, padx=10)
        tk.Button(btn_frame, text="🔊 Speak", width=15,
                  command=self.speak_text).grid(row=0, column=1, padx=10)

        self.status = tk.Label(self.root, text="", fg="gray")
        self.status.pack(pady=(5, 0))

    # ------------------------------------------------------------- Logic
    def translate_text(self):
        text = self.input_text.get("1.0", "end").strip()
        if not text:
            messagebox.showwarning("Empty input", "Please enter some text to translate.")
            return

        source_name = self.source_lang.get()
        target_name = self.target_lang.get()

        source_code = "auto" if source_name == "Auto Detect" else self.languages[source_name.lower()]
        target_code = self.languages[target_name.lower()]

        try:
            self.status.config(text="Translating...")
            self.root.update_idletasks()

            translated = GoogleTranslator(source=source_code, target=target_code).translate(text)

            self.output_text.config(state="normal")
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", translated)
            self.output_text.config(state="disabled")

            self.status.config(text="Done ✓")
        except Exception as e:
            self.status.config(text="")
            messagebox.showerror("Translation error", f"Something went wrong:\n{e}")

    def copy_text(self):
        translated = self.output_text.get("1.0", "end").strip()
        if not translated:
            messagebox.showinfo("Nothing to copy", "Translate some text first.")
            return
        self.root.clipboard_clear()
        self.root.clipboard_append(translated)
        self.status.config(text="Copied to clipboard ✓")

    def speak_text(self):
        translated = self.output_text.get("1.0", "end").strip()
        if not translated:
            messagebox.showinfo("Nothing to speak", "Translate some text first.")
            return

        target_name = self.target_lang.get()
        target_code = self.languages[target_name.lower()]

        try:
            self.status.config(text="Generating audio...")
            self.root.update_idletasks()

            tts = gTTS(text=translated, lang=target_code)
            tmp_path = os.path.join(tempfile.gettempdir(), "translation_audio.mp3")
            tts.save(tmp_path)

            if AUDIO_AVAILABLE:
                playsound(tmp_path)
                self.status.config(text="Played audio ✓")
            else:
                self.status.config(text=f"Saved audio to {tmp_path}")
        except Exception as e:
            self.status.config(text="")
            messagebox.showerror("Speech error", f"Could not generate speech:\n{e}")


if __name__ == "__main__":
    root = tk.Tk()
    app = TranslatorApp(root)
    root.mainloop()
