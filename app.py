import streamlit as st
import mido
import io
import pandas as pd
import random
import zipfile

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

def add_hit(events, note, beat, duration_beats=0.25, velocity=100, channel=0):
    # 480 ticks = 1 kwartnoot (beat)
    abs_time = int(beat * 480)
    duration = int(duration_beats * 480)
    events.append({'time': abs_time, 'type': 'note_on', 'note': note, 'velocity': velocity, 'channel': channel})
    events.append({'time': abs_time + duration, 'type': 'note_off', 'note': note, 'velocity': 0, 'channel': channel})

def generate_bassline_midi(root_number, genre):
    events = []
    b = 36 + (root_number % 12) # Bas in het lage octaaf
    
    for bar in range(4):
        offset = bar * 4 # 4 beats per maat
        if genre == "Trap":
            add_hit(events, b, offset + 0, 1.0, 127) # Hard op de 1
            add_hit(events, b, offset + 1.5, 0.5, 120) # De off-beat bounce
            if bar == 3: 
                add_hit(events, b + 12, offset + 3.5, 0.5, 120) # 808 Slide Up aan het eind!
            elif bar % 2 == 1:
                add_hit(events, b, offset + 3.5, 0.5, 110)
        elif genre == "Hiphop":
            add_hit(events, b, offset + 0, 1.5, 110)
            add_hit(events, b, offset + 2.5, 1.0, 100) # Syncopatie
            if bar == 3: add_hit(events, b + 7, offset + 3.5, 0.5, 90) # Een 'kwint' wandeling
        else: # R&B
            add_hit(events, b, offset + 0, 3.0, 100) # Lange, zwoele basnoot
            if bar == 3: 
                add_hit(events, b - 1, offset + 3.0, 0.5, 90) # Walkdown
                add_hit(events, b - 2, offset + 3.5, 0.5, 80)
    return schrijf_midi_events(events)

def generate_drum_zip(genre):
    events = []
    k, s, h, rim = 36, 38, 42, 37 # Kick, Snare, Hihat, Rimshot
    
    for bar in range(4):
        offset = bar * 4
        
        if genre == "Trap":
            for i in range(8):
                beat_pos = offset + (i * 0.5)
                if i % 2 == 1 and random.random() > 0.7:
                    add_hit(events, h, beat_pos, 0.1, 110, channel=9)
                    add_hit(events, h, beat_pos + 0.166, 0.1, 90, channel=9)
                    add_hit(events, h, beat_pos + 0.333, 0.1, 80, channel=9)
                else:
                    add_hit(events, h, beat_pos, 0.1, 100, channel=9)

            add_hit(events, k, offset + 0, velocity=127, channel=9)
            add_hit(events, k, offset + 1.5, velocity=115, channel=9)
            if bar % 2 == 1: add_hit(events, k, offset + 3.5, velocity=110, channel=9)
            add_hit(events, s, offset + 2, velocity=127, channel=9) 
                
        elif genre == "Hiphop":
            for i in range(8): 
                vel = 95 if i % 2 == 0 else 65
                add_hit(events, h, offset + (i * 0.5), 0.1, vel, channel=9)
            
            add_hit(events, k, offset + 0, velocity=110, channel=9)
            add_hit(events, k, offset + 2.5, velocity=90, channel=9)
            
            add_hit(events, s, offset + 1, velocity=110, channel=9) 
            add_hit(events, s, offset + 3, velocity=110, channel=9)
            
            add_hit(events, s, offset + 1.75, velocity=45, channel=9) 
            if bar % 2 == 1:
                add_hit(events, s, offset + 3.75, velocity=55, channel=9)
                add_hit(events, k, offset + 3.5, velocity=70, channel=9)
                
        else:
            for i in range(16): 
                vel = 85 if i % 4 == 0 else (65 if i % 2 == 0 else 45)
                add_hit(events, h, offset + (i * 0.25), 0.1, vel, channel=9)
            
            add_hit(events, k, offset + 0, velocity=100, channel=9)
            add_hit(events, k, offset + 1.75, velocity=85, channel=9) 
            
            add_hit(events, rim, offset + 1, velocity=115, channel=9)
            add_hit(events, rim, offset + 3, velocity=115, channel=9)
            
            add_hit(events, rim, offset + 2.75, velocity=40, channel=9) 
            if bar == 3:
                add_hit(events, k, offset + 3.5, velocity=60, channel=9)
                    
    # --- NIEUW: SPLIT DE NOTEN IN APARTE SPOREN ---
    events_kick = [e for e in events if e['note'] == k]
    events_snare = [e for e in events if e['note'] in (s, rim)]
    events_hihat = [e for e in events if e['note'] == h]
    
    # --- NIEUW: MAAK EEN ZIP BESTAND ---
    zip_buffer = io.BytesIO()
    with zipfile.ZipFile(zip_buffer, "a", zipfile.ZIP_DEFLATED, False) as zip_file:
        # We schrijven 4 losse MIDI bestanden in de ZIP map
        zip_file.writestr("1_PA_Kick.mid", schrijf_midi_events(events_kick))
        zip_file.writestr("2_PA_Snare.mid", schrijf_midi_events(events_snare))
        zip_file.writestr("3_PA_Hihats.mid", schrijf_midi_events(events_hihat))
        zip_file.writestr("4_PA_Full_Groove.mid", schrijf_midi_events(events)) # Alles bij elkaar
        
    return zip_buffer.getvalue()
 
# --- INTERFACE CONFIGURATIE (De nieuwe UX) ---
st.set_page_config(page_title="PA | Producer Adviser", layout="wide", initial_sidebar_state="expanded")

# Custom CSS voor de "Dark Mode VST-vibe"
st.markdown("""
    <style>
    .main { background-color: #0e1117; }
    .stMetric { background-color: #1f2937; padding: 15px; border-radius: 10px; border: 1px solid #374151; }
    </style>
    """, unsafe_allow_html=True)

# Sidebar
st.sidebar.markdown("# 🎧 PA")
st.sidebar.markdown("### *Producer Adviser v1.0*")
st.sidebar.divider()
genre = st.sidebar.selectbox("Kies je Genre", ["Hiphop", "R&B", "Trap"])

# Hoofdscherm
st.title("🎹 PA: Producer Adviser")
st.write(f"Sla de brug tussen creativiteit en techniek in **{genre}**.")

uploaded_file = st.file_uploader("Drop je MIDI-file hier", type=['mid'])

if uploaded_file:
    data = analyze_midi_deep(uploaded_file)
    
    if data:
        st.markdown("### 🛠️ Live Analyse")
        m1, m2, m3, m4 = st.columns(4)
        m1.metric("BPM", data['tempo'])
        m2.metric("Register", data['register'])
        m3.metric("Toonladder", f"{data['root_name']} {data['scale']}")
        m4.metric("Noten", data['notes_count'])

        st.divider()
        col_left, col_right = st.columns([2, 1])

        with col_left:
            st.markdown("### 📊 Frequency Blueprint")
            chart_df = get_frequency_data(data['notes'])
            st.line_chart(chart_df.set_index('Gebied'), color="#00d1ff")

        with col_right:
            st.markdown("### ⚠️ Collision Alerts")
            low_mid_val = chart_df.loc[chart_df['Gebied'] == '3. Low-Mid (250-500Hz)', 'Aantal Noten'].values[0]
            sub_bass_val = chart_df.loc[chart_df['Gebied'] == '1. Sub (0-60Hz)', 'Aantal Noten'].values[0]

            if low_mid_val >= 3:
                st.error("**MODDER-ALARM:** Te veel noten in het Low-Mid gebied (250-500Hz). Je mix wordt troebel.")
            elif sub_bass_val >= 1:
                st.warning("**SUB-COLLISION:** Akkoord-noten in het Sub-gebied. Dit vecht met je Kick/808.")
            else:
                st.success("**MIX IS CLEAN:** Goede verdeling van frequenties gevonden.")
            
        st.divider()
        with st.expander("🚀 Volgende Stappen voor je Productie", expanded=True):
            delay_ms = round(60000 / data['tempo'] / 2, 2)
            st.write("Gebaseerd op deze analyse raden we het volgende aan:")
            st.info(f"• **Delay:** Stel je delay in op **{delay_ms} ms** voor een perfecte 1/8 ritme-sync.")
            st.info(f"• **Drums:** Gebruik een {('korte, droge' if data['tempo'] > 110 else 'diepe, galmende')} kick die past bij {data['vibe']}.")
            # --- NIEUW: AI CO-PRODUCER BLOK ---
        st.divider()
        st.markdown("### 🤖 AI Co-Producer: Bassline Blueprint")
        
        root_note = data['root_name']
        
        if genre == "Hiphop":
            st.info(f"**De Boom-Bap Bass:** Speel je baslijn voornamelijk rond de noot **{root_note}**. Laat ruimte op de 2e en 4e tel (waar je snare valt). Tip: Slide aan het einde van de 4e maat omhoog voor die klassieke swing.")
        elif genre == "Trap":
            st.error(f"**De 808 Bounce:** Zet een harde 808 op de **{root_note}**. Speel snelle, korte accenten op de 'off-beats'. Als het akkoord wisselt, laat de 808 dan pas op de tweede tel meekomen voor extra bounce.")
        elif genre == "R&B":
            st.success(f"**De Soulful Sub:** Begin op **{root_note}**, maar 'wandel' rond. Speel net een fractie *na* de tel (laid-back) voor die sexy groove en loop via de toonladder langzaam omlaag.")
           
        # --- DE MAGIC BUTTONS: EXPORTEER MIDI ---
        st.divider()
        st.write("### 🎹 Exporteer MIDI Starters")
        
        # We maken 2 kolommen voor de 2 knoppen
        btn1, btn2 = st.columns(2)
        
    with btn1:
        bass_midi_bytes = generate_bassline_midi(data['root_number'], genre)
        st.download_button(
            label="🎸 Download Baslijn",
            data=bass_midi_bytes,
            file_name=f"PA_Bass_{genre}_{root_note}.mid",
            mime="audio/midi",
            use_container_width=True
        )
        
    with btn2:
            drum_zip_bytes = generate_drum_zip(genre)
            st.download_button(
                label="📦 Download Drum Stems (.zip)",
                data=drum_zip_bytes,
                file_name=f"PA_Drum_Stems_{genre}.zip",
                mime="application/zip",
                use_container_width=True
            )