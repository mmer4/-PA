import streamlit as st
import mido
import io
import pandas as pd
import random
import zipfile

# TAALINSTELLINGEN

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
#  FREQUENTIE DATA 
def get_note_name(midi_number):
    
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

# ANALYSE ENGINE
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

       # GEAVANCEERDE TOONLADDER DETECTIE
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
            "scale": scale_type, 
            "notes": notes,
            "notes_count": len(notes),
            "root_name": root_name,
            "root_number": root
        }
    except Exception as e:
        return None

# PRO MIDI SEQUENCERS (4 BARS)
def schrijf_midi_events(events):
   
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
    # HUMANIZE ENGINE 
    shift = 0
    if swing_amount > 0:
        
        max_shift = (swing_amount / 100.0) * 0.06 
        shift = random.uniform(-max_shift, max_shift)
        
      
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
            # LEGATO FIX
    
            add_hit(events, b, offset + 0, 1.5, 127, 0, swing_amount) 
            
            add_hit(events, b, offset + 1.5, 2.0, 120, 0, swing_amount) 
            
            
            if bar == 3: 
                add_hit(events, b + 12, offset + 3.5, 0.5, 120, 0, swing_amount) 
            elif bar % 2 == 1: 
                add_hit(events, b, offset + 3.5, 0.5, 110, 0, swing_amount)
                
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
        
        is_basic = "Basic" in complexity
        is_busy = "Busy" in complexity
        
        if genre == "Trap":
            if not is_basic:
                for i in range(8):
                    beat_pos = offset + (i * 0.5)
                    if is_busy and i % 2 == 1 and random.random() > 0.6:
                        # MATH FIX
                        add_hit(events, h, beat_pos, 0.1, 110, 9, swing_amount)
                        add_hit(events, h, beat_pos + (1/6), 0.1, 90, 9, swing_amount)
                        add_hit(events, h, beat_pos + (1/3), 0.1, 80, 9, swing_amount)
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
                
        else: 
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
    
    base_note = 60 + (root_number % 12) 
    
    
    intervals = [0, 2, 4, 5, 7, 9, 11] 
    if "Mineur" in scale_type:
        if "Harmonisch" in scale_type: intervals = [0, 2, 3, 5, 7, 8, 11]
        else: intervals = [0, 2, 3, 5, 7, 8, 10] 
    elif scale_type == "Dorisch": intervals = [0, 2, 3, 5, 7, 9, 10]
    elif scale_type == "Mixolydisch": intervals = [0, 2, 4, 5, 7, 9, 10]
    
    
    safe_notes = [base_note + i for i in intervals]
    
    for bar in range(4):
        offset = bar * 4
        
        if genre == "Trap":
            
            for i in range(8):
                if random.random() > 0.4: 
                    note = random.choice([safe_notes[0], safe_notes[2], safe_notes[4], safe_notes[0]+12])
                    # LEGATO FIX: Lengte veranderd van 0.25 naar 0.5. 
                
                    add_hit(events, note + 12, offset + (i * 0.5), 0.5, random.randint(90, 110), 0, swing_amount)
                    
        elif genre == "Hiphop":
            # LEGATO FIX: Lengtes opgerekt (1.5, 1.0, 1.0) zodat ze exact aansluiten 
            # op het moment dat de volgende noot kán vallen. Geen onverwachte stiltes meer.
            if random.random() > 0.3: add_hit(events, safe_notes[0], offset + 0, 1.5, 100, 0, swing_amount)
            if random.random() > 0.5: add_hit(events, safe_notes[2], offset + 1.5, 1.0, 90, 0, swing_amount)
            if random.random() > 0.3: add_hit(events, safe_notes[4], offset + 2.5, 1.0, 95, 0, swing_amount)
            if bar % 2 == 1: add_hit(events, safe_notes[6] - 12, offset + 3.5, 0.5, 80, 0, swing_amount) 
                
        else: # R&B
            add_hit(events, safe_notes[0], offset + 0, 1.0, 90, 0, swing_amount)
            add_hit(events, safe_notes[2], offset + 1.0, 1.0, 85, 0, swing_amount)
            add_hit(events, safe_notes[4], offset + 2.0, 1.0, 80, 0, swing_amount)
            add_hit(events, safe_notes[0]+12, offset + 3.0, 1.0, 75, 0, swing_amount) 

    return schrijf_midi_events(events)

 
# --- INTERFACE CONFIGURATIE (De nieuwe UX) ---
st.set_page_config(page_title="PA | AI Co-Producer", layout="wide", page_icon="🎹")

# Custom CSS voor een "Studio" vibe
st.markdown("""
    <style>
    /* Maak de achtergrond donkerder (als de gebruiker dark-mode heeft) */
    .stApp {
        font-family: 'Inter', sans-serif;
    }
    
    /* Grote, sexy Hero Titel */
    .hero-title {
        font-size: 3.5rem !important;
        font-weight: 800;
        background: -webkit-linear-gradient(45deg, #FF4B4B, #FF904B);
        -webkit-background-clip: text;
        -webkit-text-fill-color: transparent;
        margin-bottom: 0px !important;
        padding-bottom: 0px !important;
    }
    
    /* Subtitel styling */
    .hero-subtitle {
        font-size: 1.2rem;
        color: #888888;
        margin-top: 0px !important;
        padding-top: 0px !important;
        margin-bottom: 30px;
    }
    </style>
""", unsafe_allow_html=True)



#  SIDEBAR & TAALKEUZE 
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


complexity = st.sidebar.selectbox(T["complexity"], ["Basic", "Modern", "Busy"], index=1)
swing_amount = st.sidebar.slider(T["swing"], min_value=0, max_value=100, value=20, step=5)

st.sidebar.divider()
st.sidebar.markdown("### 🧪 Beta Tester?")
st.sidebar.link_button(T["feedback_btn"], "https://forms.gle/hfFYLywgzZYjzKDGA")
# Hoofdscherm
st.markdown('<h1 class="hero-title">Producer Adviser</h1>', unsafe_allow_html=True)

if lang_choice == "NL":
    st.markdown('<p class="hero-subtitle">Jouw AI-gedreven co-producer. Upload je akkoorden en ontgrendel wiskundig perfecte baslijnen en drums.</p>', unsafe_allow_html=True)
else:
    st.markdown('<p class="hero-subtitle">Your AI-driven co-producer. Upload your chords and unlock mathematically perfect basslines and drums.</p>', unsafe_allow_html=True)

st.divider()

#  Upload Sectie 
st.markdown(f"### 📥 {T['drop_midi']}")
uploaded_file = st.file_uploader("", type=['mid'], key="midi_upload")

if not uploaded_file:
   
    st.write("")
    st.write("")
    
    col_left, col_center, col_right = st.columns([1, 2, 1])
    
    with col_center:
        st.info(f"🚀 **{T['how_it_works']}**")
        st.markdown(f"""
        1️⃣ **{T['step1']}**  
        2️⃣ **{T['step2']}**  
        3️⃣ **{T['step3']}**
        """)
# START ANALYSE 
if uploaded_file:
    data = analyze_midi_deep(uploaded_file)
    
    if data:
        
        display_reg = data['register']
        display_scale = data['scale']
        
        if lang_choice == "EN":
            dict_reg = {"Laag": "Low", "Midden": "Mid", "Hoog": "High"}
            dict_scale = {
                "Harmonisch Mineur": "Harmonic Minor",
                "Dorisch": "Dorian",
                "Natuurlijk Mineur": "Natural Minor",
                "Mixolydisch": "Mixolydian",
                "Majeur": "Major",
                "Complex / Onbekend": "Complex / Unknown"
            }
            display_reg = dict_reg.get(display_reg, display_reg)
            display_scale = dict_scale.get(display_scale, display_scale)

        st.markdown(T["analysis_title"])
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("BPM", data['tempo'])
        m2.metric("Register", display_reg) 
        m3.metric(T["metric_scale"], f"{data['root_name']} {display_scale}")
        m4.metric(T["metric_notes"], data['notes_count'])
#  OVERRIDE MENU VOOR DE CONTROL FREAKS 
        with st.expander("⚙️ Override AI Analyse (Handmatig Aanpassen)"):
            c1, c2, c3 = st.columns(3)
            
            # 1. Snelheid Override
            try:
                huidig_tempo = int(data['tempo'])
            except:
                huidig_tempo = 120
            manual_bpm = c1.number_input("Snelheid (BPM)", min_value=40, max_value=250, value=huidig_tempo)
            
            # 2. Grondtoon Override
            noten_lijst = ["C", "C#", "D", "D#", "E", "F", "F#", "G", "G#", "A", "A#", "B"]
            huidige_noot_index = noten_lijst.index(data['root_name']) if data['root_name'] in noten_lijst else 0
            manual_root = c2.selectbox("Grondtoon", noten_lijst, index=huidige_noot_index)
            
            # 3. Toonladder Override
            toonladders = ["Majeur", "Natuurlijk Mineur", "Harmonisch Mineur", "Dorisch", "Mixolydisch"]
            huidige_ladder_index = toonladders.index(data['scale']) if data['scale'] in toonladders else 0
            manual_scale = c3.selectbox("Toonladder", toonladders, index=huidige_ladder_index)

           
            data['tempo'] = manual_bpm
            data['root_name'] = manual_root
            data['root_number'] = noten_lijst.index(manual_root)
            data['scale'] = manual_scale
            
           
            display_scale = manual_scale
            if lang_choice == "EN":
                dict_scale = {
                    "Harmonisch Mineur": "Harmonic Minor",
                    "Dorisch": "Dorian",
                    "Natuurlijk Mineur": "Natural Minor",
                    "Mixolydisch": "Mixolydian",
                    "Majeur": "Major",
                    "Complex / Onbekend": "Complex / Unknown"
                }
                display_scale = dict_scale.get(manual_scale, manual_scale)
#  🤖 AI UITLEG: TOONSOORTEN 
        with st.expander("🤖 AI Uitleg: Wat betekent deze Toonladder?"):
            if lang_choice == "NL":
                st.write(f"Je akkoorden staan in **{display_scale}**.")
                if "Majeur" in display_scale:
                    st.info("💡 **Vibe:** Vrolijk, hoopvol en energiek. Veel pop, house en vrolijke hiphop (denk aan Mac Miller) gebruikt deze toonladder.")
                elif "Mineur" in display_scale:
                    st.info("💡 **Vibe:** Droevig, donker, of emotioneel. Dit is de gouden standaard voor Trap, Drill en melancholische R&B.")
                elif "Dorisch" in display_scale:
                    st.info("💡 **Vibe:** Dromerig en jazzy. Het lijkt op mineur, maar heeft één noot die het net wat lichter en zwevender maakt.")
                else:
                    st.info("💡 **Vibe:** Een unieke of exotische klankkleur. Probeer hierboven handmatig een andere toonsoort te kiezen als je melodieën wilt forceren.")
            else: # Engels
                st.write(f"Your chords are in **{display_scale}**.")
                if "Major" in display_scale:
                    st.info("💡 **Vibe:** Happy, hopeful, and energetic. A lot of pop, house, and upbeat hip-hop use this scale.")
                elif "Minor" in display_scale:
                    st.info("💡 **Vibe:** Sad, dark, or emotional. This is the gold standard for Trap, Drill, and melancholic R&B.")
                elif "Dorian" in display_scale:
                    st.info("💡 **Vibe:** Dreamy and jazzy. It's like minor but with a slightly brighter, floating feel.")
                else:
                    st.info("💡 **Vibe:** A unique or exotic tone. Try manually overriding the scale above if you want to experiment with melodies.")
        
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
                #  🤖 AI UITLEG: FREQUENTIES 
            with st.expander("🤖 AI Uitleg: Frequenties & Modder"):
                if lang_choice == "NL":
                    st.write("**Waarom checken we op 'Modder'?**")
                    st.write("Geluid is ruimte. Tussen de **250Hz en 500Hz** (het 'Low-Mid' gebied) klinkt audio heel dik en warm. Maar als je baslijn, je akkoorden én je kick-drum allemaal in datzelfde gebied spelen, ontstaat er 'frequentie-file'.")
                    st.info("🔧 **Pro-Tip:** Hoor je een modderige mix? Pak een EQ-plugin in je DAW en haal bij je akkoorden-synth een paar decibel weg rond de 300Hz. Je zult horen dat je kickdrum opeens veel harder doorkomt!")
                else:
                    st.write("**Why do we check for 'Mud'?**")
                    st.write("Sound is space. Between **250Hz and 500Hz** (the 'Low-Mid' area), audio sounds thick and warm. But if your bassline, your chords, and your kick drum all play in that same area, you get a 'frequency traffic jam'.")
                    st.info("🔧 **Pro-Tip:** Got a muddy mix? Put an EQ plugin on your chord synth and cut a few decibels around 300Hz. You'll hear your kick drum suddenly punch through a lot harder!")
            
        st.divider()
        st.markdown(T["advice_title"])
        
        root_note = data['root_name']
        tempo = data['tempo']
        
        #  DYNAMISCHE AI TIPS 
        if genre == "Hiphop":
            tips = [tip.format(scale=display_scale, root_note=root_note, tempo=tempo) for tip in T["hiphop_tips"]]
            st.info(random.choice(tips))
            
        elif genre == "Trap":
            tips = [tip.format(scale=display_scale, root_note=root_note, tempo=tempo) for tip in T["trap_tips"]]
            st.error(random.choice(tips))
            
        elif genre == "R&B":
            tips = [tip.format(scale=display_scale, root_note=root_note, tempo=tempo) for tip in T["rb_tips"]]
            st.success(random.choice(tips))

        #  EXPORTEER MIDI
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
          
            melody_midi_bytes = generate_melody_midi(data['root_number'], data['scale'], genre, swing_amount)
            st.download_button(
                label=T["btn_melody"],
                data=melody_midi_bytes,
                file_name=f"PA_Melody_{genre}_{display_scale}.mid",
                mime="audio/midi",
                use_container_width=True
            )
