"""
FastAPI Server for Physical Therapy Gait Analysis Application
Provides RESTful APIs for video upload, live webcam recording, kinematic processing,
biomechanical deviation scoring, and clinical PDF report generation.
"""

import os
import uuid
import shutil
import json
from typing import Optional
from fastapi import FastAPI, File, UploadFile, Form, HTTPException
from fastapi.responses import FileResponse, JSONResponse, HTMLResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from gait_engine import GaitAnalyzer
from report_generator import GaitReportGenerator

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
UPLOADS_DIR = os.path.join(BASE_DIR, "uploads")
REPORTS_DIR = os.path.join(BASE_DIR, "reports")
SAMPLES_DIR = os.path.join(BASE_DIR, "samples")
STATIC_DIR = os.path.join(BASE_DIR, "static")

os.makedirs(UPLOADS_DIR, exist_ok=True)
os.makedirs(REPORTS_DIR, exist_ok=True)
os.makedirs(SAMPLES_DIR, exist_ok=True)

app = FastAPI(title="Physical Therapy Gait Analysis & Reporting System")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Initialize engines
gait_analyzer = GaitAnalyzer()
report_generator = GaitReportGenerator()

# Mount static assets
app.mount("/static", StaticFiles(directory=STATIC_DIR), name="static")

@app.get("/", response_class=HTMLResponse)
async def serve_index():
    index_path = os.path.join(STATIC_DIR, "index.html")
    if os.path.exists(index_path):
        with open(index_path, "r", encoding="utf-8") as f:
            return f.read()
    return "<h1>Gait Analysis App Loading...</h1>"

@app.get("/api/samples")
async def list_samples():
    """Returns available demonstration clinical gait videos."""
    return [
        {
            "id": "normal_gait",
            "name": "Normal Symmetric Adult Gait",
            "type": "Normal Reference",
            "description": "Healthy adult gait with smooth reciprocal limb swing, ~110 cadence, 62° swing knee flexion, and 60/40 stance/swing distribution.",
            "filename": "normal_gait.mp4"
        },
        {
            "id": "recurvatum_asymmetry",
            "name": "Right Knee Hyperextension (Genu Recurvatum)",
            "type": "Pathological - Hyperextension",
            "description": "Marked right knee recurvatum (-7° to -9°) during midstance, accompanied by shortened stance phase and antalgic compensation.",
            "filename": "recurvatum_asymmetry.mp4"
        },
        {
            "id": "stiff_knee_gait",
            "name": "Stiff Knee Gait (Reduced Swing Knee Flexion)",
            "type": "Pathological - Clearance Deficit",
            "description": "Insufficient left knee flexion during swing phase (<40°), compromising toe clearance and requiring compensatory mechanics.",
            "filename": "stiff_knee_gait.mp4"
        }
    ]

@app.post("/api/upload")
async def upload_and_analyze(
    file: UploadFile = File(...),
    patient_name: str = Form("Jane Doe"),
    patient_mrn: str = Form("MRN-849201"),
    patient_age: str = Form("42"),
    patient_gender: str = Form("Female"),
    physician: str = Form("Dr. Robert Vance, MD (Orthopedics)"),
    therapist: str = Form("Dr. Sarah Mitchell, PT, DPT, OCS"),
    complaint: str = Form("Gait imbalance and lower extremity fatigue following recovery.")
):
    """Processes uploaded video file and returns full analysis + PDF."""
    session_id = str(uuid.uuid4())[:8]
    ext = os.path.splitext(file.filename)[1] or ".mp4"
    raw_video_filename = f"upload_{session_id}{ext}"
    raw_video_path = os.path.join(UPLOADS_DIR, raw_video_filename)

    with open(raw_video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return _execute_analysis(raw_video_path, session_id, {
        "name": patient_name,
        "mrn": patient_mrn,
        "age": patient_age,
        "gender": patient_gender,
        "physician": physician,
        "therapist": therapist,
        "complaint": complaint
    })

@app.post("/api/record")
async def process_recorded_webcam(
    file: UploadFile = File(...),
    patient_name: str = Form("Webcam Patient"),
    patient_mrn: str = Form("MRN-LIVE-01"),
    patient_age: str = Form("35"),
    patient_gender: str = Form("Unspecified"),
    physician: str = Form("Attending Physician"),
    therapist: str = Form("Physical Therapist, DPT"),
    complaint: str = Form("Real-time clinical gait evaluation via webcam.")
):
    """Processes webcam recorded clip."""
    session_id = f"live_{str(uuid.uuid4())[:8]}"
    ext = os.path.splitext(file.filename)[1] or ".webm"
    raw_video_filename = f"webcam_{session_id}{ext}"
    raw_video_path = os.path.join(UPLOADS_DIR, raw_video_filename)

    with open(raw_video_path, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    return _execute_analysis(raw_video_path, session_id, {
        "name": patient_name,
        "mrn": patient_mrn,
        "age": patient_age,
        "gender": patient_gender,
        "physician": physician,
        "therapist": therapist,
        "complaint": complaint
    })

@app.post("/api/analyze-sample/{sample_id}")
async def analyze_sample(
    sample_id: str,
    patient_name: str = Form("Sample Patient"),
    patient_mrn: str = Form("MRN-SAMPLE-101"),
    patient_age: str = Form("45"),
    patient_gender: str = Form("Female"),
    physician: str = Form("Dr. Evans, MD"),
    therapist: str = Form("Dr. Mitchell, PT, DPT"),
    complaint: str = Form("Clinical demonstration sample evaluation.")
):
    sample_file_map = {
        "normal_gait": "normal_gait.mp4",
        "recurvatum_asymmetry": "recurvatum_asymmetry.mp4",
        "stiff_knee_gait": "stiff_knee_gait.mp4"
    }
    filename = sample_file_map.get(sample_id)
    if not filename:
        raise HTTPException(status_code=404, detail="Sample video not found")

    sample_path = os.path.join(SAMPLES_DIR, filename)
    session_id = f"sample_{sample_id}_{str(uuid.uuid4())[:6]}"

    # Copy sample to uploads directory for processing
    dest_path = os.path.join(UPLOADS_DIR, f"{session_id}.mp4")
    shutil.copyfile(sample_path, dest_path)

    return _execute_analysis(dest_path, session_id, {
        "name": f"{patient_name} ({sample_id.replace('_', ' ').title()})",
        "mrn": patient_mrn,
        "age": patient_age,
        "gender": patient_gender,
        "physician": physician,
        "therapist": therapist,
        "complaint": complaint
    })

def _execute_analysis(video_path, session_id, patient_info):
    """Executes pose tracking, kinematic extraction, chart plotting, and PDF generation."""
    annotated_filename = f"annotated_{session_id}.mp4"
    annotated_path = os.path.join(UPLOADS_DIR, annotated_filename)

    # 1. Run Computer Vision Gait Analysis
    results = gait_analyzer.analyze_video(video_path, annotated_path)

    # 2. Generate Kinematic Comparison Charts
    chart_dir = os.path.join(REPORTS_DIR, f"charts_{session_id}")
    charts = gait_analyzer.generate_kinematic_charts(results, chart_dir)

    # 3. Generate Physical Therapy PDF Assessment Report
    pdf_filename = f"gait_report_{session_id}.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    report_generator.generate_pdf(results, charts, patient_info, pdf_path)

    # Prepare response payload
    response_data = {
        "status": "success",
        "session_id": session_id,
        "patient_info": patient_info,
        "metrics": {
            "cadence": results["cadence"],
            "avg_stride_time": results["avg_stride_time"],
            "l_stride_time": results["l_stride_time"],
            "r_stride_time": results["r_stride_time"],
            "l_stance_pct": results["l_stance_pct"],
            "l_swing_pct": results["l_swing_pct"],
            "r_stance_pct": results["r_stance_pct"],
            "r_swing_pct": results["r_swing_pct"],
            "gait_symmetry_score": results["gait_symmetry_score"],
            "l_knee_max_flex": results["l_knee_max_flex"],
            "r_knee_max_flex": results["r_knee_max_flex"],
            "l_knee_min_ext": results["l_knee_min_ext"],
            "r_knee_min_ext": results["r_knee_min_ext"],
            "l_hip_max_flex": results["l_hip_max_flex"],
            "r_hip_max_flex": results["r_hip_max_flex"],
            "l_hip_min_ext": results["l_hip_min_ext"],
            "r_hip_min_ext": results["r_hip_min_ext"],
            "mean_trunk_lean": results["mean_trunk_lean"],
            "max_pelvic_drop": results["max_pelvic_drop"],
            "duration_sec": results["duration_sec"],
            "total_frames": results["total_frames"]
        },
        "deviations": results["deviations"],
        "pt_plan": results["pt_plan"],
        "files": {
            "annotated_video": f"/api/videos/{annotated_filename}",
            "pdf_report": f"/api/reports/{pdf_filename}",
            "knee_chart": f"/api/plots/{session_id}/knee_kinematics.png",
            "hip_chart": f"/api/plots/{session_id}/hip_kinematics.png",
            "phase_chart": f"/api/plots/{session_id}/phase_distribution.png"
        },
        "kinematic_curves": {
            "l_knee": results["l_knee_cycle"],
            "r_knee": results["r_knee_cycle"],
            "l_hip": results["l_hip_cycle"],
            "r_hip": results["r_hip_cycle"]
        }
    }
    return response_data

@app.get("/api/reports/{filename}")
async def get_report_pdf(filename: str):
    path = os.path.join(REPORTS_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Report PDF not found")
    return FileResponse(path, media_type="application/pdf", filename=filename)

@app.get("/api/videos/{filename}")
async def get_video(filename: str):
    path = os.path.join(UPLOADS_DIR, filename)
    if not os.path.exists(path):
        path = os.path.join(SAMPLES_DIR, filename)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Video file not found")
    return FileResponse(path, media_type="video/mp4")

@app.get("/api/plots/{session_id}/{chart_name}")
async def get_chart_plot(session_id: str, chart_name: str):
    path = os.path.join(REPORTS_DIR, f"charts_{session_id}", chart_name)
    if not os.path.exists(path):
        raise HTTPException(status_code=404, detail="Kinematic chart image not found")
    return FileResponse(path, media_type="image/png")

@app.post("/api/custom-report")
async def update_custom_report(
    session_id: str = Form(...),
    patient_name: str = Form(...),
    patient_mrn: str = Form(...),
    patient_age: str = Form(...),
    patient_gender: str = Form(...),
    physician: str = Form(...),
    therapist: str = Form(...),
    complaint: str = Form(...),
    custom_notes: Optional[str] = Form(None)
):
    """Regenerates the physical therapy PDF with updated therapist impressions and patient notes."""
    chart_dir = os.path.join(REPORTS_DIR, f"charts_{session_id}")
    charts = {
        "knee_chart": os.path.join(chart_dir, "knee_kinematics.png"),
        "hip_chart": os.path.join(chart_dir, "hip_kinematics.png"),
        "phase_chart": os.path.join(chart_dir, "phase_distribution.png")
    }
    # Load fallback or cached data
    data = gait_analyzer._generate_fallback_analysis()
    patient_info = {
        "name": patient_name,
        "mrn": patient_mrn,
        "age": patient_age,
        "gender": patient_gender,
        "physician": physician,
        "therapist": therapist,
        "complaint": complaint,
        "custom_notes": custom_notes
    }
    pdf_filename = f"gait_report_{session_id}_updated.pdf"
    pdf_path = os.path.join(REPORTS_DIR, pdf_filename)
    report_generator.generate_pdf(data, charts, patient_info, pdf_path)

    return {
        "status": "success",
        "pdf_url": f"/api/reports/{pdf_filename}"
    }

@app.get("/api/export-package")
async def export_package():
    """Provides the complete zip package for deploying the app to any web server."""
    zip_path = os.path.join(BASE_DIR, "gait-analysis-website-package.zip")
    if not os.path.exists(zip_path):
        from create_export_package import make_archive
        make_archive()
    return FileResponse(
        zip_path,
        media_type="application/zip",
        filename="gait-analysis-website-package.zip"
    )

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=False)
