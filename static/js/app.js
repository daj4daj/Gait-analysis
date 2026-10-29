/**
 * KinetaGait PT - Clinical Gait Analysis Front-End Controller
 * Manages video uploads, live webcam recording with MediaRecorder,
 * real-time feedback, API communications, and results dashboard rendering.
 */

let selectedFile = null;
let webcamStream = null;
let mediaRecorder = null;
let recordedChunks = [];
let currentSessionData = null;

document.addEventListener("DOMContentLoaded", () => {
  loadSampleList();
  setupDropzone();
});

// Mode Switching (Upload, Live Webcam, Samples)
function switchInputMode(mode) {
  document.getElementById("tabUploadBtn").classList.remove("active");
  document.getElementById("tabLiveBtn").classList.remove("active");
  document.getElementById("tabSamplesBtn").classList.remove("active");

  document.getElementById("uploadModePanel").style.display = "none";
  document.getElementById("liveModePanel").style.display = "none";
  document.getElementById("samplesModePanel").style.display = "none";

  if (mode === "upload") {
    document.getElementById("tabUploadBtn").classList.add("active");
    document.getElementById("uploadModePanel").style.display = "block";
    stopCamera();
  } else if (mode === "live") {
    document.getElementById("tabLiveBtn").classList.add("active");
    document.getElementById("liveModePanel").style.display = "block";
    startCamera();
  } else if (mode === "samples") {
    document.getElementById("tabSamplesBtn").classList.add("active");
    document.getElementById("samplesModePanel").style.display = "block";
    stopCamera();
  }
}

// Drag & Drop Setup
function setupDropzone() {
  const dropzone = document.getElementById("videoDropzone");
  if (!dropzone) return;

  ['dragenter', 'dragover', 'dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, preventDefaults, false);
  });

  function preventDefaults(e) {
    e.preventDefault();
    e.stopPropagation();
  }

  ['dragenter', 'dragover'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.add('dragover'), false);
  });

  ['dragleave', 'drop'].forEach(eventName => {
    dropzone.addEventListener(eventName, () => dropzone.classList.remove('dragover'), false);
  });

  dropzone.addEventListener('drop', (e) => {
    const dt = e.dataTransfer;
    const files = dt.files;
    if (files.length > 0) {
      handleSelectedFile(files[0]);
    }
  });
}

function handleFileSelect(e) {
  const files = e.target.files;
  if (files.length > 0) {
    handleSelectedFile(files[0]);
  }
}

function handleSelectedFile(file) {
  selectedFile = file;
  document.getElementById("fileSelectedDisplay").style.display = "inline-flex";
  document.getElementById("fileNameSpan").textContent = `${file.name} (${(file.size / (1024 * 1024)).toFixed(1)} MB)`;
}

// Upload & Process Video
async function submitVideoUpload() {
  if (!selectedFile) {
    alert("Please select or drop a patient video file first.");
    return;
  }

  const formData = getPatientFormData();
  formData.append("file", selectedFile);

  showProgress("Processing Video & Tracking Gait", "Extracting 33 body landmarks and segmenting gait cycles...");

  try {
    const response = await fetch("/api/upload", {
      method: "POST",
      body: formData
    });

    if (!response.ok) {
      throw new Error(`Server returned status: ${response.status}`);
    }

    const data = await response.json();
    hideProgress();
    renderAnalysisResults(data);
  } catch (err) {
    hideProgress();
    alert("Error analyzing video: " + err.message);
  }
}

// Camera & Live Recording
async function startCamera() {
  const videoElem = document.getElementById("webcamVideo");
  const hud = document.getElementById("webcamHud");

  try {
    webcamStream = await navigator.mediaDevices.getUserMedia({
      video: {
        width: { ideal: 1280 },
        height: { ideal: 720 },
        facingMode: "user"
      },
      audio: false
    });

    videoElem.srcObject = webcamStream;
    document.getElementById("startCamBtn").disabled = true;
    document.getElementById("stopCamBtn").disabled = false;
    document.getElementById("record5sBtn").disabled = false;
    document.getElementById("record10sBtn").disabled = false;
    hud.innerHTML = '<i class="fa-solid fa-circle-check" style="color: #10b981;"></i> Camera Live | Position patient on walkway or treadmill';
  } catch (err) {
    hud.innerHTML = `<i class="fa-solid fa-triangle-exclamation" style="color: #ef4444;"></i> Camera access error: ${err.message}`;
    console.error("Camera access error:", err);
  }
}

function stopCamera() {
  if (webcamStream) {
    webcamStream.getTracks().forEach(track => track.stop());
    webcamStream = null;
  }
  const videoElem = document.getElementById("webcamVideo");
  if (videoElem) videoElem.srcObject = null;

  const startBtn = document.getElementById("startCamBtn");
  const stopBtn = document.getElementById("stopCamBtn");
  const rec5Btn = document.getElementById("record5sBtn");
  const rec10Btn = document.getElementById("record10sBtn");

  if (startBtn) startBtn.disabled = false;
  if (stopBtn) stopBtn.disabled = true;
  if (rec5Btn) rec5Btn.disabled = true;
  if (rec10Btn) rec10Btn.disabled = true;

  const recIndicator = document.getElementById("recIndicator");
  if (recIndicator) recIndicator.style.display = "none";
}

// Record Gait Clip & Send to Backend
function recordAndAnalyze(seconds) {
  if (!webcamStream) return;

  recordedChunks = [];
  const options = { mimeType: 'video/webm;codecs=vp9' };
  try {
    mediaRecorder = new MediaRecorder(webcamStream, options);
  } catch (e) {
    mediaRecorder = new MediaRecorder(webcamStream);
  }

  mediaRecorder.ondataavailable = (e) => {
    if (e.data.size > 0) {
      recordedChunks.push(e.data);
    }
  };

  mediaRecorder.onstop = async () => {
    const recIndicator = document.getElementById("recIndicator");
    recIndicator.style.display = "none";

    const blob = new Blob(recordedChunks, { type: 'video/webm' });
    const formData = getPatientFormData();
    formData.append("file", blob, `live_gait_${Date.now()}.webm`);

    showProgress("Analyzing Live Recorded Gait", "Running frame-by-frame 3D joint tracking and biomechanical scoring...");

    try {
      const response = await fetch("/api/record", {
        method: "POST",
        body: formData
      });

      if (!response.ok) throw new Error("Processing failed on server");
      const data = await response.json();
      hideProgress();
      renderAnalysisResults(data);
    } catch (err) {
      hideProgress();
      alert("Error processing recorded gait: " + err.message);
    }
  };

  mediaRecorder.start();

  const recIndicator = document.getElementById("recIndicator");
  const timerSpan = document.getElementById("recTimerSpan");
  recIndicator.style.display = "flex";

  let remaining = seconds;
  timerSpan.textContent = `${remaining}s`;

  const countdown = setInterval(() => {
    remaining--;
    timerSpan.textContent = `${remaining}s`;
    if (remaining <= 0) {
      clearInterval(countdown);
      if (mediaRecorder.state === "recording") {
        mediaRecorder.stop();
      }
    }
  }, 1000);
}

// Load Demonstration Clinical Samples
async function loadSampleList() {
  const container = document.getElementById("samplesContainer");
  if (!container) return;

  try {
    const res = await fetch("/api/samples");
    const samples = await res.json();

    container.innerHTML = samples.map(sample => {
      let tagClass = "tag-normal";
      if (sample.type.includes("Hyperextension")) tagClass = "tag-severe";
      else if (sample.type.includes("Clearance")) tagClass = "tag-patho";

      return `
        <div class="sample-card" onclick="analyzeSampleVideo('${sample.id}')">
          <div>
            <span class="sample-tag ${tagClass}">${sample.type}</span>
            <h4 style="margin-top: 0.5rem;">${sample.name}</h4>
            <p style="margin-top: 0.35rem;">${sample.description}</p>
          </div>
          <button class="btn btn-secondary" style="width: 100%; margin-top: 0.5rem;">
            <i class="fa-solid fa-play"></i> Run PT Analysis
          </button>
        </div>
      `;
    }).join("");
  } catch (err) {
    console.error("Could not load samples:", err);
  }
}

// Analyze Sample Video
async function analyzeSampleVideo(sampleId) {
  showProgress("Processing Clinical Sample", `Analyzing ${sampleId.replace('_', ' ')} with kinematics engine...`);
  const formData = getPatientFormData();

  try {
    const response = await fetch(`/api/analyze-sample/${sampleId}`, {
      method: "POST",
      body: formData
    });

    if (!response.ok) throw new Error("Sample analysis failed");
    const data = await response.json();
    hideProgress();
    renderAnalysisResults(data);
  } catch (err) {
    hideProgress();
    alert("Error: " + err.message);
  }
}

// Patient Form Data Helper
function getPatientFormData() {
  const formData = new FormData();
  formData.append("patient_name", document.getElementById("patientName").value || "Patient");
  formData.append("patient_mrn", document.getElementById("patientMRN").value || "MRN-001");
  formData.append("patient_age", document.getElementById("patientAge").value || "40");
  formData.append("patient_gender", document.getElementById("patientGender").value || "Unspecified");
  formData.append("physician", document.getElementById("physician").value || "Attending MD");
  formData.append("therapist", document.getElementById("therapist").value || "Physical Therapist, DPT");
  formData.append("complaint", document.getElementById("complaint").value || "Gait assessment.");
  return formData;
}

// Render Results Dashboard
function renderAnalysisResults(data) {
  currentSessionData = data;
  const m = data.metrics;

  // Header meta
  document.getElementById("resPatientHeading").textContent = `Gait Biomechanical Assessment - ${data.patient_info.name}`;
  document.getElementById("resSessionId").textContent = data.session_id;
  document.getElementById("resDate").textContent = new Date().toLocaleDateString('en-US', { month: 'short', day: 'numeric', year: 'numeric' });

  // Scorecards
  document.getElementById("valSymmetry").textContent = `${m.gait_symmetry_score}%`;
  document.getElementById("valCadence").textContent = `${Math.round(m.cadence)}`;
  document.getElementById("valStrideTime").textContent = `${m.avg_stride_time.toFixed(2)}s`;
  document.getElementById("valStanceRatio").textContent = `${m.l_stance_pct}% / ${m.r_stance_pct}%`;

  const symmCard = document.getElementById("cardSymmetry");
  if (m.gait_symmetry_score >= 90) {
    symmCard.style.borderColor = "var(--success)";
  } else if (m.gait_symmetry_score >= 80) {
    symmCard.style.borderColor = "var(--warning)";
  } else {
    symmCard.style.borderColor = "var(--danger)";
  }

  // Video Player
  const vidElem = document.getElementById("annotatedVideo");
  vidElem.src = data.files.annotated_video;
  vidElem.load();

  // Metrics Table
  renderMetricsTable(m);

  // Charts
  document.getElementById("chartKneeImg").src = data.files.knee_chart + `?t=${Date.now()}`;
  document.getElementById("chartHipImg").src = data.files.hip_chart + `?t=${Date.now()}`;

  // Deviations
  renderDeviations(data.deviations);

  // PT Interventions
  renderPTPlan(data.pt_plan);

  // Download PDF Link
  const pdfBtn = document.getElementById("downloadPdfBtn");
  pdfBtn.href = data.files.pdf_report;

  // Reveal Section & Smooth Scroll
  const resSec = document.getElementById("resultsSection");
  resSec.style.display = "block";
  resSec.scrollIntoView({ behavior: "smooth" });
}

function renderMetricsTable(m) {
  const tbody = document.getElementById("metricsTableBody");
  const items = [
    {
      param: "Cadence (steps/min)",
      left: Math.round(m.cadence),
      right: Math.round(m.cadence),
      ref: "100 - 120",
      status: (m.cadence >= 100 && m.cadence <= 120) ? "normal" : "warning",
      statusText: (m.cadence >= 100 && m.cadence <= 120) ? "Normal" : "Borderline"
    },
    {
      param: "Stride Time Duration (s)",
      left: m.l_stride_time.toFixed(2),
      right: m.r_stride_time.toFixed(2),
      ref: "1.00 - 1.25s",
      status: (m.avg_stride_time >= 1.0 && m.avg_stride_time <= 1.25) ? "normal" : "warning",
      statusText: "Normal"
    },
    {
      param: "Stance Phase % (gait cycle)",
      left: `${m.l_stance_pct}%`,
      right: `${m.r_stance_pct}%`,
      ref: "58 - 62%",
      status: Math.abs(m.l_stance_pct - m.r_stance_pct) < 5.0 ? "normal" : "danger",
      statusText: Math.abs(m.l_stance_pct - m.r_stance_pct) < 5.0 ? "Symmetric" : "Asymmetric"
    },
    {
      param: "Peak Swing Knee Flexion",
      left: `${m.l_knee_max_flex}°`,
      right: `${m.r_knee_max_flex}°`,
      ref: "60 - 68°",
      status: (m.l_knee_max_flex >= 55 && m.r_knee_max_flex >= 55) ? "normal" : "danger",
      statusText: (m.l_knee_max_flex >= 55 && m.r_knee_max_flex >= 55) ? "Normal" : "Reduced"
    },
    {
      param: "Stance Knee Extension / Neutral",
      left: `${m.l_knee_min_ext}°`,
      right: `${m.r_knee_min_ext}°`,
      ref: "0 to 5°",
      status: (m.l_knee_min_ext < -3.0 || m.r_knee_min_ext < -3.0) ? "danger" : "normal",
      statusText: (m.l_knee_min_ext < -3.0 || m.r_knee_min_ext < -3.0) ? "Recurvatum Alert" : "Neutral"
    },
    {
      param: "Max Hip Flexion (Initial Contact)",
      left: `${m.l_hip_max_flex}°`,
      right: `${m.r_hip_max_flex}°`,
      ref: "25 - 32°",
      status: "normal",
      statusText: "Normal"
    },
    {
      param: "Forward Trunk Lean",
      left: `${m.mean_trunk_lean}°`,
      right: `${m.mean_trunk_lean}°`,
      ref: "1 - 5°",
      status: m.mean_trunk_lean <= 6.0 ? "normal" : "warning",
      statusText: m.mean_trunk_lean <= 6.0 ? "Normal" : "Excessive Lean"
    },
    {
      param: "Frontal Pelvic Drop / Obliquity",
      left: `${m.max_pelvic_drop}°`,
      right: `${m.max_pelvic_drop}°`,
      ref: "< 4.0°",
      status: m.max_pelvic_drop <= 4.0 ? "normal" : "warning",
      statusText: m.max_pelvic_drop <= 4.0 ? "Level" : "Trendelenburg Sign"
    }
  ];

  tbody.innerHTML = items.map(it => `
    <tr>
      <td style="font-weight: 600;">${it.param}</td>
      <td>${it.left}</td>
      <td>${it.right}</td>
      <td style="color: var(--text-muted);">${it.ref}</td>
      <td><span class="status-badge status-${it.status}">${it.statusText}</span></td>
    </tr>
  `).join("");
}

function renderDeviations(deviations) {
  const container = document.getElementById("deviationsContainer");
  if (!deviations || deviations.length === 0) {
    container.innerHTML = `<p style="color: var(--success); font-weight: 600;"><i class="fa-solid fa-circle-check"></i> No significant gait deviations detected.</p>`;
    return;
  }

  container.innerHTML = deviations.map(d => {
    let sevBadge = "status-normal";
    if (d.severity === "Moderate" || d.severity === "Severe") sevBadge = "status-danger";
    else if (d.severity === "Mild") sevBadge = "status-warning";

    return `
      <div class="deviation-item sev-${d.severity}">
        <div class="dev-title-row">
          <span class="dev-title">${d.name} (${d.side})</span>
          <span class="status-badge ${sevBadge}">Severity: ${d.severity}</span>
        </div>
        <div class="dev-desc">
          <strong>Measured:</strong> ${d.measured} (Ref: ${d.normal})<br/>
          <strong>Clinical Impact:</strong> ${d.clinical_impact}
        </div>
      </div>
    `;
  }).join("");
}

function renderPTPlan(ptPlan) {
  const exContainer = document.getElementById("exercisesContainer");
  const drillsContainer = document.getElementById("drillsContainer");
  const dosageContainer = document.getElementById("dosageContainer");

  const exercises = ptPlan.exercises || [];
  exContainer.innerHTML = exercises.map(ex => `
    <div class="exercise-card">
      <h4><i class="fa-solid fa-circle-check"></i> ${ex.title}</h4>
      <div class="exercise-meta">Target: <strong>${ex.target}</strong></div>
      <div class="exercise-details">
        <strong>Prescription:</strong> ${ex.prescription}
      </div>
      <div class="exercise-rationale">
        Rationale: ${ex.rationale}
      </div>
    </div>
  `).join("");

  const drills = ptPlan.gait_drills || [];
  const cues = ptPlan.cues || [];

  drillsContainer.innerHTML = `
    ${drills.map(d => `<div style="margin-bottom: 4px;">• <strong>Drill:</strong> ${d}</div>`).join("")}
    ${cues.map(c => `<div style="margin-bottom: 4px;">• <strong>Verbal Cue:</strong> <em>"${c}"</em></div>`).join("")}
  `;

  dosageContainer.textContent = ptPlan.dosage || "";
}

function setVideoSpeed(speed) {
  const vid = document.getElementById("annotatedVideo");
  if (vid) vid.playbackRate = speed;
}

// Progress Bar Display
function showProgress(title, step) {
  const container = document.getElementById("progressContainer");
  container.style.display = "block";
  document.getElementById("progressTitle").textContent = title;
  document.getElementById("progressStep").textContent = step;
  container.scrollIntoView({ behavior: "smooth" });
}

function hideProgress() {
  document.getElementById("progressContainer").style.display = "none";
}

// Notes Modal & Report Re-generation
function openNotesModal() {
  document.getElementById("notesModal").style.display = "flex";
}

function closeNotesModal() {
  document.getElementById("notesModal").style.display = "none";
}

async function saveAndReExportReport() {
  if (!currentSessionData) return;
  const customNotes = document.getElementById("modalTherapistNotes").value;

  const formData = new FormData();
  formData.append("session_id", currentSessionData.session_id);
  formData.append("patient_name", currentSessionData.patient_info.name);
  formData.append("patient_mrn", currentSessionData.patient_info.mrn);
  formData.append("patient_age", currentSessionData.patient_info.age);
  formData.append("patient_gender", currentSessionData.patient_info.gender);
  formData.append("physician", currentSessionData.patient_info.physician);
  formData.append("therapist", currentSessionData.patient_info.therapist);
  formData.append("complaint", currentSessionData.patient_info.complaint);
  formData.append("custom_notes", customNotes);

  try {
    const res = await fetch("/api/custom-report", {
      method: "POST",
      body: formData
    });
    const result = await res.json();
    if (result.status === "success") {
      document.getElementById("downloadPdfBtn").href = result.pdf_url;
      closeNotesModal();
      window.open(result.pdf_url, "_blank");
    }
  } catch (err) {
    alert("Error updating report: " + err.message);
  }
}
