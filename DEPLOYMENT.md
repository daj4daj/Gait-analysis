# Deployment Guide - KinetaGait PT Web Application

This guide explains how to upload, deploy, and host the **KinetaGait PT** application on a website or cloud server.

---

## 📦 What is in the Deployment Package?

The deployment package contains everything needed to run the app in production:
* `app.py`: FastAPI web server and REST API endpoints.
* `gait_engine.py`: MediaPipe pose tracking, joint angle math, and cycle segmentation.
* `report_generator.py`: ReportLab clinical Physical Therapy assessment PDF generator.
* `models/`: Pre-loaded MediaPipe pose landmark models (`pose_landmarker_lite.task`).
* `static/`: Production HTML5, CSS3, and JavaScript frontend assets.
* `samples/`: Sample demonstration gait videos.
* `Dockerfile` & `docker-compose.yml`: Standardized container configurations.
* `Procfile`: PaaS entrypoint (Render, Railway, Heroku).
* `requirements.txt`: Python production dependencies.

---

## 🚀 Deployment Options

### Option 1: Render.com (Recommended - Easiest & Fast)

1. Upload the files or push to a GitHub/GitLab repository.
2. Go to [Render.com](https://render.com) and click **New +** -> **Web Service**.
3. Select your repository (or connect Git).
4. Configure:
   - **Environment**: `Docker` (or `Python 3`)
   - **Build Command**: `pip install -r requirements.txt` (if using Python environment)
   - **Start Command**: `uvicorn app:app --host 0.0.0.0 --port $PORT`
5. Click **Create Web Service**. Your website URL will be live with free automatic SSL (HTTPS).

---

### Option 2: Railway.app (1-Click Docker Deploy)

1. Sign in to [Railway.app](https://railway.app).
2. Click **New Project** -> **Deploy from GitHub repo** (or use Railway CLI: `railway up`).
3. Railway will automatically detect the `Dockerfile` or `Procfile` and deploy your app.
4. Under project **Settings** -> **Generate Domain** to get your public HTTPS URL.

---

### Option 3: VPS / Cloud Server (Ubuntu 22.04 / 24.04 on DigitalOcean, AWS EC2, Linode, Hetzner)

#### Method A: Using Docker (Fastest & Cleanest)
1. Upload the zip package to your server:
   ```bash
   scp gait-analysis-website-package.zip user@YOUR_SERVER_IP:/var/www/
   ```
2. Unzip on the server:
   ```bash
   cd /var/www && unzip gait-analysis-website-package.zip -d gait-app
   cd /var/www/gait-app
   ```
3. Run with Docker Compose:
   ```bash
   docker compose up -d --build
   ```
4. The application is now running on port 8000!

#### Method B: Native Linux Systemd + Nginx Reverse Proxy
1. Install system prerequisites:
   ```bash
   sudo apt update && sudo apt install -y python3-pip python3-venv ffmpeg libgl1 nginx
   ```
2. Set up virtual environment and install dependencies:
   ```bash
   cd /var/www/gait-app
   python3 -m venv venv
   source venv/bin/activate
   pip install -r requirements.txt
   ```
3. Create systemd service (`/etc/systemd/system/gaitapp.service`):
   ```ini
   [Unit]
   Description=KinetaGait PT Web Application
   After=network.target

   [Service]
   User=www-data
   WorkingDirectory=/var/www/gait-app
   Environment="PATH=/var/www/gait-app/venv/bin"
   Environment="MPLCONFIGDIR=/tmp/matplotlib_cache"
   ExecStart=/var/www/gait-app/venv/bin/uvicorn app:app --host 127.0.0.1 --port 8000

   [Install]
   WantedBy=multi-user.target
   ```
4. Start the service:
   ```bash
   sudo systemctl daemon-reload
   sudo systemctl enable --now gaitapp
   ```
5. Configure Nginx (`/etc/nginx/sites-available/gaitapp`):
   ```nginx
   server {
       server_name yourdomain.com;
       client_max_body_size 100M;

       location / {
           proxy_pass http://127.0.0.1:8000;
           proxy_set_header Host $host;
           proxy_set_header X-Real-IP $remote_addr;
           proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
           proxy_set_header X-Forwarded-Proto $scheme;
       }
   }
   ```
6. Enable SSL:
   ```bash
   sudo certbot --nginx -d yourdomain.com
   ```

---

### Option 4: Google Cloud Run (Serverless Container)

1. Build and push image:
   ```bash
   gcloud builds submit --tag gcr.io/YOUR_PROJECT_ID/gait-analysis-app
   ```
2. Deploy to Cloud Run:
   ```bash
   gcloud run deploy gait-analysis-app \
     --image gcr.io/YOUR_PROJECT_ID/gait-analysis-app \
     --platform managed \
     --allow-unauthenticated \
     --memory 2Gi \
     --cpu 2
   ```

---

## 🔒 Security & Performance Tips for Production
- **File Upload Limits**: Ensure `client_max_body_size` is set to at least `100M` in Nginx or reverse proxy for large 4K/HD video uploads.
- **HTTPS Camera Permissions**: Web browsers require HTTPS (`https://`) to grant webcam access (`getUserMedia`). Ensure SSL is enabled.
- **Temporary File Cleanup**: The app writes uploaded and generated files to `/uploads` and `/reports`. A nightly cron job can clean files older than 24-48 hours if storage is constrained.
