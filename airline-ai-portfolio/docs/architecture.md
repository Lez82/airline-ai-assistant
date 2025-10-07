# System Architecture
┌─────────────────┐ ┌──────────────────┐ ┌─────────────────┐
│ Web Browser │◄──►│ Python Flask │◄──►│ RAG AI Engine │
│ │ │ Server │ │ │
│ HTML/CSS/JS │ │ • REST API │ │ • Smart Search │
│ Chat Interface│ │ • Web Server │ │ • FAQ Matching │
└─────────────────┘ └──────────────────┘ └─────────────────┘
│
▼
┌──────────────────┐
│ Data Layer │
│ • JSON Knowledge│
│ • Airline FAQs │
└──────────────────┘
