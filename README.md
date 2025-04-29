# Open Memory - AI Memory Platform

English | [中文](./README_CN.md)

## Product Overview

### Vision
Build an AI memory platform that captures, organizes, and utilizes user knowledge and interaction history, helping users build personalized knowledge bases and enhance large model interaction experiences.

### Pain Points
- Need to use different chatbots across platforms during projects, requiring repeated context explanations
- Manual documentation organization, lacking automated knowledge recording mechanisms

### Use Cases
1. Content Creators
   - Using multiple large models across platforms during projects
   - Integrating reference materials, papers, documents, code, and design sketches
   - AI project assistant based on memory
   - Support for memory snapshot saving and restoration

2. Psychological Counseling
   - Continuous tracking of counseling records
   - Providing consistent counseling experience

## Core Values
- Build personalized AI memory library
- Avoid repeated explanations when communicating with chatbots
- Provide more coherent interaction experience
- Save and share valuable knowledge and insights
- Enhance AI's understanding of users' long-term interests and projects

## System Architecture

### System Components
1. Web Platform
   - RAG chatbot interface
   - Memory management
   - Memory history and rollback
   - Memory marketplace
   - User permission management

2. Browser Extension
   - Upload chat records
   - Multi-modal content collection (text, etc.)
   - Memory assistance tools

3. Memory Processing Engine
   - Multi-source data collection (chat records, text, PDF, images, code)
   - Data preprocessing
   - Memory integration

### Memory Types
1. Personal Trait Memory
   - User preferences
   - Background information
   - Usage habits

2. Project Memory
   - Project-related knowledge
   - Project-related materials

3. Knowledge Memory
   - Learning materials
   - Research papers
   - Personal notes

## Feature Design

### Data Collection
- Active upload: files, links, text
- Browser extension collection: web content
- Platform conversation automatic memory

### Memory Management
- Core features:
  - Memory creation, annotation, viewing, deletion
  - Memory retrieval
- Extended features:
  - Memory history tracking
  - Memory rollback

### Memory Application
- RAG-enhanced conversation
- Memory snapshots
- Memory marketplace

## Getting Started

### 1. Clone the Code
```bash
git clone https://github.com/RecallNet0526/ai-memory.git
cd ai-memory
```

### 2. Start Backend Services

#### Using Docker Compose
```bash
cd braindance_back
docker-compose up -d
```

#### Configure and Run Backend
```bash
pip install -r requirements.txt
python run_braindance.py --port 5002
```

### 3. Configure and Run Frontend
```bash
cd braindance_front
npm install
npm start
```

Visit http://localhost:3000 to start using the application.

## Project Structure
```
- braindance_back/ (Python Backend)
  - api.py (API endpoints)
  - chat.py (Chat functionality)
  - config.py (Configuration)
  - memory_store.py (Memory storage)
  - main.py (Entry point)
  - docker-compose.yaml (Docker configuration)

- braindance_front/ (React Frontend)
  - src/
    - components/ (UI components)
    - api/ (API services)
    - styles/ (Styling)
    - utils/ (Utility functions)

- your_memory/ (Memory snapshots)
```

We hope you enjoy using the application!