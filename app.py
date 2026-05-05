import streamlit as st
import mido
import io
import pandas as pd
import random
import zipfile
# --- TAALINSTELLINGEN ---
# --- TAALINSTELLINGEN ---
LANGUAGES = {
    "NL": {
        "sidebar_title": "### *Producer Adviser v1.0*",
        "gen_settings": "### 🎛️ Generator Instellingen",
        "choose_genre": "Kies je Genre",
        "complexity": "Drum Complexiteit",
        "swing": "Swing / Humanize (%)",
        "feedback_btn": "📝 Geef Feedback",
        "drop_midi": "Drop je MIDI-akkoorden hier",
        "how_it_works": "Hoe werkt het?",
        "step1": "**1. Upload je akkoorden**\n\nSleep een .mid bestand met je basisakkoorden in het vak hierboven.",
        "step2": "**2. Check je frequenties**\n\nPA analyseert je noten op toonsoort, ritme en botsingen.",
        "step3": "**3. Genereer Stems**\n\nDownload unieke baslijnen, drum stems en melodieën.",
        "analysis_title": "### 🛠️ Live Analyse",
        "metric_scale": "Toonladder",
        "metric_notes": "Noten",
        "chart_title": "### 📊 Frequentie Blauwdruk",
        "collision_title": "### ⚠️ Collision Alerts",
        "mud_alarm": "**MODDER-ALARM:** Je hebt {} noten in het Low-Mid gebied (250-500Hz). Dit botst met je kick en bas! Verplaats minimaal 2 noten een octaaf omhoog.",
        "low_mid_warn": "**LET OP (Low-Mid):** Het begint een beetje druk te worden in het lage middengebied. EQ dit gebied ietsjes weg op je synth.",
        "sub_warn": "**SUB-COLLISION:** Akkoord-noten in het Sub-gebied. Dit vecht met je Kick/808.",
        "clean_mix": "**MIX IS CLEAN:** Goede verdeling van frequenties gevonden.",
        "advice_title": "### 🤖 AI Co-Producer: Dynamisch Studio Advies",
        "hiphop_tips": [
            "**De Boom-Bap Bass:** Omdat je in **{scale}** zit, speel je baslijn voornamelijk rond de noot **{root_note}**. Tip: Slide aan het eind van de 4e maat kort omhoog.",
            "**Lo-Fi Pocket:** Je tempo is {tempo} BPM. Probeer de baslijn net een paar milliseconden ná de kick te laten vallen voor een enorm slepende groove.",
            "**Melodische Variatie:** Gebruik de 5e noot in je **{scale}** toonladder als 'springplank' vlak voordat je terugkeert naar je **{root_note}** basnoot."
        ],
        "trap_tips": [
            "**De 808 Bounce:** Zet een harde 808 op de **{root_note}**. Omdat het **{scale}** is, klinkt het ijzersterk als je snelle accenten op de 'off-beats' plaatst.",
            "**808 Glide:** Start op de **{root_note}** en teken een snelle 808-slide naar een octaaf hoger, exact vlak voordat de snare op de 3e tel valt.",
            "**Syncopated Drop:** Laat je 808 de eerste tel rusten als het akkoord wisselt. Val pas in op de 'en' van de 1. Dit geeft je beat een enorme bounce."
        ],
        "rb_tips": [
            "**De Soulful Sub:** Begin op **{root_note}**, maar blijf daar niet zweven. Wandel via de **{scale}** toonladder langzaam omlaag richting de volgende tel.",
            "**Neo-Soul Timing:** Speel je bas extreem zacht en nét te laat achter de tel (D'Angelo stijl). Dit past perfect bij het {tempo} BPM tempo.",
            "**R&B Arp Bass:** Pluk de hoge noten uit je **{root_note}** akkoord en speel ze één voor één af als een trage, zwoele bas-arpeggio."
        ],
        "export_title": "### 🎹 Exporteer MIDI Starters",
        "btn_bass": "🎸 Download Baslijn",
        "btn_drums": "📦 Download Drum Stems",
        "btn_melody": "🎹 Download Melodie"
    },
    "EN": {
        "sidebar_title": "### *Producer Adviser v1.0*",
        "gen_settings": "### 🎛️ Generator Settings",
        "choose_genre": "Choose your Genre",
        "complexity": "Drum Complexity",
        "swing": "Swing / Humanize (%)",
        "feedback_btn": "📝 Give Feedback",
        "drop_midi": "Drop your MIDI chords here",
        "how_it_works": "How does it work?",
        "step1": "**1. Upload your chords**\n\nDrag a .mid file with your base chords into the box above.",
        "step2": "**2. Check your frequencies**\n\nPA analyzes your notes for key, rhythm, and collisions.",
        "step3": "**3. Generate Stems**\n\nDownload unique basslines, drum stems, and melodies.",
        "analysis_title": "### 🛠️ Live Analysis",
        "metric_scale": "Scale",
        "metric_notes": "Notes",
        "chart_title": "### 📊 Frequency Blueprint",
        "collision_title": "### ⚠️ Collision Alerts",
        "mud_alarm": "**MUD ALARM:** You have {} notes in the Low-Mid area (250-500Hz). This clashes with your kick and bass! Move at least 2 notes an octave up.",
        "low_mid_warn": "**CAUTION (Low-Mid):** It's getting a bit crowded in the lower mid-range. EQ this area slightly on your synth.",
        "sub_warn": "**SUB-COLLISION:** Chord notes in the Sub area. This fights with your Kick/808.",
        "clean_mix": "**MIX IS CLEAN:** Good frequency distribution found.",
        "advice_title": "### 🤖 AI Co-Producer: Dynamic Studio Advice",
        "hiphop_tips": [
            "**The Boom-Bap Bass:** Because you are in **{scale}**, play your bassline mostly around the **{root_note}**. Tip: Slide up briefly at the end of the 4th bar.",
            "**Lo-Fi Pocket:** Your tempo is {tempo} BPM. Try to drop the bassline just a few milliseconds after the kick for a heavily dragging, laid-back groove.",
            "**Melodic Variation:** Use the 5th note in your **{scale}** scale as a 'springboard' just before returning to your **{root_note}** bass note."
        ],
        "trap_tips": [
            "**The 808 Bounce:** Put a hard 808 on the **{root_note}**. Since it's **{scale}**, it sounds incredibly strong if you place fast accents on the off-beats.",
            "**808 Glide:** Start on the **{root_note}** and draw a fast 808-slide an octave higher, exactly right before the snare hits on the 3rd beat.",
            "**Syncopated Drop:** Rest your 808 on the first beat when the chord changes. Drop in on the 'and' of the 1. This gives your beat a huge unexpected bounce."
        ],
        "rb_tips": [
            "**The Soulful Sub:** Start on **{root_note}**, but don't just hover there. Walk down the **{scale}** slowly towards the next beat.",
            "**Neo-Soul Timing:** Play your bass extremely soft and just a bit late behind the beat (D'Angelo style). This fits perfectly with the {tempo} BPM tempo.",
            "**R&B Arp Bass:** Pluck the high notes from your **{root_note}** chord and play them one by one in the bass register as a slow, sultry bass arpeggio."
        ],
        "export_title": "### 🎹 Export MIDI Starters",
        "btn_bass": "🎸 Download Bassline",
        "btn_drums": "📦 Download Drum Stems",
        "btn_melody": "🎹 Download Melody"
    }
}
# --- FUNCTIE 1: FREQUENTIE DATA ---
def get_note_name(midi_number):
    # Lijst van alle 12 muzieknoten
    NOTES = ['C', 'C#', 'D', 'D#', 'E', 'F', 'F#', 'G', 'G#', 'A', 'A#', 'B']
    return NOTES[midi_number % 12]

def get_frequency_data(notes):
    freqs = [440 * (2**((n - 69) / 12)) for n in notes]
    data = {
        "1. Sub (0-60Hz)": 0, "2. Bass (60-250Hz)": 0,
        "3. Low-Mid (250-500Hz)": 0, "4. Mid (500-2kHz)": 0,
        "5. High-Mid (2k-4kHz)": 0, "6. High (4kHz+)": 0
    }
    for f in freqs:
        if f < 60: data["1. Sub (0-60Hz)"] += 1
        elif f < 250: data["2. Bass (60-250Hz)"] += 1
        elif f < 500: data["3. Low-Mid (250-500Hz)"] += 1
        elif f < 2000: data["4. Mid (500-2kHz)"] += 1
        elif f < 4000: data["5. High-Mid (2k-4kHz)"] += 1
        else: data["6. High (4kHz+)"] += 1
    return pd.DataFrame(list(data.items()), columns=['Gebied', 'Aantal Noten'])

# --- FUNCTIE 2: ANALYSE ENGINE ---
def analyze_midi_deep(uploaded_file):
    try:
        uploaded_file.seek(0)
        mid = mido.MidiFile(file=io.BytesIO(uploaded_file.read()))
        notes = []
        tempo = 120 
        for track in mid.tracks:
            for msg in track:
                if msg.type == 'set_tempo':
                    tempo = mido.tempo2bpm(msg.tempo)
                if msg.type == 'note_on' and msg.velocity > 0:
                    notes.append(msg.note)
        if not notes: return None

        avg_note = sum(notes) / len(notes)
        unique_notes = sorted(list(set([n % 12 for n in notes])))
        root = unique_notes[0]
        root_name = get_note_name(root) # Hier leert PA de naam van het akkoord
        intervals = [(n - root) % 12 for n in unique_notes]

       # --- NIEUW: GEAVANCEERDE TOONLADDER DETECTIE ---
        scale_type = "Complex / Onbekend"
        if 3 in intervals: # Mineur basis
            if 11 in intervals: scale_type = "Harmonisch Mineur"
            elif 9 in intervals and 10 in intervals: scale_type = "Dorisch"
            else: scale_type = "Natuurlijk Mineur"
            vibe_type = "Mineur"
        elif 4 in intervals: # Majeur basis
            if 10 in intervals: scale_type = "Mixolydisch"
            else: scale_type = "Majeur"
            vibe_type = "Majeur"
        else:
            vibe_type = "Complex"

        register = "Laag" if avg_note < 50 else "Midden" if avg_note < 70 else "Hoog"

        return {
            "tempo": round(tempo, 1),
            "register": register,
            "vibe": vibe_type,
            "scale": scale_type, # De exacte toonladder wordt nu onthouden
            "notes": notes,
            "notes_count": len(notes),
            "root_name": root_name,
            "root_number": root
        }
    except Exception as e:
        return None

# --- FUNCTIE 3 & 4: PRO MIDI SEQUENCERS (4 BARS) ---
def schrijf_midi_events(events):
    # Een slimme 'engine' om overlappende noten naar MIDI delta-tijd om te zetten
    mid = mido.MidiFile()
    track = mido.MidiTrack()
    mid.tracks.append(track)
    events.sort(key=lambda x: x['time'])
    last_time = 0
    for e in events:
        delta = e['time'] - last_time
        track.append(mido.Message(e['type'], note=e['note'], velocity=e['velocity'], time=delta, channel=e.get('channel', 0)))
        last_time = e['time']
    file_buffer = io.BytesIO()
    mid.save(file=file_buffer)
    return file_buffer.getvalue()

def add_hit(events, note, beat, duration_beats=0.25, velocity=100, channel=0, swing_amount=0):
    # --- NIEUW: HUMANIZE ENGINE ---
    shift = 0
    if swing_amount > 0:
        # Verschuif de timing een fractie (hoe hoger de swing, hoe losser)
        max_shift = (swing_amount / 100.0) * 0.06 
        shift = random.uniform(-max_shift, max_shift)
        
        # Varieer de aanslagkracht (velocity) voor een menselijk gevoel
        vel_var = int((swing_amount / 100.0) * 20)
        velocity = max(1, min(127, velocity + random.randint(-vel_var, vel_var)))

    abs_time = int(max(0, beat + shift) * 480)
    duration = int(duration_beats * 480)
    
    events.append({'time': abs_time, 'type': 'note_on', 'note': note, 'velocity': velocity, 'channel': channel})
    events.append({'time': abs_time + duration, 'type': 'note_off', 'note': note, 'velocity': 0, 'channel': channel})

def generate_bassline_midi(root_number, genre, swing_amount):
    events = []
    b = 36 + (root_number % 12) 
    
    for bar in range(4):
        offset = bar * 4 
        if genre == "Trap":
            add_hit(events, b, offset + 0, 1.0, 127, 0, swing_amount) 
            add_hit(events, b, offset + 1.5, 0.5, 120, 0, swing_amount) 
            if bar == 3: add_hit(events, b + 12, offset + 3.5, 0.5, 120, 0, swing_amount) 
            elif bar % 2 == 1: add_hit(events, b, offset + 3.5, 0.5, 110, 0, swing_amount)
        elif genre == "Hiphop":
            add_hit(events, b, offset + 0, 1.5, 110, 0, swing_amount)
            add_hit(events, b, offset + 2.5, 1.0, 100, 0, swing_amount) 
            if bar == 3: add_hit(events, b + 7, offset + 3.5, 0.5, 90, 0, swing_amount) 
        else: 
            add_hit(events, b, offset + 0, 3.0, 100, 0, swing_amount) 
            if bar == 3: 
                add_hit(events, b - 1, offset + 3.0, 0.5, 90, 0, swing_amount) 
                add_hit(events, b - 2, offset + 3.5, 0.5, 80, 0, swing_amount)
    return schrijf_midi_events(events)

def generate_drum_zip(genre, complexity, swing_amount):
    events = []
    k, s, h, rim = 36, 38, 42, 37 
    
    for bar in range(4):
        offset = bar * 4
        
        # COMPLEXITY: Basic heeft GEEN hihats, Modern heeft standaard, Busy heeft rolls
        is_basic = "Basic" in complexity
        is_busy = "Busy" in complexity
        
        if genre == "Trap":
            if not is_basic:
                for i in range(8):
                    beat_pos = offset + (i * 0.5)
                    if is_busy and i % 2 == 1 and random.random() > 0.6:
                        add_hit(events, h, beat_pos, 0.1, 110, 9, swing_amount)
                        add_hit(events, h, beat_pos + 0.166, 0.1, 90, 9, swing_amount)
                        add_hit(events, h, beat_pos + 0.333, 0.1, 80, 9, swing_amount)
                    else:
                        add_hit(events, h, beat_pos, 0.1, 100, 9, swing_amount)

            add_hit(events, k, offset + 0, velocity=127, channel=9, swing_amount=swing_amount)
            add_hit(events, s, offset + 2, velocity=127, channel=9, swing_amount=swing_amount) 
            
            if not is_basic: add_hit(events, k, offset + 1.5, velocity=115, channel=9, swing_amount=swing_amount)
            if is_busy and bar % 2 == 1: add_hit(events, k, offset + 3.5, velocity=110, channel=9, swing_amount=swing_amount)
                
        elif genre == "Hiphop":
            if not is_basic:
                for i in range(8): 
                    vel = 95 if i % 2 == 0 else 65
                    add_hit(events, h, offset + (i * 0.5), 0.1, vel, 9, swing_amount)
            
            add_hit(events, k, offset + 0, velocity=110, channel=9, swing_amount=swing_amount)
            add_hit(events, s, offset + 1, velocity=110, channel=9, swing_amount=swing_amount) 
            add_hit(events, s, offset + 3, velocity=110, channel=9, swing_amount=swing_amount)
            
            if not is_basic: add_hit(events, k, offset + 2.5, velocity=90, channel=9, swing_amount=swing_amount)
            
            if is_busy:
                add_hit(events, s, offset + 1.75, velocity=45, channel=9, swing_amount=swing_amount) 
                if bar % 2 == 1:
                    add_hit(events, s, offset + 3.75, velocity=55, channel=9, swing_amount=swing_amount)
                    add_hit(events, k, offset + 3.5, velocity=70, channel=9, swing_amount=swing_amount)
                
        else: # R&B
            if not is_basic:
                for i in range(16): 
                    vel = 85 if i % 4 == 0 else (65 if i % 2 == 0 else 45)
                    add_hit(events, h, offset + (i * 0.25), 0.1, vel, 9, swing_amount)
            
            add_hit(events, k, offset + 0, velocity=100, channel=9, swing_amount=swing_amount)
            add_hit(events, rim, offset + 1, velocity=115, channel=9, swing_amount=swing_amount)
            add_hit(events, rim, offset + 3, velocity=115, channel=9, swing_amount=swing_amount)
            
            if not is_basic: add_hit(events, k, offset + 1.75, velocity=85, channel=9, swing_amount=swing_amount) 
            
            if is_busy:
                add_hit(events, rim, offset + 2.75, velocity=40, channel=9, swing_amount=swing_amount) 
                if bar == 3: add_hit(events, k, offset + 3.5, velocity=60, channel=9, swing_amount=swing_amount)

    events_kick = [e for e in events if e['note'] == k]
    events_snare = [e for e in events if e['note'] in (s, rim)]
    events_hihat = [e for e in events if e['note'] == h]
    
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        zip_file.writestr("1_PA_Kick.mid", schrijf_midi_events(events_kick))
        zip_file.writestr("2_PA_Snare.mid", schrijf_midi_events(events_snare))
        zip_file.writestr("3_PA_Hihats.mid", schrijf_midi_events(events_hihat))
        zip_file.writestr("4_PA_Full_Groove.mid", schrijf_midi_events(events)) 
        
    return zip_buffer.getvalue()

def generate_melody_midi(root_number, scale_type, genre, swing_amount):
    events = []
    # Zet de melodie in een hoger octaaf (octaaf 5, rond MIDI noot 72)
    base_note = 60 + (root_number % 12) 
    
    # Bepaal de veilige afstanden (intervallen) op basis van de ontdekte toonladder
    intervals = [0, 2, 4, 5, 7, 9, 11] # Standaard Majeur
    if "Mineur" in scale_type:
        if "Harmonisch" in scale_type: intervals = [0, 2, 3, 5, 7, 8, 11]
        else: intervals = [0, 2, 3, 5, 7, 8, 10] # Natuurlijk Mineur
    elif scale_type == "Dorisch": intervals = [0, 2, 3, 5, 7, 9, 10]
    elif scale_type == "Mixolydisch": intervals = [0, 2, 4, 5, 7, 9, 10]
    
    # Genereer een lijst met 100% zuivere noten
    safe_notes = [base_note + i for i in intervals]
    
    for bar in range(4):
        offset = bar * 4
        
        if genre == "Trap":
            # Snelle, repetitieve hoge melodie (plucks/bells)
            for i in range(8):
                if random.random() > 0.4: # 60% kans op een noot
                    # Kies willekeurig de grondtoon, de terts of de kwint
                    note = random.choice([safe_notes[0], safe_notes[2], safe_notes[4], safe_notes[0]+12])
                    # Zet hem nog een octaaf hoger (+12) voor die Trap bell vibe
                    add_hit(events, note + 12, offset + (i * 0.5), 0.25, random.randint(90, 110), 0, swing_amount)
                    
        elif genre == "Hiphop":
            # Meer jazzy, gesyncopeerde timing met meer ademruimte
            if random.random() > 0.3: add_hit(events, safe_notes[0], offset + 0, 0.5, 100, 0, swing_amount)
            if random.random() > 0.5: add_hit(events, safe_notes[2], offset + 1.5, 0.5, 90, 0, swing_amount)
            if random.random() > 0.3: add_hit(events, safe_notes[4], offset + 2.5, 0.5, 95, 0, swing_amount)
            if bar % 2 == 1: add_hit(events, safe_notes[6] - 12, offset + 3.5, 0.5, 80, 0, swing_amount) # Jazzy loopje
                
        else: # R&B
            # Gladde, langzame arpeggio's die door de akkoorden heen rollen
            add_hit(events, safe_notes[0], offset + 0, 1.0, 90, 0, swing_amount)
            add_hit(events, safe_notes[2], offset + 1.0, 1.0, 85, 0, swing_amount)
            add_hit(events, safe_notes[4], offset + 2.0, 1.0, 80, 0, swing_amount)
            add_hit(events, safe_notes[0]+12, offset + 3.0, 1.0, 75, 0, swing_amount) # Octaaf sprong omhoog

    return schrijf_midi_events(events)

 
# --- INTERFACE CONFIGURATIE (De nieuwe UX) ---
st.set_page_config(page_title="PA | Producer Adviser", page_icon="🎧", layout="wide", initial_sidebar_state="expanded")
# Custom CSS voor de "Dark Mode VST-vibe"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)


# Sidebar
# --- SIDEBAR & TAALKEUZE ---
try:
    st.sidebar.image("logo.png", use_container_width=True)
except:
    st.sidebar.markdown("# 🎧 PA")

lang_choice = st.sidebar.radio("Language / Taal", ["EN", "NL"], horizontal=True)
T = LANGUAGES[lang_choice] 

st.sidebar.markdown(T["sidebar_title"])
st.sidebar.divider()

st.sidebar.markdown(T["gen_settings"])
genre = st.sidebar.selectbox(T["choose_genre"], ["Hiphop", "R&B", "Trap"])

# HIER ZIJN ZE WEER: De missende variabelen!
complexity = st.sidebar.selectbox(T["complexity"], ["Basic", "Modern", "Busy"], index=1)
swing_amount = st.sidebar.slider(T["swing"], min_value=0, max_value=100, value=20, step=5)

st.sidebar.divider()
st.sidebar.markdown("### 🧪 Beta Tester?")
st.sidebar.link_button(T["feedback_btn"], "https://forms.gle/hfFYLywgzZYjzKDGA")
# Hoofdscherm
st.title("🎹 PA: Producer Adviser")

uploaded_file = st.file_uploader(T["drop_midi"], type=['mid'])

if not uploaded_file:
    st.divider()
    st.markdown(f"### 🚀 {T['how_it_works']}")
    
    col1, col2, col3 = st.columns(3)
    col1.info(T["step1"])
    col2.warning(T["step2"])
    col3.success(T["step3"])

# --- START ANALYSE (Als er wél iets is geüpload) ---
if uploaded_file:
    data = analyze_midi_deep(uploaded_file)
    
    if data:
        st.markdown(T["analysis_title"])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("BPM", data['tempo'])
        m2.metric("Register", data['register']) 
        m3.metric(T["metric_scale"], f"{data['root_name']} {data['scale']}")
        m4.metric(T["metric_notes"], data['notes_count'])

        st.divider()
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown(T["chart_title"])
            chart_df = get_frequency_data(data['notes'])
            st.line_chart(chart_df.set_index('Gebied'), color="#00d1ff")

        with col_right:
            st.markdown(T["collision_title"])
            low_mid_val = chart_df.loc[chart_df['Gebied'] == '3. Low-Mid (250-500Hz)', 'Aantal Noten'].values[0]
            sub_bass_val = chart_df.loc[chart_df['Gebied'] == '1. Sub (0-60Hz)', 'Aantal Noten'].values[0]

            if low_mid_val >= 5:
                st.error(T["mud_alarm"].format(low_mid_val))
            elif low_mid_val == 4:
                st.warning(T["low_mid_warn"])
            elif sub_bass_val >= 1:
                st.warning(T["sub_warn"])
            else:
                st.success(T["clean_mix"])
            
        st.divider()
        st.markdown(T["advice_title"])
        
        root_note = data['root_name']
        scale = data['scale']
        tempo = data['tempo']
        
        # --- DYNAMISCHE AI TIPS ---
        if genre == "Hiphop":
            tips = [tip.format(scale=scale, root_note=root_note, tempo=tempo) for tip in T["hiphop_tips"]]
            st.info(random.choice(tips))
            
        elif genre == "Trap":
            tips = [tip.format(scale=scale, root_note=root_note, tempo=tempo) for tip in T["trap_tips"]]
            st.error(random.choice(tips))
            
        elif genre == "R&B":
            tips = [tip.format(scale=scale, root_note=root_note, tempo=tempo) for tip in T["rb_tips"]]
            st.success(random.choice(tips))

        # --- DE MAGIC BUTTONS: EXPORTEER MIDI ---
        st.divider()
        st.write(T["export_title"])
        
        btn1, btn2, btn3 = st.columns(3)
        
        with btn1:
            bass_midi_bytes = generate_bassline_midi(data['root_number'], genre, swing_amount)
            st.download_button(
                label=T["btn_bass"],
                data=bass_midi_bytes,
                file_name=f"PA_Bass_{genre}_{root_note}.mid",
                mime="audio/midi",
                use_container_width=True
            )
            
        with btn2:
            drum_zip_bytes = generate_drum_zip(genre, complexity, swing_amount)
            st.download_button(
                label=T["btn_drums"],
                data=drum_zip_bytes,
                file_name=f"PA_Drum_Stems_{genre}.zip",
                mime="application/zip",
                use_container_width=True
            )
            
        with btn3:
            melody_midi_bytes = generate_melody_midi(data['root_number'], scale, genre, swing_amount)
            st.download_button(
                label=T["btn_melody"],
                data=melody_midi_bytes,
                file_name=f"PA_Melody_{genre}_{scale}.mid",
                mime="audio/midi",
                use_container_width=True
            )
