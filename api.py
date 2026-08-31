from fastapi import FastAPI, UploadFile, File, Response, Depends, HTTPException, Security
from fastapi.security.api_key import APIKeyHeader
import os
import mido
import io
import random
import zipfile



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
    
    
    return data

def analyze_midi_deep(file_bytes):
    try:
        mid = mido.MidiFile(file=io.BytesIO(file_bytes))
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
        root_name = get_note_name(root)
        intervals = [(n - root) % 12 for n in unique_notes]

        scale_type = "Complex / Onbekend"
        if 3 in intervals: 
            if 11 in intervals: scale_type = "Harmonisch Mineur"
            elif 9 in intervals and 10 in intervals: scale_type = "Dorisch"
            else: scale_type = "Natuurlijk Mineur"
            vibe_type = "Mineur"
        elif 4 in intervals: 
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
                    add_hit(events, note + 12, offset + (i * 0.5), 0.5, random.randint(90, 110), 0, swing_amount)
                    
        elif genre == "Hiphop":
            if random.random() > 0.3: add_hit(events, safe_notes[0], offset + 0, 1.5, 100, 0, swing_amount)
            if random.random() > 0.5: add_hit(events, safe_notes[2], offset + 1.5, 1.0, 90, 0, swing_amount)
            if random.random() > 0.3: add_hit(events, safe_notes[4], offset + 2.5, 1.0, 95, 0, swing_amount)
            if bar % 2 == 1: add_hit(events, safe_notes[6] - 12, offset + 3.5, 0.5, 80, 0, swing_amount) 
                
        else: 
            add_hit(events, safe_notes[0], offset + 0, 1.0, 90, 0, swing_amount)
            add_hit(events, safe_notes[2], offset + 1.0, 1.0, 85, 0, swing_amount)
            add_hit(events, safe_notes[4], offset + 2.0, 1.0, 80, 0, swing_amount)
            add_hit(events, safe_notes[0]+12, offset + 3.0, 1.0, 75, 0, swing_amount) 

    return schrijf_midi_events(events)
app = FastAPI(title="Producer Adviser API", version="1.0")


API_KEY_NAME = "X-API-KEY"


VALID_API_KEY = os.environ.get("PA_API_KEY", "super-geheime-test-sleutel-123") 

api_key_header = APIKeyHeader(name=API_KEY_NAME, auto_error=True)

async def check_api_key(api_key: str = Security(api_key_header)):
    if api_key != VALID_API_KEY:
        raise HTTPException(status_code=403, detail="Toegang geweigerd: Ongeldige of ontbrekende API sleutel.")
    return api_key
@app.get("/")
def read_root():
    return {"status": "PA Server is online 🟢"}

# --- NIEUW: Het Analyse Loket ---
@app.post("/analyze")
async def analyze_midi(file: UploadFile = File(...)):
    # 1. Lees het binnengekomen bestand in het werkgeheugen
    file_bytes = await file.read()
    
    # 2. Laat Mido het lezen alsof het een echt bestand is (zonder op te slaan)
    midi_data = mido.MidiFile(file=io.BytesIO(file_bytes))
    
    # 3. Zoek even snel het tempo (als test)
    tempo = 120
    for track in midi_data.tracks:
        for msg in track:
            if msg.type == 'set_tempo':
                tempo = round(mido.tempo2bpm(msg.tempo))
                break

    # 4. Stuur het antwoord terug als pure JSON data
    return {
        "bestandsnaam": file.filename,
        "gevonden_tempo": tempo,
        "aantal_tracks": len(midi_data.tracks),
        "status": "Succesvol uitgelezen door de API!"
    }
# ==========================================
# 🚪 DE API LOKETTEN (ENDPOINTS)
# ==========================================

@app.get("/")
def read_root():
    return {"status": "PA Server is online 🟢", "message": "De theorie-engine draait."}

# 1. HET ANALYSE LOKET (POST)
@app.post("/analyze")
async def analyze_midi_endpoint(file: UploadFile = File(...), api_key: str = Depends(check_api_key)):
        file_bytes = await file.read()
        
        # Voer de theorie-engine uit
        analysis_data = analyze_midi_deep(file_bytes)
        if not analysis_data:
            return {"error": "Geen geldige MIDI-noten gevonden in dit bestand."}
            
        # Voer de modder-check uit
        freq_data = get_frequency_data(analysis_data["notes"])
        
        # Stuur het complete JSON-rapport terug
        return {
            "status": "success",
            "filename": file.filename,
            "theorie": analysis_data,         # <--- Deze mist waarschijnlijk!
            "frequenties": freq_data          # <--- En deze ook!
        }

# 2. BASLIJN GENERATOR LOKET (GET)
@app.get("/generate/bass")
def generate_bass_endpoint(root_number: int, genre: str, swing_amount: int = 20, api_key: str = Depends(check_api_key)):
    midi_bytes = generate_bassline_midi(root_number, genre, swing_amount)
    return Response(
        content=midi_bytes,
        media_type="audio/midi",
        headers={"Content-Disposition": f"attachment; filename=PA_Bass_{genre}.mid"}
    )

# 3. MELODIE GENERATOR LOKET (GET)
@app.get("/generate/melody")
def generate_melody_endpoint(root_number: int, scale_type: str, genre: str, swing_amount: int = 20, api_key: str = Depends(check_api_key)):
    midi_bytes = generate_melody_midi(root_number, scale_type, genre, swing_amount)
    return Response(
        content=midi_bytes, 
        media_type="audio/midi",
        headers={"Content-Disposition": f"attachment; filename=PA_Melody_{genre}.mid"}
    )

# 4. DRUM STEMS GENERATOR LOKET (GET)
@app.get("/generate/drums")
def generate_drums_endpoint(genre: str, complexity: str, swing_amount: int = 20, api_key: str = Depends(check_api_key)):
    zip_bytes = generate_drum_zip(genre, complexity, swing_amount)
    return Response(
        content=zip_bytes, 
        media_type="application/zip",
        headers={"Content-Disposition": f"attachment; filename=PA_Drums_{genre}.zip"}
    )
