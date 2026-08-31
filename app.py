"""
Producer Adviser v1.0 — Local Desktop Client (API-Driven)
Run with: python producer_adviser.py
Dependencies: pip install requests
"""

import tkinter as tk
from tkinter import ttk, filedialog, messagebox
import io
import random
import os
import requests

API_URL = "http://127.0.0.1:8000"

# ─────────────────────────────────────────────
# TAALINSTELLINGEN / LANGUAGE SETTINGS
# ─────────────────────────────────────────────
LANGUAGES = {
    "NL": {
        "sidebar_title": "Producer Adviser v1.0",
        "gen_settings": "🎛️ Generator Instellingen",
        "choose_genre": "Kies je Genre",
        "complexity": "Drum Complexiteit",
        "swing": "Swing / Humanize (%)",
        "feedback_btn": "📝 Geef Feedback",
        "drop_midi": "Drop je MIDI-akkoorden hier",
        "how_it_works": "Hoe werkt het?",
        "step1": "1. Upload je akkoorden — Sleep een .mid bestand met je basisakkoorden.",
        "step2": "2. Check je frequenties — PA analyseert noten op toonsoort, ritme en botsingen.",
        "step3": "3. Genereer Stems — Download unieke baslijnen, drum stems en melodieën.",
        "analysis_title": "🛠️ Live Analyse",
        "metric_scale": "Toonladder",
        "metric_notes": "Noten",
        "chart_title": "📊 Frequentie Blauwdruk",
        "collision_title": "⚠️ Collision Alerts",
        "mud_alarm": "MODDER-ALARM: Je hebt {} noten in het Low-Mid gebied (250-500Hz). Dit botst met je kick en bas! Verplaats minimaal 2 noten een octaaf omhoog.",
        "low_mid_warn": "LET OP (Low-Mid): Het begint een beetje druk te worden in het lage middengebied. EQ dit gebied weg op je synth.",
        "sub_warn": "SUB-COLLISION: Akkoord-noten in het Sub-gebied. Dit vecht met je Kick/808.",
        "clean_mix": "MIX IS CLEAN: Goede verdeling van frequenties gevonden.",
        "advice_title": "🤖 AI Co-Producer: Dynamisch Studio Advies",
        "hiphop_tips": [
            "De Boom-Bap Bass: Omdat je in {scale} zit, speel je baslijn voornamelijk rond de noot {root_note}. Tip: Slide aan het eind van de 4e maat kort omhoog.",
            "Lo-Fi Pocket: Je tempo is {tempo} BPM. Probeer de baslijn net een paar milliseconden ná de kick te laten vallen voor een enorm slepende groove.",
            "Melodische Variatie: Gebruik de 5e noot in je {scale} toonladder als 'springplank' vlak voordat je terugkeert naar je {root_note} basnoot."
        ],
        "trap_tips": [
            "De 808 Bounce: Zet een harde 808 op de {root_note}. Omdat het {scale} is, klinkt het ijzersterk als je snelle accenten op de off-beats plaatst.",
            "808 Glide: Start op de {root_note} en teken een snelle 808-slide naar een octaaf hoger, exact vlak voordat de snare op de 3e tel valt.",
            "Syncopated Drop: Laat je 808 de eerste tel rusten als het akkoord wisselt. Val pas in op de 'en' van de 1. Dit geeft je beat een enorme bounce."
        ],
        "rb_tips": [
            "De Soulful Sub: Begin op {root_note}, maar blijf daar niet zweven. Wandel via de {scale} toonladder langzaam omlaag richting de volgende tel.",
            "Neo-Soul Timing: Speel je bas extreem zacht en nét te laat achter de tel (D'Angelo stijl). Dit past perfect bij het {tempo} BPM tempo.",
            "R&B Arp Bass: Pluk de hoge noten uit je {root_note} akkoord en speel ze één voor één af als een trage, zwoele bas-arpeggio."
        ],
        "export_title": "🎹 Exporteer MIDI Starters",
        "btn_bass": "🎸 Download Baslijn",
        "btn_drums": "📦 Download Drum Stems",
        "btn_melody": "🎹 Download Melodie",
        "browse_btn": "📂 Open MIDI Bestand",
        "no_file": "Geen bestand geladen",
        "override_title": "⚙️ Override AI Analyse",
        "bpm_label": "Snelheid (BPM)",
        "root_label": "Grondtoon",
        "scale_label": "Toonladder",
        "saved": "Opgeslagen!",
        "error_load": "Fout bij laden van MIDI bestand of server is offline.",
        "scale_explain_title": "🤖 Wat betekent deze toonladder?",
        "major_vibe": "Vibe: Vrolijk, hoopvol en energiek. Veel pop, house en vrolijke hiphop gebruikt deze toonladder.",
        "minor_vibe": "Vibe: Droevig, donker, of emotioneel. De gouden standaard voor Trap, Drill en melancholische R&B.",
        "dorian_vibe": "Vibe: Dromerig en jazzy. Lijkt op mineur maar net wat lichter en zwevender.",
        "other_vibe": "Vibe: Een unieke of exotische klankkleur. Probeer handmatig een andere toonsoort.",
    },
    "EN": {
        "sidebar_title": "Producer Adviser v1.0",
        "gen_settings": "🎛️ Generator Settings",
        "choose_genre": "Choose your Genre",
        "complexity": "Drum Complexity",
        "swing": "Swing / Humanize (%)",
        "feedback_btn": "📝 Give Feedback",
        "drop_midi": "Load your MIDI chords",
        "how_it_works": "How does it work?",
        "step1": "1. Upload your chords — Open a .mid file with your base chords.",
        "step2": "2. Check your frequencies — PA analyzes notes for key, rhythm, and collisions.",
        "step3": "3. Generate Stems — Download unique basslines, drum stems, and melodies.",
        "analysis_title": "🛠️ Live Analysis",
        "metric_scale": "Scale",
        "metric_notes": "Notes",
        "chart_title": "📊 Frequency Blueprint",
        "collision_title": "⚠️ Collision Alerts",
        "mud_alarm": "MUD ALARM: You have {} notes in the Low-Mid area (250-500Hz). This clashes with your kick and bass! Move at least 2 notes an octave up.",
        "low_mid_warn": "CAUTION (Low-Mid): It's getting crowded in the lower mid-range. EQ this area slightly on your synth.",
        "sub_warn": "SUB-COLLISION: Chord notes in the Sub area. This fights with your Kick/808.",
        "clean_mix": "MIX IS CLEAN: Good frequency distribution found.",
        "advice_title": "🤖 AI Co-Producer: Dynamic Studio Advice",
        "hiphop_tips": [
            "The Boom-Bap Bass: Because you are in {scale}, play your bassline mostly around {root_note}. Tip: Slide up briefly at the end of the 4th bar.",
            "Lo-Fi Pocket: Your tempo is {tempo} BPM. Try to drop the bassline just a few milliseconds after the kick for a heavily dragging groove.",
            "Melodic Variation: Use the 5th note in your {scale} scale as a springboard just before returning to your {root_note} bass note."
        ],
        "trap_tips": [
            "The 808 Bounce: Put a hard 808 on the {root_note}. Since it's {scale}, it sounds strong if you place fast accents on the off-beats.",
            "808 Glide: Start on the {root_note} and draw a fast 808-slide an octave higher, right before the snare hits on the 3rd beat.",
            "Syncopated Drop: Rest your 808 on the first beat when the chord changes. Drop in on the 'and' of the 1. Huge unexpected bounce."
        ],
        "rb_tips": [
            "The Soulful Sub: Start on {root_note}, but don't hover there. Walk down the {scale} scale slowly towards the next beat.",
            "Neo-Soul Timing: Play your bass extremely soft and just a bit late behind the beat (D'Angelo style). Fits perfectly with {tempo} BPM.",
            "R&B Arp Bass: Pluck the high notes from your {root_note} chord and play them one by one as a slow, sultry bass arpeggio."
        ],
        "export_title": "🎹 Export MIDI Starters",
        "btn_bass": "🎸 Download Bassline",
        "btn_drums": "📦 Download Drum Stems",
        "btn_melody": "🎹 Download Melody",
        "browse_btn": "📂 Open MIDI File",
        "no_file": "No file loaded",
        "override_title": "⚙️ Override AI Analysis",
        "bpm_label": "Tempo (BPM)",
        "root_label": "Root Note",
        "scale_label": "Scale",
        "saved": "Saved!",
        "error_load": "Error loading MIDI file or server is offline.",
        "scale_explain_title": "🤖 What does this scale mean?",
        "major_vibe": "Vibe: Happy, hopeful, and energetic. A lot of pop, house, and upbeat hip-hop use this scale.",
        "minor_vibe": "Vibe: Sad, dark, or emotional. The gold standard for Trap, Drill, and melancholic R&B.",
        "dorian_vibe": "Vibe: Dreamy and jazzy. Like minor but with a slightly brighter, floating feel.",
        "other_vibe": "Vibe: A unique or exotic tone. Try manually overriding the scale to experiment.",
    }
}

SCALE_TRANSLATE = {
    "Harmonisch Mineur": "Harmonic Minor",
    "Dorisch": "Dorian",
    "Natuurlijk Mineur": "Natural Minor",
    "Mixolydisch": "Mixolydian",
    "Majeur": "Major",
    "Complex / Onbekend": "Complex / Unknown"
}
SCALE_TRANSLATE_BACK = {v: k for k, v in SCALE_TRANSLATE.items()}
NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']

# ─────────────────────────────────────────────
# TKINTER GUI (CLIENT-SIDE)
# ─────────────────────────────────────────────
class ProducerAdviserApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Producer Adviser v1.0 🎹")
        self.root.geometry("900x760")
        self.root.configure(bg="#1a1a2e")
        self.root.resizable(True, True)

        self.lang = tk.StringVar(value="EN")
        self.genre = tk.StringVar(value="Hiphop")
        self.complexity = tk.StringVar(value="Modern")
        self.swing = tk.IntVar(value=20)
        self.current_data = None
        self.freq_data = None
        self.filepath = None

        self._build_ui()

    @property
    def T(self):
        return LANGUAGES[self.lang.get()]

    def _style(self):
        style = ttk.Style()
        style.theme_use("clam")
        style.configure("TFrame", background="#1a1a2e")
        style.configure("TLabel", background="#1a1a2e", foreground="#e0e0e0", font=("Inter", 10))
        style.configure("Title.TLabel", background="#1a1a2e", foreground="#ff6b35", font=("Inter", 18, "bold"))
        style.configure("Sub.TLabel", background="#1a1a2e", foreground="#888888", font=("Inter", 10))
        style.configure("Section.TLabel", background="#1a1a2e", foreground="#ffffff", font=("Inter", 11, "bold"))
        style.configure("Metric.TLabel", background="#16213e", foreground="#00d4ff", font=("Inter", 13, "bold"))
        style.configure("MetricTitle.TLabel", background="#16213e", foreground="#888888", font=("Inter", 9))
        style.configure("TButton", font=("Inter", 10), padding=6)
        style.configure("Accent.TButton", font=("Inter", 10, "bold"), padding=8)
        style.configure("TCombobox", fieldbackground="#16213e", background="#16213e", foreground="#e0e0e0")
        style.configure("TScale", background="#1a1a2e")
        style.configure("TRadiobutton", background="#1a1a2e", foreground="#e0e0e0", font=("Inter", 10))
        style.configure("Success.TLabel", background="#1a1a2e", foreground="#00c875", font=("Inter", 10))
        style.configure("Warning.TLabel", background="#1a1a2e", foreground="#f0a500", font=("Inter", 10))
        style.configure("Error.TLabel", background="#1a1a2e", foreground="#ff4b4b", font=("Inter", 10))
        style.configure("Info.TLabel", background="#16213e", foreground="#c0c0c0", font=("Inter", 10), wraplength=780)
        return style

    def _build_ui(self):
        self._style()
        canvas = tk.Canvas(self.root, bg="#1a1a2e", highlightthickness=0)
        scrollbar = ttk.Scrollbar(self.root, orient="vertical", command=canvas.yview)
        self.scroll_frame = ttk.Frame(canvas)
        self.scroll_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.create_window((0, 0), window=self.scroll_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)
        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1*(e.delta/120)), "units"))

        main = self.scroll_frame
        main.configure(padding=20)

        top = ttk.Frame(main)
        top.pack(fill="x", pady=(0, 8))
        ttk.Label(top, text="Producer Adviser", style="Title.TLabel").pack(side="left")
        lang_frame = ttk.Frame(top)
        lang_frame.pack(side="right")
        for lng in ("EN", "NL"):
            ttk.Radiobutton(lang_frame, text=lng, variable=self.lang, value=lng,
                            command=self._refresh_ui).pack(side="left", padx=4)

        self.subtitle_lbl = ttk.Label(main, style="Sub.TLabel",
            text="Your AI-driven co-producer. Upload your chords and unlock mathematically perfect basslines and drums.")
        self.subtitle_lbl.pack(anchor="w", pady=(0, 12))

        ttk.Separator(main, orient="horizontal").pack(fill="x", pady=8)

        settings_frame = ttk.Frame(main)
        settings_frame.pack(fill="x", pady=6)

        self.genre_lbl = ttk.Label(settings_frame, text=self.T["choose_genre"])
        self.genre_lbl.grid(row=0, column=0, sticky="w", padx=(0, 8))
        self.genre_cb = ttk.Combobox(settings_frame, textvariable=self.genre,
                                     values=["Hiphop", "R&B", "Trap"], state="readonly", width=12)
        self.genre_cb.grid(row=1, column=0, sticky="w", padx=(0, 16))

        self.complexity_lbl = ttk.Label(settings_frame, text=self.T["complexity"])
        self.complexity_lbl.grid(row=0, column=1, sticky="w", padx=(0, 8))
        self.complexity_cb = ttk.Combobox(settings_frame, textvariable=self.complexity,
                                          values=["Basic", "Modern", "Busy"], state="readonly", width=12)
        self.complexity_cb.grid(row=1, column=1, sticky="w", padx=(0, 16))

        self.swing_lbl = ttk.Label(settings_frame, text=f"{self.T['swing']}: 20%")
        self.swing_lbl.grid(row=0, column=2, sticky="w", padx=(0, 8))
        swing_scale = ttk.Scale(settings_frame, from_=0, to=100, variable=self.swing, orient="horizontal",
                                length=160, command=self._update_swing_label)
        swing_scale.grid(row=1, column=2, sticky="w")

        ttk.Separator(main, orient="horizontal").pack(fill="x", pady=8)

        file_frame = ttk.Frame(main)
        file_frame.pack(fill="x", pady=6)
        self.browse_btn = ttk.Button(file_frame, text=self.T["browse_btn"], command=self._load_file, style="Accent.TButton")
        self.browse_btn.pack(side="left", padx=(0, 12))
        self.file_lbl = ttk.Label(file_frame, text=self.T["no_file"], style="Sub.TLabel")
        self.file_lbl.pack(side="left")

        self.howto_frame = ttk.Frame(main)
        self.howto_frame.pack(fill="x", pady=12)
        self._build_howto()

        ttk.Separator(main, orient="horizontal").pack(fill="x", pady=8)

        self.analysis_frame = ttk.Frame(main)
        self.analysis_frame.pack(fill="x")

    def _build_howto(self):
        for w in self.howto_frame.winfo_children():
            w.destroy()
        T = self.T
        ttk.Label(self.howto_frame, text=f"🚀 {T['how_it_works']}", style="Section.TLabel").pack(anchor="w", pady=(0, 6))
        for step in [T["step1"], T["step2"], T["step3"]]:
            ttk.Label(self.howto_frame, text=step, style="Info.TLabel").pack(anchor="w", pady=2)

    def _update_swing_label(self, val=None):
        v = int(float(self.swing.get()))
        self.swing_lbl.config(text=f"{self.T['swing']}: {v}%")

    def _refresh_ui(self):
        T = self.T
        self.subtitle_lbl.config(text=(
            "Jouw AI-gedreven co-producer. Upload je akkoorden en ontgrendel wiskundig perfecte baslijnen en drums."
            if self.lang.get() == "NL" else
            "Your AI-driven co-producer. Upload your chords and unlock mathematically perfect basslines and drums."
        ))
        self.genre_lbl.config(text=T["choose_genre"])
        self.complexity_lbl.config(text=T["complexity"])
        self.swing_lbl.config(text=f"{T['swing']}: {self.swing.get()}%")
        self.browse_btn.config(text=T["browse_btn"])
        if not self.filepath:
            self.file_lbl.config(text=T["no_file"])
        self._build_howto()
        if self.current_data:
            self._render_analysis()

    def _load_file(self):
        path = filedialog.askopenfilename(filetypes=[("MIDI files", "*.mid *.midi")])
        if not path:
            return
        self.filepath = path
        self.file_lbl.config(text=os.path.basename(path))

        # API Call
        try:
            with open(path, "rb") as f:
                files = {"file": (os.path.basename(path), f, "audio/midi")}
                res = requests.post(f"{API_URL}/analyze", files=files)

            if res.status_code == 200:
                api_data = res.json()
                if "error" in api_data:
                    messagebox.showerror("Error", api_data["error"])
                    return
                self.current_data = api_data["theorie"]
                self.freq_data = api_data["frequenties"]
                self.howto_frame.pack_forget()
                self._render_analysis()
            else:
                messagebox.showerror("Error", self.T["error_load"])
        except Exception as e:
            messagebox.showerror("Error", f"Kan de API niet bereiken: {e}")

    def _render_analysis(self):
        for w in self.analysis_frame.winfo_children():
            w.destroy()

        T = self.T
        data = dict(self.current_data)
        lang = self.lang.get()

        display_reg = data['register']
        display_scale = data['scale']
        if lang == "EN":
            reg_map = {"Laag": "Low", "Midden": "Mid", "Hoog": "High"}
            display_reg = reg_map.get(display_reg, display_reg)
            display_scale = SCALE_TRANSLATE.get(display_scale, display_scale)

        ttk.Label(self.analysis_frame, text=T["analysis_title"], style="Section.TLabel").pack(anchor="w", pady=(8, 6))
        metrics_row = ttk.Frame(self.analysis_frame)
        metrics_row.pack(fill="x", pady=4)
        for label, value in [
            ("BPM", data['tempo']),
            ("Register", display_reg),
            (T["metric_scale"], f"{data['root_name']} {display_scale}"),
            (T["metric_notes"], data['notes_count']),
        ]:
            box = ttk.Frame(metrics_row, padding=10, relief="flat")
            box.pack(side="left", padx=6, ipadx=6, ipady=4)
            box.configure(style="TFrame")
            tk.Label(box, text=str(value), bg="#16213e", fg="#00d4ff",
                     font=("Inter", 14, "bold")).pack()
            tk.Label(box, text=label, bg="#16213e", fg="#888888",
                     font=("Inter", 9)).pack()

        self._build_override(data, display_scale, lang)

        ttk.Separator(self.analysis_frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(self.analysis_frame, text=T["chart_title"], style="Section.TLabel").pack(anchor="w", pady=(4, 6))
        self._draw_bar_chart(self.freq_data)

        ttk.Label(self.analysis_frame, text=T["collision_title"], style="Section.TLabel").pack(anchor="w", pady=(8, 4))
        low_mid_val = self.freq_data.get("3. Low-Mid (250-500Hz)", 0)
        sub_val = self.freq_data.get("1. Sub (0-60Hz)", 0)
        if low_mid_val >= 5:
            ttk.Label(self.analysis_frame, text=T["mud_alarm"].format(low_mid_val),
                      style="Error.TLabel", wraplength=800).pack(anchor="w")
        elif low_mid_val == 4:
            ttk.Label(self.analysis_frame, text=T["low_mid_warn"],
                      style="Warning.TLabel", wraplength=800).pack(anchor="w")
        elif sub_val >= 1:
            ttk.Label(self.analysis_frame, text=T["sub_warn"],
                      style="Warning.TLabel", wraplength=800).pack(anchor="w")
        else:
            ttk.Label(self.analysis_frame, text=T["clean_mix"],
                      style="Success.TLabel").pack(anchor="w")

        self._build_scale_explain(display_scale, lang)

        ttk.Separator(self.analysis_frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(self.analysis_frame, text=T["advice_title"], style="Section.TLabel").pack(anchor="w", pady=(4, 6))
        genre = self.genre.get()
        root_note = data['root_name']
        tempo = data['tempo']
        tip_key = {"Hiphop": "hiphop_tips", "Trap": "trap_tips", "R&B": "rb_tips"}.get(genre, "hiphop_tips")
        tips = [t.format(scale=display_scale, root_note=root_note, tempo=tempo) for t in T[tip_key]]
        tip_style = "Error.TLabel" if genre == "Trap" else "Success.TLabel" if genre == "R&B" else "Info.TLabel"
        ttk.Label(self.analysis_frame, text=random.choice(tips),
                  style=tip_style, wraplength=800).pack(anchor="w", pady=4)

        ttk.Separator(self.analysis_frame, orient="horizontal").pack(fill="x", pady=10)

        ttk.Label(self.analysis_frame, text=T["export_title"], style="Section.TLabel").pack(anchor="w", pady=(4, 8))
        btn_row = ttk.Frame(self.analysis_frame)
        btn_row.pack(fill="x")

        root_num = data['root_number']
        scale_nl = data['scale'] 
        root_name = data['root_name']

        def save_bass():
            path = filedialog.asksaveasfilename(
                defaultextension=".mid",
                filetypes=[("MIDI", "*.mid")],
                initialfile=f"PA_Bass_{genre}_{root_name}.mid")
            if path:
                try:
                    res = requests.get(f"{API_URL}/generate/bass", params={"root_number": root_num, "genre": genre, "swing_amount": self.swing.get()})
                    if res.status_code == 200:
                        with open(path, "wb") as f:
                            f.write(res.content)
                        messagebox.showinfo("✅", T["saved"])
                    else:
                        messagebox.showerror("Error", "API generatie mislukt.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        def save_drums():
            path = filedialog.asksaveasfilename(
                defaultextension=".zip",
                filetypes=[("ZIP", "*.zip")],
                initialfile=f"PA_Drum_Stems_{genre}.zip")
            if path:
                try:
                    res = requests.get(f"{API_URL}/generate/drums", params={"genre": genre, "complexity": self.complexity.get(), "swing_amount": self.swing.get()})
                    if res.status_code == 200:
                        with open(path, "wb") as f:
                            f.write(res.content)
                        messagebox.showinfo("✅", T["saved"])
                    else:
                        messagebox.showerror("Error", "API generatie mislukt.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        def save_melody():
            path = filedialog.asksaveasfilename(
                defaultextension=".mid",
                filetypes=[("MIDI", "*.mid")],
                initialfile=f"PA_Melody_{genre}_{display_scale}.mid")
            if path:
                try:
                    res = requests.get(f"{API_URL}/generate/melody", params={"root_number": root_num, "scale_type": scale_nl, "genre": genre, "swing_amount": self.swing.get()})
                    if res.status_code == 200:
                        with open(path, "wb") as f:
                            f.write(res.content)
                        messagebox.showinfo("✅", T["saved"])
                    else:
                        messagebox.showerror("Error", "API generatie mislukt.")
                except Exception as e:
                    messagebox.showerror("Error", str(e))

        ttk.Button(btn_row, text=T["btn_bass"], command=save_bass, style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(btn_row, text=T["btn_drums"], command=save_drums, style="Accent.TButton").pack(side="left", padx=(0, 10))
        ttk.Button(btn_row, text=T["btn_melody"], command=save_melody, style="Accent.TButton").pack(side="left")

        ttk.Label(self.analysis_frame, text="").pack(pady=20)

    def _build_override(self, data, display_scale, lang):
        T = self.T
        override_toggle = tk.BooleanVar(value=False)
        override_container = ttk.Frame(self.analysis_frame)
        override_container.pack(fill="x", pady=6)

        header = ttk.Frame(override_container)
        header.pack(fill="x")
        toggle_btn = ttk.Button(header, text=f"▶  {T['override_title']}",
                                command=lambda: self._toggle_override(override_toggle, override_body, toggle_btn, T))
        toggle_btn.pack(anchor="w")

        override_body = ttk.Frame(override_container, padding=(8, 6))

        bpm_var = tk.IntVar(value=int(data['tempo']))
        ttk.Label(override_body, text=T["bpm_label"]).grid(row=0, column=0, sticky="w", padx=(0, 12))
        bpm_spin = ttk.Spinbox(override_body, from_=40, to=250, textvariable=bpm_var, width=7)
        bpm_spin.grid(row=1, column=0, sticky="w", padx=(0, 16))

        root_var = tk.StringVar(value=data['root_name'])
        ttk.Label(override_body, text=T["root_label"]).grid(row=0, column=1, sticky="w", padx=(0, 12))
        root_cb = ttk.Combobox(override_body, textvariable=root_var, values=NOTES, state="readonly", width=7)
        root_cb.grid(row=1, column=1, sticky="w", padx=(0, 16))

        scale_options_nl = ["Majeur", "Natuurlijk Mineur", "Harmonisch Mineur", "Dorisch", "Mixolydisch"]
        scale_display = [SCALE_TRANSLATE.get(s, s) if lang == "EN" else s for s in scale_options_nl]
        current_display = display_scale if display_scale in scale_display else scale_display[0]
        scale_var = tk.StringVar(value=current_display)
        ttk.Label(override_body, text=T["scale_label"]).grid(row=0, column=2, sticky="w", padx=(0, 12))
        scale_cb = ttk.Combobox(override_body, textvariable=scale_var, values=scale_display, state="readonly", width=18)
        scale_cb.grid(row=1, column=2, sticky="w")

        def apply_override():
            sel_display = scale_var.get()
            sel_nl = SCALE_TRANSLATE_BACK.get(sel_display, sel_display)
            data['tempo'] = bpm_var.get()
            data['root_name'] = root_var.get()
            data['root_number'] = NOTES.index(root_var.get())
            data['scale'] = sel_nl
            self.current_data = data
            self._render_analysis()

        ttk.Button(override_body, text="✅ Apply", command=apply_override).grid(row=1, column=3, padx=(16, 0))

    def _toggle_override(self, var, body, btn, T):
        if var.get():
            body.pack_forget()
            var.set(False)
            btn.config(text=f"▶  {T['override_title']}")
        else:
            body.pack(fill="x", pady=4)
            var.set(True)
            btn.config(text=f"▼  {T['override_title']}")

    def _build_scale_explain(self, display_scale, lang):
        T = self.T
        ttk.Label(self.analysis_frame, text=T["scale_explain_title"], style="Section.TLabel").pack(anchor="w", pady=(8, 4))
        if "Major" in display_scale or "Majeur" in display_scale:
            vibe = T["major_vibe"]
            style = "Success.TLabel"
        elif "Minor" in display_scale or "Mineur" in display_scale:
            vibe = T["minor_vibe"]
            style = "Info.TLabel"
        elif "Dorian" in display_scale or "Dorisch" in display_scale:
            vibe = T["dorian_vibe"]
            style = "Info.TLabel"
        else:
            vibe = T["other_vibe"]
            style = "Warning.TLabel"
        ttk.Label(self.analysis_frame, text=vibe, style=style, wraplength=800).pack(anchor="w")

    def _draw_bar_chart(self, freq_data):
        canvas = tk.Canvas(self.analysis_frame, bg="#16213e", height=140,
                           highlightthickness=0, relief="flat")
        canvas.pack(fill="x", padx=0, pady=4)

        labels = list(freq_data.keys())
        values = list(freq_data.values())
        max_val = max(values) if max(values) > 0 else 1

        bar_colors = ["#ff4b4b", "#ff904b", "#ffdd4b", "#4bffb5", "#4bb5ff", "#b54bff"]
        padding = 30
        chart_w = 860
        bar_w = (chart_w - padding * 2) / len(labels) - 6
        max_h = 90

        for i, (lbl, val) in enumerate(zip(labels, values)):
            x0 = padding + i * ((chart_w - padding * 2) / len(labels))
            bar_h = (val / max_val) * max_h if max_val else 0
            y0 = 120 - bar_h
            y1 = 120
            canvas.create_rectangle(x0, y0, x0 + bar_w, y1,
                                    fill=bar_colors[i % len(bar_colors)], outline="")
            canvas.create_text(x0 + bar_w / 2, 128, text=str(val),
                                fill="#e0e0e0", font=("Inter", 9))
            
            short = lbl.split("(")[0].strip().replace("1. ", "").replace("2. ", "") \
                       .replace("3. ", "").replace("4. ", "").replace("5. ", "").replace("6. ", "")
            canvas.create_text(x0 + bar_w / 2, 138, text=short[:8],
                                fill="#666666", font=("Inter", 7))


# ─────────────────────────────────────────────
# ENTRY POINT
# ─────────────────────────────────────────────
if __name__ == "__main__":
    root = tk.Tk()
    app = ProducerAdviserApp(root)
    root.mainloop()
