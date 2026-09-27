# 🚗 DEFECTRA — AI-Powered Vehicle Defect Detection

> **DEFECTRA** is an intelligent vehicle inspection system that uses **Computer Vision and Artificial Intelligence** to automatically detect external vehicle defects and provide an intelligent diagnosis and maintenance recommendations.

---

## 📌 Overview

**DEFECTRA** is an end-to-end AI solution designed to assist in vehicle inspection.

The system allows users to:

* 📷 Upload a vehicle image for automatic inspection
* 🤖 Detect visible vehicle defects using **RT-DETR**
* 🔎 Identify defects such as **scratches, dents, and cracks**
* 📊 Display detection confidence and defect information
* 🧠 Analyze defect severity using **RAG + LLM**
* 💬 Ask questions through an intelligent assistant
* 🎙️ Interact with the system using **voice commands**
* 📄 Generate inspection reports
* 🚘 Manage vehicles and inspection history
* 📈 Visualize inspection statistics

The project combines **Computer Vision, Deep Learning, Generative AI, RAG, Web Development, Mobile Development, and Database Management** into a complete inspection platform.

---

## 🎯 Objectives

The main objectives of DEFECTRA are:

1. Automate the visual inspection of vehicle bodywork.
2. Detect visible defects using Deep Learning.
3. Reduce the time required for manual inspection.
4. Provide an understandable diagnosis for detected defects.
5. Estimate defect severity using contextual technical documentation.
6. Provide maintenance recommendations through an LLM.
7. Centralize vehicles, inspections, and defect history.
8. Provide a modern mobile interface for inspectors and users.

---

## 🔍 Detected Defects

The current detection system focuses on three main categories:

| Defect     | Description                                    |
| ---------- | ---------------------------------------------- |
| 🔴 Scratch | Surface scratches or paint damage              |
| 🟠 Dent    | Deformation or indentation of the vehicle body |
| 🟡 Crack   | Visible cracks on external vehicle components  |

The detection model can be extended to support additional defect categories.

---

## 🧠 AI Pipeline

The DEFECTRA AI pipeline is organized as follows:

```text
                Vehicle Image
                     │
                     ▼
              ┌─────────────┐
              │   RT-DETR   │
              │ Detection   │
              └──────┬──────┘
                     │
                     ▼
            Detected Defects
                     │
                     ▼
              ┌─────────────┐
              │   Severity  │
              │  Analysis   │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │     RAG     │
              │ ChromaDB    │
              └──────┬──────┘
                     │
                     ▼
              ┌─────────────┐
              │     LLM     │
              │    Groq     │
              └──────┬──────┘
                     │
                     ▼
        Diagnosis & Recommendations
```

---

## 🏗️ System Architecture

DEFECTRA is composed of several services:

```text
┌───────────────────────────────┐
│       React Native App        │
│          Expo Mobile          │
└───────────────┬───────────────┘
                │
                │ REST API
                ▼
┌───────────────────────────────┐
│          Django API           │
│        Authentication         │
│   Vehicles / Inspections      │
│          PostgreSQL           │
└───────────────┬───────────────┘
                │
                ▼
┌───────────────────────────────┐
│          FastAPI AI           │
│   Detection / RAG / LLM       │
│     Severity / Voice          │
└───────────────┬───────────────┘
                │
        ┌───────┴────────┐
        ▼                ▼
┌──────────────┐  ┌──────────────┐
│   ChromaDB   │  │   Groq LLM   │
│  Vector DB   │  │ AI Assistant │
└──────────────┘  └──────────────┘
```

---

## 🛠️ Technologies

### 📱 Mobile Application

* React Native
* Expo
* JavaScript
* Expo Speech Recognition
* Expo Speech

### 🌐 Backend

* Python
* Django
* Django REST Framework
* FastAPI
* PostgreSQL

### 🤖 Artificial Intelligence

* Python
* PyTorch
* RT-DETR
* Computer Vision
* Deep Learning
* RAG
* LLM
* ChromaDB
* Groq

### 📊 Data & Visualization

* PostgreSQL
* REST APIs
* Statistical dashboards
* Inspection history

### 🔐 Security

* JWT Authentication
* Access / Refresh Tokens
* Environment variables

---

## 📂 Project Structure

```text
Defectra/
│
├── DefectraApp/                 # React Native / Expo application
│   ├── assets/
│   ├── components/
│   ├── screens/
│   ├── services/
│   └── ...
│
├── backend/                     # Django backend
│   ├── models/
│   ├── views/
│   ├── serializers/
│   ├── urls/
│   └── ...
│
├── ai_service/                  # FastAPI AI service
│   ├── routers/
│   ├── rag/
│   ├── prompts/
│   ├── services/
│   └── ...
│
├── requirements.txt
├── .gitignore
└── README.md
```

---

## ⚙️ Installation

### 1. Clone the repository

```bash
git clone https://github.com/BOUCHRATOR/Defectra.git
cd Defectra
```

### 2. Create a Python virtual environment

```bash
python -m venv venv
```

Activate it on Windows:

```bash
venv\Scripts\activate
```

### 3. Install Python dependencies

```bash
pip install -r requirements.txt
```

---

## 🔐 Environment Variables

Create a `.env` file for your local environment.

Example:

```env
SECRET_KEY=your_django_secret_key

DEBUG=True

DATABASE_NAME=data_defectra
DATABASE_USER=your_database_user
DATABASE_PASSWORD=your_database_password
DATABASE_HOST=localhost
DATABASE_PORT=5432

GROQ_API_KEY=your_groq_api_key
```

> ⚠️ Never commit your `.env` file or API keys to GitHub.

---

## 🗄️ Database

DEFECTRA uses **PostgreSQL** to store application data.

Main entities include:

```text
User
  │
  ├── Vehicle
  │      │
  │      └── Inspection
  │              │
  │              └── Defect
```

The system stores information such as:

* Vehicle brand
* Vehicle model
* Registration plate
* Vehicle image
* Inspection date
* Detected defects
* Defect confidence
* Defect severity
* Defect description
* Recommended solution
* Defect image

---

## 🧠 RAG System

DEFECTRA integrates a **Retrieval-Augmented Generation (RAG)** pipeline to provide contextual explanations.

The process is:

```text
Technical Documentation
          │
          ▼
      Chunking
          │
          ▼
      Embeddings
          │
          ▼
       ChromaDB
          │
          ▼
     Retriever
          │
          ▼
       Context
          │
          ▼
        LLM
          │
          ▼
Diagnosis / Recommendation
```

The RAG system retrieves relevant technical information before sending the context to the LLM.

This helps the system provide more contextual answers instead of relying only on the model's general knowledge.

---

## 🤖 Defect Detection

The computer vision module uses **RT-DETR** for object detection.

The model receives a vehicle image and returns:

```text
Defect Class
Bounding Box
Confidence Score
```

Example:

```text
Scratch
Confidence: 0.93
Bounding Box: [x1, y1, x2, y2]
```

The detected defects are then sent to the backend and stored in PostgreSQL.

---

## 🧠 Severity Analysis

After detection, DEFECTRA performs a severity analysis.

The system can classify defects into:

```text
LOW
MEDIUM
HIGH
```

The severity analysis combines:

* Detected defect type
* Detection information
* Technical documentation
* RAG retrieval
* LLM reasoning

The final result can include:

* Severity level
* Explanation
* Recommended action
* Additional information required

---

## 🎙️ Voice Assistant

DEFECTRA also includes a voice interaction module.

### Speech-to-Text

User voice:

```text
"Quels sont les défauts détectés ?"
```

is converted into text using speech recognition.

### AI Processing

The question is sent to the AI service and processed using the RAG/LLM pipeline.

### Text-to-Speech

The assistant converts the response back into speech.

```text
Voice Input
     ↓
Speech-to-Text
     ↓
FastAPI
     ↓
RAG + LLM
     ↓
Response
     ↓
Text-to-Speech
     ↓
Voice Output
```

---

## 📄 Inspection Reports

DEFECTRA can generate inspection reports containing information such as:

* Vehicle information
* Inspection date
* Detected defects
* Confidence scores
* Severity
* Diagnosis
* Recommendations

---

## 📊 Dashboard

The application provides an inspection dashboard with statistics such as:

* Vehicles consulted
* Number of inspections
* Number of detected defects
* Severe defects
* Recent inspections

The dashboard supports different time periods:

```text
Today
Week
Month
Quarter
Year
```

---

## 🔌 API Services

### Django API

Main responsibilities:

```text
Authentication
Vehicles
Inspections
Defects
Statistics
Reports
```

### FastAPI AI Service

Main responsibilities:

```text
Detection
RAG
Severity analysis
LLM
Voice
Question answering
Reports
```

---

## 🚀 Running the Project

### Start PostgreSQL

Make sure PostgreSQL is running and the database is configured.

### Start Django

```bash
python manage.py runserver 8000
```

### Start FastAPI

```bash
uvicorn main:app --reload --port 8001
```

### Start React Native / Expo

From the mobile application directory:

```bash
npm install
```

Then:

```bash
npx expo start
```

---

## 🧪 Testing

The AI service can be tested using Swagger UI:

```text
http://127.0.0.1:8001/docs
```

The Django API can be accessed through:

```text
http://127.0.0.1:8000/
```

---

## 📈 Future Improvements

Possible future developments include:

* 🔎 More vehicle defect classes
* 🎥 Real-time video defect detection
* 📱 Improved mobile experience
* 🌐 Cloud deployment
* ⚡ AI inference optimization
* 📊 Advanced analytics
* 🧠 Improved RAG pipeline
* 🔧 Automated maintenance estimation
* 🗣️ Multilingual voice assistant
* ☁️ Scalable AI infrastructure

---

## 👩‍💻 Author

**Bouchra TOR**

🎓 Engineering Student — Artificial Intelligence
🏫 École Nationale de l'Intelligence Artificielle et du Digital (ENIAD), Berkane, Morocco

### Areas of Interest

* Artificial Intelligence
* Computer Vision
* Deep Learning
* Generative AI
* RAG & LLMs
* Software Engineering
* Intelligent Systems

---

## 📜 Project

**DEFECTRA — Intelligent Vehicle Defect Inspection System**

Developed as an AI engineering project combining:

**Computer Vision + Deep Learning + RAG + LLM + Mobile Development + Backend Engineering**

---

## ⭐ Acknowledgments

Special thanks to the supervisors, collaborators, and everyone who contributed to the development and evaluation of the DEFECTRA project.
