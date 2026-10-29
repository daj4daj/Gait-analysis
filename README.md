# KinetaGait PT - Clinical Gait Analysis & Biomechanical Reporting System

**KinetaGait PT** is a specialized, computer-vision powered gait analysis application designed for **Physical Therapists, Physiatrists, and Orthopedic Rehabilitation Specialists**. It processes patient walking videos (either recorded live via webcam or uploaded from video files) to extract 3D/2D joint kinematics, detect clinical movement abnormalities, and compile a comprehensive, publication-quality **Physical Therapy Biomechanical Assessment Report in PDF format**.

---

## 🌟 Key Capabilities

### 1. Dual Video Analysis Modes
- **Live Webcam Gait Capture**:
  - Direct browser camera integration with real-time video preview.
  - One-click **5-Second or 10-Second gait recording** (ideal for clinical walking runways or treadmills).
  - Automatically sends captured video to the biomechanical processing pipeline.
- **Uploaded Patient Video**:
  - Drag-and-drop or file upload supporting MP4, MOV, WebM, and AVI formats recorded from sagittal (side) or frontal views.
  - Built-in **Demonstration Clinical Samples** (Healthy Symmetric Gait, Genu Recurvatum / Hyperextension, and Stiff Knee Gait) for immediate 1-click evaluation without needing video files.

### 2. Biomechanical & Kinematic Extraction Engine
Powered by **Google MediaPipe PoseLandmarker** with Metal GPU acceleration:
- **Joint Kinematic Ranges of Motion (ROM)**:
  - Knee Flexion / Extension at Initial Contact, Midstance, Terminal Stance, and Peak Swing (detects hyperextension / genu recurvatum).
  - Hip Flexion at Initial Contact and Terminal Stance Extension.
  - Forward Trunk Lean relative to gravity vertical.
  - Frontal Pelvic Obliquity / Drop (Trendelenburg sign).
- **Spatiotemporal Parameters**:
  - Cadence (steps/minute).
  - Stride Time & Step Duration (seconds).
  - Stance Phase % vs. Swing Phase % distribution.
  - **Gait Symmetry Index (SI %)**: Quantifies bilateral limb loading balance.
- **Continuous 0–100% Gait Cycle Curves**:
  - Time-normalized kinematic curves plotted against **2-SD Normative Adult Corridors** (Perry & Burnfield reference data).

### 3. Automated Pathology & Clinical Deviation Detection
Automatically flags pathological gait strategies and rates their severity:
- **Genu Recurvatum (Knee Hyperextension)** during midstance.
- **Stiff Knee Gait / Reduced Swing Flexion** (compromised foot clearance).
- **Antalgic / Asymmetric Stance** (unloading of symptomatic limb).
- **Excessive Forward Trunk Lean** (compensation for hip extensor or quad weakness).
- **Trendelenburg Sign / Pelvic Obliquity** (gluteus medius abductor insufficiency).

### 4. Evidence-Based Physical Therapy Prescription
Maps detected deviations directly into an individualized clinical rehabilitation protocol:
- **Therapeutic Exercise Prescription**: Target musculature, precise dosage (sets/reps/duration), and clinical rationale (e.g., Terminal Knee Extensions, Eccentric Step-Downs, Prone Hamstring Curls, Clamshells, Lateral Monster Walks).
- **Neuromotor Gait Retraining Drills**: Auditory pacing, tactile soft-landing cues, obstacle step-overs, and mirror biofeedback.
- **Recommended Treatment Frequency**: Plan of care duration and Home Exercise Program (HEP) guidelines.

### 5. Multi-Page Clinical PDF Assessment Report
Generated using **ReportLab** with a professional medical layout:
- Clinic Header & Department Branding.
- Patient Demographics & Chief Complaint meta-table.
- Executive Mobility Scorecard (Symmetry Index %, Cadence, Stance Balance).
- Spatiotemporal & Kinematic Comparison Table with Normative Values and Status Badges.
- High-Resolution Embedded Kinematic Graphs (Knee ROM vs Normative corridor, Hip ROM vs Normative corridor, Stance/Swing balance).
- Observed Deviations and Biomechanical Impact Narrative.
- Individualized Physical Therapy Intervention Protocol.
- Evaluating Physical Therapist Clinical Sign-Off, Progress Notes, and Signature Line.

---

## 🚀 Quick Start & How to Run

### 1. Launch the Application
In your terminal, navigate to the project directory and run:

```bash
cd /Users/daj4daj/.gemini/antigravity/scratch/gait-analysis-app
./venv/bin/python3 run.py
```

Or run via `uvicorn`:
```bash
./venv/bin/uvicorn app:app --host 0.0.0.0 --port 8000
```

### 2. Open the Web Application
Open your web browser and navigate to:
```
http://localhost:8000
```

### 3. Usage Steps
1. Fill in or edit patient demographics (Name, MRN, Age, Gender, Chief Complaint).
2. Choose your input mode:
   - **Upload Video**: Select or drag a video file.
   - **Live Webcam**: Click "Start Webcam", position the patient, and click "Record 5-Sec Gait".
   - **Demo Samples**: Click on one of the pre-loaded clinical samples to run an instant analysis.
3. Review the **Interactive Results Dashboard**:
   - Inspect the skeleton-tracked video with 0.25x / 0.5x slow-motion controls.
   - Review joint kinematics against normative reference limits.
   - Inspect the Knee and Hip trajectories plotted against the shaded normative corridors.
   - Review the tailored Physical Therapy exercise prescription.
4. Click **"Download Full PT Report (PDF)"** to open or save the finalized medical report.
5. Click **"Edit Therapist Notes"** if you wish to adjust clinical notes or sign-off remarks before printing.

---

## 📂 Project Architecture

```
gait-analysis-app/
├── app.py                     # FastAPI web server and REST API endpoints
├── gait_engine.py             # MediaPipe 33-landmark pose tracking, kinematics & cycle segmentation
├── report_generator.py        # ReportLab multi-page clinical PDF report generator
├── sample_generator.py        # Articulated humanoid clinical gait video generator
├── run.py                     # Application launcher
├── requirements.txt           # Python package dependencies
├── models/
│   └── pose_landmarker_lite.task # Google MediaPipe pose landmarker model
├── static/
│   ├── index.html             # Responsive clinical web interface
│   ├── css/
│   │   └── style.css          # Healthcare UI design system
│   └── js/
│       └── app.js             # Webcam recorder, video sync, API controller
├── samples/                   # Pre-rendered demonstration clinical videos
│   ├── normal_gait.mp4
│   ├── recurvatum_asymmetry.mp4
│   └── stiff_knee_gait.mp4
├── uploads/                   # Temporary directory for uploaded and annotated videos
└── reports/                   # Generated clinical PDF reports and kinematic plots
```

---

## 🔬 Clinical Reference Norms (Adult Gait)

| Biomechanical Parameter | Normative Reference | Unit | Clinical Significance |
|:---|:---:|:---:|:---|
| **Cadence** | 100 – 120 | steps/min | Overall stepping tempo and rhythmicity |
| **Stride Duration** | 1.00 – 1.25 | sec | Time for one complete gait cycle |
| **Stance Phase Ratio** | 58.0 – 62.0% | % cycle | Weight-bearing contact duration |
| **Swing Phase Ratio** | 38.0 – 42.0% | % cycle | Non-weightbearing limb advancement |
| **Gait Symmetry Index** | &ge; 90.0% | % | Inter-limb loading and temporal symmetry |
| **Knee Flexion (Initial Contact)** | 0.0 – 5.0° | deg | Soft-landing shock attenuation |
| **Peak Swing Knee Flexion** | 60.0 – 68.0° | deg | Toe clearance to prevent tripping |
| **Stance Knee Extension** | 0.0 – 5.0° | deg | Extension neutral (<0° flags hyperextension) |
| **Max Hip Flexion (Initial Contact)** | 25.0 – 32.0° | deg | Forward step progression |
| **Terminal Stance Hip Extension** | 8.0 – 15.0° | deg | Trailing limb push-off propulsion |
| **Forward Trunk Lean** | 1.0 – 5.0° | deg | Sagittal postural stability |
| **Frontal Pelvic Drop** | &lt; 4.0° | deg | Gluteus medius dynamic lateral stability |

---

## 🛡️ Confidentiality & Compliance Notice
This system generates documents intended for **clinical decision support and educational motion analysis**. Clinical findings should be reviewed and verified by a licensed Physical Therapist or qualified healthcare professional.
