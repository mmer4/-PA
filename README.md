# 🎹 PA (Producer Adviser) 
> *Your AI-driven Co-Producer for modern beatmaking. Bridge the gap between music theory and technical production.*

![Version](https://img.shields.io/badge/version-1.0_Beta-blue)
![Python](https://img.shields.io/badge/Python-3.9+-yellow)
![Streamlit](https://img.shields.io/badge/Streamlit-Framework-FF4B4B)

## 🚀 Overview
PA (Producer Adviser) is an interactive, web-based MIDI companion built for modern music producers. Instead of relying on generic loops, PA analyzes the producer's custom chord progressions and generates highly specific, mathematically perfect basslines, drum stems, and melodies tailored to the selected genre.

Currently in **Closed Beta (V1.0)**, PA serves as the cloud-based prototype for a future hybrid VST plugin.

## ✨ Key Features
* **🧠 Deep MIDI Analysis:** Upload your base chords (`.mid`) and PA instantly detects the musical key, scale, tempo, and register.
* **⚠️ Mud / Collision Alerts:** The algorithm calculates frequency distribution and warns you if too many notes are clashing in the sub or low-mid frequencies (250-500Hz).
* **🧬 Dynamic Stem Generation:** 
  * Generates intelligent **Basslines** that respect the detected scale and root notes.
  * Generates **Drum Stems** (Kick, Snare, Hi-hat, Percussion) packed in a `.zip` file.
  * Generates **Melodies / Toplines** using safe-note calculation.
* **🎛️ Humanize & Swing:** Inject life into rigid MIDI by adjusting the global Swing percentage.
* **🌍 Bilingual UI:** Seamlessly switch between English and Dutch interfaces.

## 🛠️ Tech Stack
* **Language:** Python
* **Frontend/UI:** Streamlit
* **MIDI Processing:** `mido` (Musical Instrument Digital Interface parsing)
* **Data Handling:** `pandas`, `io` (In-memory zip generation)

## 🗺️ Project Roadmap
- [x] **Phase 1:** Web-based SaaS Prototype (Streamlit) & Closed Beta.
- [ ] **Phase 2:** Brain Extraction (Converting the engine to a FastAPI backend).
- [ ] **Phase 3:** VST/AU Client Development (JUCE/C++ interface communicating with the Python API).
- [ ] **Phase 4:** Commercial Launch & Subscription Model.

## 🤝 Contributing & Feedback
PA is currently in Closed Beta. If you have an invite link, please use the built-in feedback button in the app's sidebar to report bugs or request features. 

---
*Developed with ❤️ for the modern producer.*
