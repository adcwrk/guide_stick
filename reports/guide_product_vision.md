# GUIDE Product Vision

## Name

GUIDE: Generative Unified Intelligence for Disaster and Emergency Management

## Guiding Statement

"It is not just about the gear you have; it is about the decisions you make."

## Executive Summary

GUIDE is an offline-first emergency preparedness, disaster response, and operational decision-support platform designed to help individuals, families, preparedness groups, first responders, and organizations make informed decisions before, during, and after emergencies.

Unlike a traditional AI chatbot, GUIDE combines artificial intelligence, trusted emergency knowledge, household preparedness planning, inventory management, communications support, mapping, and incident management into a unified operational platform.

GUIDE's purpose is not simply to answer questions. Its purpose is to help users understand their situation, assess risks, identify resource gaps, and take appropriate action using trusted, source-grounded information.

## Core Mission

GUIDE transforms:

- Documents into operational intelligence
- Inventory into preparedness awareness
- Communications into coordinated action
- Data into decision support
- AI into a trusted emergency advisor

The platform is designed around one principle:

Reliable decisions save lives.

## What GUIDE Does

GUIDE serves as a preparedness advisor, emergency assistant, knowledge platform, planning tool, communications hub, and operational dashboard.

It helps users:

- Prepare for emergencies
- Assess risks
- Track resources
- Plan evacuations
- Manage incidents
- Coordinate communications
- Access trusted knowledge
- Understand complex situations
- Train and build preparedness skills

## Major Platform Components

### AI Workspace

The primary interaction point with GUIDE.

Users can ask questions such as:

- How much water should my family store?
- How long will my generator run?
- What should I do during a wildfire evacuation?
- How do I stop severe bleeding?
- What supplies am I missing?

GUIDE provides:

- Structured answers
- Retrieval-grounded information
- Source citations
- Risk assessments
- Recommended actions

### Household Intake and Preparedness Profile

GUIDE learns about the household or organization it is supporting.

The intake process captures:

- Household size
- Ages
- Medical conditions
- Medications
- Pets
- Power dependencies
- Mobility limitations
- Preparedness goals

Using this information, GUIDE can generate personalized recommendations and inventory calculations.

### Preparedness Planning

GUIDE helps users understand their readiness level.

Capabilities include:

- Readiness assessments
- Gap analysis
- Resource planning
- Evacuation planning
- Medical planning
- Power resilience planning
- Communications planning

### Inventory Management

GUIDE tracks preparedness resources and calculates requirements.

Inventory categories include:

- Water
- Food
- Medical supplies
- Medications
- Fuel
- Power systems
- Communications equipment
- Shelter supplies

GUIDE can determine:

- How much inventory is needed
- How long supplies will last
- What critical gaps exist

### Incident Management

GUIDE supports real-world emergency operations.

Incident types include:

- Medical emergencies
- Power outages
- Severe weather
- Wildfires
- Flooding
- Search and rescue
- Communications failures

Each incident can include:

- Status tracking
- Timelines
- Documentation
- Resource assignments
- AI-assisted recommendations

### Communications Center

GUIDE supports emergency communications planning and coordination.

Future capabilities include:

- Meshtastic integration
- Radio planning
- Message drafting
- Message compression
- Communications logging
- Network visualization

This enables GUIDE to support operations when traditional communications are unavailable.

### Maps and Situational Awareness

GUIDE provides geographic awareness through integrated mapping.

Users can visualize:

- Hazards
- Incidents
- Resources
- Shelters
- Hospitals
- Communications infrastructure
- Evacuation routes

Maps provide context that helps users understand what is happening and where resources are located.

### Knowledge Base

The Knowledge Base is the foundation of GUIDE.

Rather than relying solely on AI model knowledge, GUIDE retrieves information from trusted sources and organizational documents.

Sources may include:

- FEMA
- Ready.gov
- CERT
- CDC
- NOAA
- Red Cross
- Government publications
- User-provided SOPs
- Technical manuals
- Training resources
- Educational content

GUIDE transforms these documents into a searchable operational knowledge network.

### Learning and Training

GUIDE is not only a response platform. It is also a preparedness education platform.

Educational resources may include:

- Emergency preparedness training
- Technical skills
- Medical fundamentals
- Infrastructure knowledge
- Science and engineering concepts
- Community preparedness education

The goal is to build resilient and informed users before emergencies occur.

## Operating Architecture

GUIDE combines multiple systems to generate recommendations.

```text
User Input
  -> Emergency Classification
  -> Specialist Agents
  -> Knowledge Retrieval
  -> Safety Validation
  -> Structured Response
```

This architecture allows GUIDE to provide answers that are:

- Grounded
- Explainable
- Traceable
- Defensible
- Operationally useful

## Deployment Models

### GUIDE Base

Designed for:

- Families
- Preparedness enthusiasts
- Homesteads
- CERT teams

Capabilities:

- Offline AI
- Knowledge base
- Inventory management
- Preparedness planning
- Basic incident support

### GuideKit Base

Portable field deployment.

Includes:

- Local AI
- Offline maps
- Emergency knowledge library
- Inventory tools
- Communications planning

Runs entirely without internet access.

### GUIDE Pro

Designed for:

- Emergency managers
- Organizations
- Response teams
- Preparedness groups

Adds:

- Incident management
- Resource coordination
- Multi-user support
- Communications integration
- Advanced mapping
- Operational reporting

## Product Implications for This USB Build

The current USB build is the foundation for GUIDE Base and GuideKit Base.

Implemented foundation:

- Portable USB runtime
- Local Ollama backend
- Lightweight GUIDE WebUI
- LAN-accessible interface
- Offline IIAB library import
- Library browser API
- Health checks
- Backup scripts
- Linux/NUC support
- Apple Silicon support path

Near-term product direction:

- Complete ZIM content import
- Add trusted-source extraction
- Build ChromaDB RAG index
- Add Ask Library mode with citations
- Add household intake profile
- Add preparedness inventory schema
- Add readiness and gap calculations
- Add incident record model
- Add mapping and communications planning modules

## Vision

GUIDE is intended to become a comprehensive preparedness and emergency management platform that integrates artificial intelligence, trusted knowledge, operational planning, communications, mapping, and resource management into a single system.

The long-term goal is to provide individuals and organizations with the ability to prepare for, respond to, and recover from emergencies using informed, data-driven decision support, even when disconnected from the internet.

GUIDE is not simply an AI assistant.

GUIDE is a preparedness, response, and operational intelligence platform designed to help people make better decisions when those decisions matter most.
