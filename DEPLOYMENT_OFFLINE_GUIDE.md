# Vision: Offline Deployment Guide

This guide is intended for users who need to deploy the Vision project onto a **network-disconnected GPU RHEL system**. 

Because the target system does not have internet access, you must first prepare the project on a **network-connected non-GPU RHEL system**, package everything into a single file, transfer it, and then load it on the disconnected machine.

---

## Phase 1: On the Network-Connected Non-GPU RHEL System

You will need a system with internet access, Git, and Docker installed.

### 1. Clone the Repository
Clone the codebase to your internet-connected machine:
```bash
git clone <URL_TO_VISION_REPOSITORY> vision
cd vision
```
*(If you are reading this locally, you are already in the cloned repository.)*

### 2. Export Docker Images
The project relies on multiple Docker containers. Run the provided script to download and package all of them into a single file.
```bash
bash scripts/export_offline_images_linux.sh
```
- **What this does:** It pulls all necessary Docker images from the internet and saves them to a file named `vision_images.tar`.
- **Note:** This process might take 10-20 minutes, and the resulting file will be very large (15GB+).

---

## Phase 2: Transfer

Now you must transfer the necessary files from your internet-connected machine to the offline GPU machine.

### 1. What to Transfer
You need to transfer two things to the offline machine:
1. The entire `vision` code repository folder (which now includes `vision_images.tar`).
2. The AI Models zip file containing the Qwen 32B AWQ model, the BGE embedding model, and the BGE reranker model (you may have already done this step).

### 2. How to Transfer
Use a secure USB drive, an internal network file share, or any approved organizational method for air-gapped transfers.

---

## Phase 3: On the Network-Disconnected GPU RHEL System

Once you have transferred the files, proceed with the following steps on the machine equipped with GPUs.

### 1. Place the Models
The system expects the models to be located in a specific folder. 
1. Navigate to the `vision` repository directory you just transferred.
2. Ensure there is a folder named `models` inside it (i.e., `vision/models`).
3. Extract your AI Models zip file into this `vision/models` folder.
   
Your folder structure should look exactly like this:
```
vision/
├── models/
│   ├── Qwen2.5-VL-32B-Instruct-AWQ/
│   ├── bge-m3/
│   └── bge-reranker-v2-m3/
├── docker-compose.yml
├── Makefile
└── ... (other project files)
```

### 2. Load the Docker Images
You must load the packaged Docker images into the offline machine's Docker engine. Run:
```bash
bash scripts/load_offline_images.sh
```
- **What this does:** It reads the `vision_images.tar` file and loads all the images so they can be used without downloading.

### 3. Start the Project
Finally, run the following commands to initialize and start the Vision platform:
```bash
make setup
make up
```

### 4. Access the Application
Once the startup completes, the system will be available locally:
- **User Interface:** http://localhost:3000
- **API Health Check:** http://localhost:8000/api/health
- **Monitoring (Grafana):** http://localhost:3001

*Note: The first startup may take a few minutes as the 32B model is loaded into the GPU memory.*
