# Vanta Ledger: Architectural Design and Project Plan

## 1. Introduction

This document outlines the comprehensive architectural design and project plan for the Vanta Ledger system. Building upon previous discussions and research, this plan details the system's core components, their interactions, and the strategic approach to development and deployment. The Vanta Ledger is envisioned as a robust, self-hosted digital records and financial management system tailored for a family-owned group of companies in Kenya, specializing in government tenders and construction projects. It aims to address the current informal record-keeping practices by providing a centralized, efficient, and secure platform for managing projects, documents, and financial transactions.

## 2. High-Level Architecture Overview

The Vanta Ledger system is designed with a modular, layered architecture to ensure scalability, maintainability, and flexibility. It comprises several key components that work in concert to provide a comprehensive solution for digital record-keeping and business intelligence. The primary focus is on a self-hosted environment, leveraging open-source technologies to minimize initial costs while allowing for future expansion and integration with advanced capabilities.

### 2.1. Architectural Layers

The system can be broadly categorized into three main layers:

*   **Ingestion & Storage Layer:** Responsible for capturing and storing various types of documents and data from the real world, converting them into a digital format, and managing their storage.
*   **Understanding & Structuring Layer:** Focuses on processing the raw digital data, extracting meaningful information, and transforming it into structured data suitable for database storage and analysis. This layer incorporates advanced capabilities like Optical Character Recognition (OCR) and Natural Language Processing (NLP).
*   **Business Application & Reporting Layer:** Provides the user interface and core business logic, enabling users to interact with the system, manage projects and finances, and generate insightful reports and dashboards.

### 2.2. Core Components

At the heart of the Vanta Ledger are several interconnected components:

*   **FastAPI Backend:** The central application programming interface (API) that exposes the system's functionalities. It handles business logic, data validation, and interactions with the database and other services.
*   **PostgreSQL Database:** The primary data store for all structured information, including company details, project data, ledger entries, and document metadata. PostgreSQL is chosen for its robustness, scalability, and rich feature set.
*   **Paperless-ngx:** An open-source document management system that serves as the backbone for document ingestion, OCR, and initial metadata extraction. It processes scanned documents and provides a searchable archive.
*   **AI/NLP Microservice:** A planned separate service responsible for advanced document analysis, including extracting specific fields from OCR text, categorizing documents, and potentially identifying anomalies. This service will leverage libraries like spaCy and potentially local Large Language Models (LLMs) like Llama2.
*   **React Frontend (Web):** The primary user interface for desktop and web access. It provides a rich, interactive dashboard for managing companies, projects, documents, and financial data.
*   **Flutter Frontend (Mobile):** A cross-platform mobile application designed for on-the-go access, enabling users to manage transactions, view reports, and interact with the system from their mobile devices.
*   **Local File Storage:** A structured file system on the office PCs for storing the actual document files, linked to the database via file paths.
*   **Deployment Environment:** The system will be self-hosted on local office PCs, likely running Ubuntu, with Docker Compose for containerization and simplified deployment.




## 3. Ingestion & Storage Layer

This layer is responsible for the entry point of all data into the Vanta Ledger system, primarily focusing on documents. Given the informal nature of current record-keeping and the prevalence of physical documents, a robust and user-friendly ingestion mechanism is crucial. The goal is to seamlessly convert physical and digital documents into a structured, searchable format within the system.

### 3.1. Document Sources

Documents entering the system can originate from various sources:

*   **Scanned Physical Documents:** Traditional paper documents (e.g., tender documents, contracts, invoices, certificates) will be scanned into digital formats (PDF, JPEG).
*   **Digital Documents:** Electronically generated documents (e.g., Word, Excel, PDF) received via email or other digital channels.
*   **Mobile Captures:** Photos of receipts, site progress, or other relevant information captured directly from mobile devices.

### 3.2. Key Components and Workflow

#### 3.2.1. Paperless-ngx

Paperless-ngx serves as the primary engine for document ingestion and initial processing. It is an open-source document management system that automates the process of digitizing and archiving documents. Its key functionalities include:

*   **Document Consumption:** Paperless-ngx monitors designated 


input folders for new documents. Once a document is detected, it is automatically processed.
*   **Optical Character Recognition (OCR):** It performs OCR on scanned documents, converting images of text into machine-readable text. This is critical for making scanned documents searchable.
*   **Metadata Extraction:** Paperless-ngx can automatically extract basic metadata from documents, such as creation date, file type, and potentially some inferred tags.
*   **Tagging and Archiving:** Documents are tagged and organized within Paperless-ngx, creating a searchable archive. This initial tagging can be manual or rule-based.
*   **API Access:** Paperless-ngx provides a robust API that allows external applications (like our FastAPI backend) to interact with its document repository, retrieve OCR text, and access metadata.

#### 3.2.2. Syncthing

To facilitate the seamless transfer of documents from various user devices (e.g., other office PCs, mobile phones) to the Paperless-ngx input folder, Syncthing will be utilized. Syncthing is a free, open-source, peer-to-peer file synchronization application. It ensures that files are automatically synchronized between designated folders on multiple devices, providing a robust and decentralized way to collect documents.

*   **Decentralized Sync:** Unlike cloud-based sync services, Syncthing operates directly between devices, ensuring data privacy and control remain within the local network.
*   **Real-time Synchronization:** Changes to files are synchronized almost instantly, ensuring that documents captured on one device quickly become available for processing by Paperless-ngx.
*   **Version Control (Basic):** While Paperless-ngx handles document versioning within its system, Syncthing can also maintain basic file versions on the file system, providing an additional layer of data safety.

#### 3.2.3. Mobile Uploads

For mobile-first document capture, the Flutter application will include functionality to directly upload images (e.g., photos of receipts, site progress) or PDF documents. These uploads will be directed to a designated folder that Syncthing monitors, or directly to the FastAPI backend which then pushes them to Paperless-ngx for processing. This ensures that field-generated documents are quickly integrated into the system.

#### 3.2.4. Local File Storage Organization

All original document files, along with their OCR-processed versions, will be stored on the local office PCs. A structured folder hierarchy will be implemented to ensure logical organization and easy retrieval, even outside the Vanta Ledger application. The proposed structure is:

`/docs/<company_name>/<project_name>/<year>_<doc_type>_<filename>_v<version>.pdf`

*   **`<company_name>`:** Top-level folder for each of the ~10 companies within the group.
*   **`<project_name>`:** Sub-folder for each project associated with a company.
*   **`<year>`:** Year of document creation or relevance, aiding chronological organization.
*   **`<doc_type>`:** Categorization of the document (e.g., `letter_of_award`, `tax_compliance`, `invoice`, `contract`). This will be crucial for quick identification and search.
*   **`<filename>`:** Original or descriptive filename.
*   **`v<version>`:** Version indicator for documents that undergo revisions.

This structured approach ensures that even if the database is temporarily unavailable, documents can still be located and understood based on their file path. The database will store references to these file paths, linking the structured metadata to the actual document files.




## 4. Understanding & Structuring Layer

This layer is the intelligence hub of the Vanta Ledger, transforming raw OCR text from Paperless-ngx into structured, actionable data that populates the core database. Its primary function is to extract specific entities and relationships from unstructured document content, making the information queryable and usable for reporting and analysis.

### 4.1. The AI/NLP Microservice

The core component of this layer is a dedicated AI/NLP microservice, designed as a separate FastAPI application. This separation ensures modularity, allowing for independent scaling and updates of the NLP capabilities without affecting the main Vanta Ledger backend. It will consume OCR text from Paperless-ngx or directly from the main backend and return structured data.

#### 4.1.1. Key Functionalities

*   **Entity Extraction:** Identifying and extracting key pieces of information from the document text, such as:
    *   **Project Details:** Project name, client name, project value, start/end dates, contract numbers.
    *   **Company Details:** Company names, registration numbers, tax IDs.
    *   **Financial Data:** Amounts (income, expense), dates of transactions, invoice numbers, payment terms.
    *   **Document-Specific Data:** Expiry dates for certificates (NCA, Tax Compliance, CR12), award dates for letters of award.
*   **Document Classification:** Categorizing documents based on their content (e.g., Letter of Award, Invoice, Certificate, Contract, Tender Document). This can be rule-based (keywords) or machine learning-based.
*   **Relationship Extraction:** Identifying relationships between entities, such as linking an invoice to a specific project or a certificate to a particular company.
*   **Data Normalization:** Standardizing extracted data (e.g., date formats, currency symbols) to ensure consistency in the database.

#### 4.1.2. Technology Stack

*   **FastAPI:** Used to build the microservice API, providing endpoints for text processing and data extraction.
*   **spaCy:** A powerful open-source library for advanced Natural Language Processing in Python. It will be used for:
    *   **Named Entity Recognition (NER):** Identifying and classifying named entities (e.g., organizations, dates, monetary values).
    *   **Rule-based Matching:** Defining custom rules (e.g., regular expressions, token patterns) to extract specific information relevant to Kenyan tender documents and construction contracts.
*   **Local LLMs (e.g., Llama2 via Ollama - future consideration):** For more complex tasks like summarization, sentiment analysis, or more nuanced entity extraction, a locally hosted Large Language Model could be integrated. This would be a Phase 2 or 3 feature, ensuring cost-effectiveness and data privacy.

### 4.2. Integration with Vanta Ledger Backend

The AI/NLP microservice will communicate with the main Vanta Ledger FastAPI backend. The workflow will be as follows:

1.  **Document Ingestion:** Paperless-ngx processes a document, performs OCR, and makes the OCR text available via its API.
2.  **Trigger Extraction:** The Vanta Ledger backend (or a dedicated background worker) will retrieve the OCR text from Paperless-ngx and send it to the AI/NLP microservice via an API call (e.g., `POST /extract`).
3.  **Data Extraction:** The AI/NLP microservice processes the text using spaCy and its defined rules/models, extracting structured data.
4.  **Data Return:** The microservice returns the extracted structured data (e.g., JSON object) to the Vanta Ledger backend.
5.  **Database Storage:** The Vanta Ledger backend then takes this structured data and populates the relevant fields in its PostgreSQL database (e.g., `projects` table, `documents` table, `ledger_entries` table, and a dedicated `document_analysis` table for raw extracted metadata).

### 4.3. Document Analysis Table

A dedicated `DocumentAnalysis` table in the PostgreSQL database will store the raw and processed extracted metadata from documents. This table will be linked to the `documents` table and will serve as an audit trail for extracted information, allowing for re-evaluation or refinement of extraction rules in the future. It will also provide a rich dataset for future advanced analytics and AI model training.

### 4.4. Challenges and Considerations

*   **Accuracy of Extraction:** The accuracy of OCR and NLP extraction can vary, especially with scanned documents or complex layouts. Manual review and correction mechanisms will be necessary.
*   **Rule Maintenance:** As document types evolve or new requirements emerge, the extraction rules (spaCy patterns, regexes) will need to be updated and maintained.
*   **Performance:** Processing large volumes of documents with NLP can be computationally intensive. The microservice design allows for scaling this component independently if needed.
*   **Domain Specificity:** The NLP models and rules will need to be highly tailored to the specific language and terminology used in Kenyan tendering and construction documents to achieve high accuracy.




## 5. Business Application & Reporting Layer

This layer represents the user-facing part of the Vanta Ledger system, providing the interface for interaction, data management, and insights. It encompasses the core business logic, data presentation, and reporting functionalities, ensuring that the structured data from the underlying layers is accessible and actionable for the family business.

### 5.1. FastAPI Backend (Core Business Logic)

The FastAPI backend serves as the central hub, orchestrating interactions between the database, the AI/NLP microservice, and the various frontend applications. It is built with a modular design, separating concerns into distinct routers and services.

#### 5.1.1. Core Modules and Data Models

The backend will manage the following key entities, each with its corresponding SQLAlchemy model and Pydantic schemas for data validation and serialization:

*   **Companies:** Represents each of the family-owned companies. This is the top-level organizational unit.
    *   **SQLAlchemy Model (`src/vanta_ledger/models/company.py`):**
        ```python
        class Company(Base):
            __tablename__ = 'companies'
            id = Column(Integer, primary_key=True, autoincrement=True)
            name = Column(String(255), nullable=False)
            description = Column(Text)
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
            projects = relationship("Project", back_populates="company")
            ledger_entries = relationship("LedgerEntry", back_populates="company")
            documents = relationship("Document", back_populates="company")
        ```
    *   **Pydantic Schemas (`src/vanta_ledger/schemas/company.py`):** `CompanyCreate`, `CompanyRead`.
    *   **API Endpoints (`src/vanta_ledger/routers/companies.py`):** CRUD operations (`GET /companies`, `GET /companies/{id}`, `POST /companies`, `PUT /companies/{id}`, `DELETE /companies/{id}`).

*   **Projects:** Represents individual construction, supply, or management projects undertaken by a company. Projects are linked to a specific company.
    *   **SQLAlchemy Model (`src/vanta_ledger/models/project.py`):**
        ```python
        class Project(Base):
            __tablename__ = 'projects'
            id = Column(Integer, primary_key=True, autoincrement=True)
            company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
            name = Column(String(255), nullable=False)
            client = Column(String(255))
            value = Column(Float)
            start_date = Column(Date)
            end_date = Column(Date)
            status = Column(String(50)) # e.g., 'active', 'completed', 'pending', 'cancelled'
            description = Column(Text)
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            updated_at = Column(DateTime, default=datetime.datetime.utcnow, onupdate=datetime.datetime.utcnow)
            company = relationship('Company', back_populates='projects')
            ledger_entries = relationship('LedgerEntry', back_populates='project')
            documents = relationship('Document', back_populates='project')
        ```
    *   **Pydantic Schemas (`src/vanta_ledger/schemas/project.py`):** `ProjectCreate`, `ProjectRead` (including nested `CompanyInfo`).
    *   **API Endpoints (`src/vanta_ledger/routers/projects.py`):** CRUD operations (`GET /projects`, `GET /projects/{id}`, `GET /companies/{company_id}/projects`, `POST /projects`, `PUT /projects/{id}`, `DELETE /projects/{id}`).

*   **Documents:** Stores metadata about documents, linking them to projects and companies. This module will also handle file uploads and versioning.
    *   **SQLAlchemy Model (`src/vanta_ledger/models/document.py`):**
        ```python
        class Document(Base):
            __tablename__ = "documents"
            id = Column(Integer, primary_key=True, index=True)
            paperless_id = Column(Integer, unique=True, nullable=True) # Link to Paperless-ngx document ID
            company_id = Column(Integer, ForeignKey("companies.id"))
            project_id = Column(Integer, ForeignKey("projects.id"), nullable=True)
            filename = Column(String(255), nullable=False)
            file_path = Column(String(512), nullable=False) # Path to the actual file on local storage
            doc_type = Column(String(100)) # e.g., 'Letter of Award', 'Invoice', 'NCA Certificate'
            version_number = Column(Integer, default=1)
            uploaded_at = Column(DateTime, default=datetime.datetime.utcnow)
            uploader_id = Column(Integer, ForeignKey('users.id'))
            notes = Column(Text)
            expiry_date = Column(Date, nullable=True) # For certificates, compliance docs
            # Relationships
            company = relationship("Company", back_populates="documents")
            project = relationship("Project", back_populates="documents")
            uploader = relationship("User", back_populates="uploaded_documents")
            document_analysis = relationship("DocumentAnalysis", back_populates="document", uselist=False)
        ```
    *   **Pydantic Schemas (`src/vanta_ledger/schemas/document.py`):** `DocumentCreate`, `DocumentRead`, `DocumentUpload`.
    *   **API Endpoints (`src/vanta_ledger/routers/documents.py`):** `POST /documents/upload` (for file upload), `GET /documents`, `GET /documents/{id}`, `PUT /documents/{id}`, `DELETE /documents/{id}`, `GET /documents/{id}/versions`.

*   **Ledger Entries:** Records all financial transactions (income, expenses, owner withdrawals), linking them to specific companies and projects.
    *   **SQLAlchemy Model (`src/vanta_ledger/models/ledger.py`):**
        ```python
        class LedgerEntry(Base):
            __tablename__ = 'ledger_entries'
            id = Column(Integer, primary_key=True, autoincrement=True)
            company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
            project_id = Column(Integer, ForeignKey('projects.id'), nullable=True)
            type = Column(String(50), nullable=False)  # 'income', 'expense', 'withdrawal'
            amount = Column(Float, nullable=False)
            date = Column(Date, nullable=False)
            description = Column(Text)
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            uploaded_by = Column(Integer, ForeignKey('users.id'))
            # Relationships
            company = relationship('Company', back_populates='ledger_entries')
            project = relationship('Project', back_populates='ledger_entries')
            uploader = relationship('User', back_populates='uploaded_ledger_entries')
        ```
    *   **Pydantic Schemas (`src/vanta_ledger/schemas/ledger.py`):** `LedgerEntryCreate`, `LedgerEntryRead`.
    *   **API Endpoints (`src/vanta_ledger/routers/ledger.py`):** CRUD operations (`GET /ledger`, `GET /ledger/{id}`, `POST /ledger`, `PUT /ledger/{id}`, `DELETE /ledger/{id}`), and filtered views (`GET /companies/{company_id}/ledger`, `GET /projects/{project_id}/ledger`).

*   **Users & Authentication:** Manages user accounts and access control. Initially, a simple admin user system for the 3 heads, with potential for more granular roles (e.g., viewer, staff) in the future.
    *   **SQLAlchemy Model (`src/vanta_ledger/models/user.py`):**
        ```python
        class User(Base):
            __tablename__ = 'users'
            id = Column(Integer, primary_key=True, autoincrement=True)
            name = Column(String(255), nullable=False)
            email = Column(String(255), unique=True, nullable=False)
            password_hash = Column(String(255), nullable=False)
            role = Column(String(50), default='admin') # 'admin', 'viewer', 'staff'
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            last_login = Column(DateTime)
            uploaded_documents = relationship("Document", back_populates="uploader")
            uploaded_ledger_entries = relationship("LedgerEntry", back_populates="uploader")
        ```
    *   **Pydantic Schemas (`src/vanta_ledger/schemas/user.py`):** `UserCreate`, `UserRead`, `UserLogin`.
    *   **API Endpoints (`src/vanta_ledger/routers/users.py`):** `POST /auth/login`, `GET /users/me`, `POST /users` (for admin to create users).

*   **Subcontractors (Future Module):** To track external partners involved in projects.
    *   **SQLAlchemy Model (`src/vanta_ledger/models/subcontractor.py`):**
        ```python
        class Subcontractor(Base):
            __tablename__ = 'subcontractors'
            id = Column(Integer, primary_key=True, autoincrement=True)
            project_id = Column(Integer, ForeignKey('projects.id'))
            name = Column(String(255), nullable=False)
            contact_person = Column(String(255))
            phone = Column(String(50))
            email = Column(String(255))
            services = Column(Text) # Description of services provided
            contract_value = Column(Float)
            start_date = Column(Date)
            end_date = Column(Date)
            status = Column(String(50)) # e.g., 'active', 'completed', 'pending'
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            project = relationship('Project', backref='subcontractors')
        ```
    *   **Pydantic Schemas (`src/vanta_ledger/schemas/subcontractor.py`):** `SubcontractorCreate`, `SubcontractorRead`.
    *   **API Endpoints (`src/vanta_ledger/routers/subcontractors.py`):** CRUD operations.

*   **Tender Pipeline (Future Module):** To manage the tender application process.
    *   **SQLAlchemy Model (`src/vanta_ledger/models/tender.py`):**
        ```python
        class Tender(Base):
            __tablename__ = 'tenders'
            id = Column(Integer, primary_key=True, autoincrement=True)
            company_id = Column(Integer, ForeignKey('companies.id'), nullable=False)
            tender_number = Column(String(255), unique=True, nullable=False)
            client_name = Column(String(255))
            submission_date = Column(Date)
            status = Column(String(50)) # e.g., 'pending', 'won', 'lost', 'withdrawn'
            amount = Column(Float) # Bid amount
            documents_required = Column(Text) # Checklist or description of required docs
            notes = Column(Text)
            created_at = Column(DateTime, default=datetime.datetime.utcnow)
            company = relationship('Company', backref='tenders')
        ```
    *   **Pydantic Schemas (`src/vanta_ledger/schemas/tender.py`):** `TenderCreate`, `TenderRead`.
    *   **API Endpoints (`src/vanta_ledger/routers/tenders.py`):** CRUD operations.

#### 5.1.2. API Design Principles

*   **RESTful:** Adhering to REST principles for clear, predictable API endpoints.
*   **Modular Routers:** Each major entity (Companies, Projects, Documents, Ledger, Users, etc.) will have its own FastAPI router, promoting code organization and maintainability.
*   **Dependency Injection:** Utilizing FastAPI's dependency injection system for database sessions (`get_db`) and authentication.
*   **Error Handling:** Consistent error responses using FastAPI's `HTTPException`.
*   **Pydantic for Validation:** Leveraging Pydantic for request body validation and response serialization, ensuring data integrity and clear API contracts.

### 5.2. Frontend Applications

The Vanta Ledger will provide two primary frontend interfaces to cater to different user needs and access patterns: a web-based React application for desktop use and a cross-platform Flutter application for mobile devices.

#### 5.2.1. React Frontend (Web Dashboard)

This will be the main interface for users accessing the system from desktop computers within the office LAN. It will provide a comprehensive dashboard and detailed views for managing all aspects of the business.

*   **Technology:** React with Vite for fast development and a modern build setup.
*   **UI/UX Principles:** Clean, intuitive, and responsive design, inspired by modern business applications like Notion. Emphasis on clarity, ease of navigation, and quick access to critical information.
*   **Key Features:**
    *   **Dashboard:** Overview of key metrics (total income/expenses, active projects, upcoming deadlines, document expiry alerts).
    *   **Company & Project Management:** Detailed views for each company and its associated projects, with the ability to add, edit, and archive entries.
    *   **Document Library:** Browse, search, upload, and download documents. View document versions and associated metadata. Integration with Paperless-ngx for direct access to OCR text and advanced search.
    *   **Ledger Management:** Enter and view income, expenses, and owner withdrawals. Filter by company, project, date range, and category. Basic financial reporting.
    *   **User Management:** Simple interface for managing user accounts and roles (for administrators).
    *   **Reports & Exports:** Generate printable PDF reports (e.g., project summaries, company financial statements, tender packs) and export data to Excel/CSV.
*   **API Integration:** All frontend components will consume data from the FastAPI backend via RESTful API calls. Initial implementation will use `fetch` or `axios` for API interactions.
*   **Routing:** React Router will manage client-side navigation between different views (e.g., `/companies`, `/projects`, `/documents`, `/ledger`).

#### 5.2.2. Flutter Frontend (Mobile Application)

The Flutter application will provide a native-like experience on Android, iOS, and potentially desktop platforms, optimized for mobile use cases such as on-site data entry and quick lookups.

*   **Technology:** Flutter, enabling a single codebase for multiple platforms.
*   **UI/UX Principles:** Mobile-first design, emphasizing quick actions, clear data presentation on smaller screens, and offline capabilities.
*   **Key Features:**
    *   **Transaction Management:** Streamlined interface for quickly adding income and expense entries, potentially with photo capture for receipts.
    *   **Basic Project/Company View:** Quick access to project status and company overview.
    *   **Offline-First:** Utilizing a local database (e.g., sqflite, Isar, or Drift) to allow users to record data even without an internet connection. Data will be synchronized with the central PostgreSQL database when connectivity is restored.
    *   **Biometric/PIN Security:** Enhanced security for mobile access.
    *   **Basic Reports:** Simplified views of financial summaries and project progress.
*   **Backend Sync:** A synchronization mechanism will be implemented to ensure data consistency between the local mobile database and the central PostgreSQL database. This will involve handling conflicts and ensuring data integrity during sync operations.

### 5.3. Reporting and Dashboards

Reporting is a critical aspect of the Vanta Ledger, enabling the family heads to gain insights into their business operations and prepare necessary documentation for tenders and compliance.

*   **In-App Reports:** The React frontend will offer various built-in reports:
    *   **Profit & Loss Statements:** Per company, per project, and consolidated.
    *   **Project Summaries:** Detailed reports for individual projects, including financial performance, document lists, and key milestones.
    *   **Company Profiles:** Comprehensive documents summarizing a company's past projects, key financial figures, and relevant certifications (for tender submissions).
    *   **Document Expiry Reports:** Lists of certificates and compliance documents nearing their expiry dates.
*   **Export Formats:** Reports will be exportable to PDF for printing and official submissions, and to Excel/CSV for further analysis by accountants or for government forms.
*   **Metabase (Future Consideration):** For more advanced business intelligence and custom dashboards, an open-source BI tool like Metabase could be integrated. Metabase can connect directly to the PostgreSQL database and allow users to create interactive dashboards and reports without writing SQL queries. This would provide deeper analytical capabilities for identifying trends, anomalies, and performance metrics across all companies and projects.




## 6. Infrastructure and Deployment

The Vanta Ledger system is designed for self-hosting within the family business's existing office infrastructure. This approach prioritizes data privacy, cost-effectiveness (avoiding recurring SaaS fees), and full control over the system. The deployment strategy focuses on leveraging existing hardware and open-source tools to create a robust and maintainable environment.

### 6.1. Self-Hosting Strategy

The core principle is to run the entire Vanta Ledger stack on local office computers, accessible via the Local Area Network (LAN). This eliminates the need for external cloud hosting services, keeping all sensitive business data within the physical control of the family.

*   **Local Network Access:** All frontend applications (React web dashboard, Flutter desktop app) will connect to the FastAPI backend and PostgreSQL database over the local office network. Mobile devices (phones, tablets) will also access the system when connected to the office Wi-Fi.
*   **No Internet Exposure (Default):** By default, the system will not be exposed to the public internet, significantly reducing the attack surface and enhancing security. If remote access is required in the future, a secure VPN solution would be recommended.

### 6.2. Hardware Considerations

The existing office PCs will serve as the foundation for the Vanta Ledger infrastructure. While the current hardware (e.g., i5-650, 4GB RAM, HDD) is functional, strategic upgrades are recommended to ensure optimal performance and reliability.

*   **Dedicated Server PC:** Ideally, one of the office PCs will be designated as the primary server, hosting the PostgreSQL database, FastAPI backend, AI/NLP microservice, and Paperless-ngx. This centralizes the core services and prevents performance degradation on user workstations.
*   **Recommended Upgrades for Server PC:**
    *   **Solid State Drive (SSD):** Upgrading from a Hard Disk Drive (HDD) to an SSD is the most impactful upgrade for performance. SSDs offer significantly faster read/write speeds, drastically improving database operations, application startup times, and overall system responsiveness. A 240GB or 480GB SSD would be sufficient for the OS, applications, and initial document storage.
    *   **Random Access Memory (RAM):** Increasing RAM to 8GB or 16GB (from 4GB) will provide more headroom for PostgreSQL, FastAPI, and Paperless-ngx, especially when processing large documents or handling multiple concurrent users. This reduces reliance on swap space, which is much slower.
*   **Operating System:** While Windows is currently in use, installing a Linux distribution (e.g., Ubuntu Server LTS) on the dedicated server PC is highly recommended. Linux offers:
    *   **Lower Resource Consumption:** Uses significantly less RAM and CPU compared to Windows, freeing up resources for the Vanta Ledger applications.
    *   **Stability and Reliability:** Known for its stability and suitability for server environments.
    *   **Security:** Generally considered more secure out-of-the-box for server applications.
    *   **Ease of Automation:** Simplifies the creation of backup scripts and other automation tasks using shell scripting (e.g., cron jobs).

### 6.3. Containerization with Docker Compose

Docker Compose will be the primary tool for deploying and managing the Vanta Ledger services. Containerization offers numerous benefits for development, deployment, and maintenance:

*   **Simplified Deployment:** Defines all services (backend, database, AI extractor, Paperless-ngx) and their dependencies in a single `docker-compose.yml` file, allowing the entire stack to be deployed with a single command (`docker-compose up`).
*   **Environment Consistency:** Ensures that the development, testing, and production environments are identical, reducing 


inconsistencies and 


reducing "works on my machine" issues.
*   **Isolation:** Each service runs in its own isolated container, preventing conflicts between dependencies and ensuring a clean environment.
*   **Scalability:** While initially running on a single machine, Docker Compose makes it easier to scale individual services if needed in the future.
*   **Portability:** The entire application stack can be easily moved to another machine or server with Docker installed.

#### 6.3.1. `docker-compose.yml` Structure (Draft)

A sample `docker-compose.yml` will define the following services:

```yaml
version: '3.8'
services:
  backend:
    build: .
    command: uvicorn src.vanta_ledger.main:app --host 0.0.0.0 --port 8500
    volumes:
      - .:/app
      - ./docs_data:/app/docs_data # Mount for document storage
    environment:
      - DATABASE_URL=postgresql://vanta_user:vanta_password@postgres/vanta_ledger
    depends_on:
      - postgres
    ports:
      - "8500:8500" # Expose backend port

  postgres:
    image: postgres:15
    environment:
      POSTGRES_DB: vanta_ledger
      POSTGRES_USER: vanta_user
      POSTGRES_PASSWORD: vanta_password
    volumes:
      - pgdata:/var/lib/postgresql/data # Persistent data volume

  ai_extractor:
    build: ./src/ai_extractor
    command: uvicorn main:app --host 0.0.0.0 --port 8600
    volumes:
      - ./src/ai_extractor:/app
    depends_on:
      - backend # Or directly by the backend
    ports:
      - "8600:8600" # Expose AI extractor port

  paperless:
    image: paperlessngx/paperless-ngx:latest
    environment:
      PAPERLESS_CONSUMER_DIR: /consume
      PAPERLESS_DATA_DIR: /data
      PAPERLESS_MEDIA_ROOT: /media
      PAPERLESS_DB_URL: postgresql://paperless_user:paperless_password@paperless_db/paperless
    volumes:
      - paperless_consume:/consume
      - paperless_data:/data
      - paperless_media:/media
    depends_on:
      - paperless_db
    ports:
      - "8000:8000"

  paperless_db:
    image: postgres:15
    environment:
      POSTGRES_DB: paperless
      POSTGRES_USER: paperless_user
      POSTGRES_PASSWORD: paperless_password
    volumes:
      - paperless_pgdata:/var/lib/postgresql/data

volumes:
  pgdata:
  paperless_consume:
  paperless_data:
  paperless_media:
  paperless_pgdata:
```

### 6.4. Database Setup and Migrations

PostgreSQL will be the relational database management system. Its robust features, ACID compliance, and strong community support make it an ideal choice for the Vanta Ledger. Database schema management will be handled using Alembic.

*   **Alembic:** A lightweight database migration tool for SQLAlchemy. It allows for version control of the database schema, enabling controlled evolution of the database as the application develops. This is crucial for maintaining data integrity and facilitating deployments.
    *   **Initialization:** `alembic init alembic` will create the necessary directory structure and configuration files.
    *   **Migration Generation:** `alembic revision --autogenerate -m "Initial tables: companies, projects, ledger_entries, documents"` will automatically generate a migration script based on changes detected in the SQLAlchemy models.
    *   **Applying Migrations:** `alembic upgrade head` will apply all pending migrations to the database, bringing the schema up to date.
*   **Database Credentials:** All database connection details (username, password, database name) will be managed via environment variables, loaded from a `.env` file, ensuring sensitive information is not hardcoded in the application. This also allows for easy configuration changes across different environments (development, production).




## 7. Security and Backup Strategies

Given the sensitive nature of financial and project data, robust security and backup strategies are paramount for the Vanta Ledger system. As a self-hosted, LAN-only system, the focus shifts from cloud-provider security to local infrastructure and operational best practices.

### 7.1. Security Measures

*   **Network Security (LAN-only Access):** By default, the Vanta Ledger will not be exposed to the public internet. Access will be restricted to devices within the local office network. This significantly reduces the attack surface from external threats. If remote access is ever required, it should be implemented via a secure Virtual Private Network (VPN) solution, ensuring encrypted and authenticated connections.
*   **Firewall Configuration:** The server hosting the Vanta Ledger should have a properly configured firewall (e.g., `ufw` on Ubuntu) to restrict incoming and outgoing traffic to only necessary ports (e.g., PostgreSQL port, FastAPI port, Paperless-ngx port). This prevents unauthorized access to services running on the server.
*   **User Authentication and Authorization:**
    *   **Strong Passwords:** Users will be required to set strong, unique passwords. Password hashes will be stored in the database, never plain text.
    *   **Role-Based Access Control (RBAC):** Initially, a simple role system (e.g., `admin`, `viewer`) will be implemented. `admin` users (the 3 heads) will have full access, while `viewer` roles (if introduced later for staff) will have read-only access to specific modules or data. This ensures that users only access information relevant to their roles.
    *   **Audit Logs:** The system will implement comprehensive audit logging to track user actions (e.g., who created/modified/deleted a project, document, or ledger entry, and when). This provides a clear trail for accountability and forensic analysis if needed.
*   **Data Encryption (at Rest):** While the primary storage is local, sensitive data within the PostgreSQL database can be encrypted at rest using database-level encryption features or file-system encryption (e.g., LUKS for Linux partitions). This protects data even if the physical storage device is compromised.
*   **Secure Coding Practices:** The FastAPI backend will adhere to secure coding practices, including input validation, protection against SQL injection, cross-site scripting (XSS), and other common web vulnerabilities.
*   **Regular Updates:** The underlying operating system, Docker, PostgreSQL, and all Python/Node.js dependencies will be kept up-to-date to patch security vulnerabilities.

### 7.2. Backup and Disaster Recovery

Data loss can be catastrophic for any business. A robust backup strategy is essential to protect the Vanta Ledger data against hardware failures, accidental deletions, or other unforeseen events.

*   **Automated Daily Backups:**
    *   **Database Backups:** A daily automated script (e.g., a cron job on Linux) will perform a `pg_dump` of the PostgreSQL database. This creates a logical backup of the entire database schema and data.
    *   **Document File Backups:** The `docs` folder (containing all original document files) will also be backed up daily. This can be done using `rsync` for incremental backups, ensuring only changed or new files are copied.
*   **Backup Destinations:**
    *   **Local Redundancy:** Backups will initially be stored on a separate physical drive within the office (e.g., the second working PC, or a dedicated external hard drive). This provides immediate recovery in case of primary server failure.
    *   **Offsite Backups (Optional but Recommended):** For disaster recovery (e.g., fire, theft), offsite backups are crucial. This can involve syncing encrypted backup archives to a cloud storage service (e.g., Google Drive, MEGA, Backblaze) or physically rotating external drives to an offsite location. Encryption of backups before sending them offsite is mandatory to maintain data privacy.
*   **Backup Retention Policy:** A clear retention policy will be defined (e.g., keep daily backups for 7 days, weekly backups for 4 weeks, monthly backups for 6 months). This balances storage requirements with recovery needs.
*   **Disaster Recovery Plan:** A simple, documented plan will outline the steps required to restore the Vanta Ledger system from backups in case of a catastrophic failure. This includes instructions for setting up a new server, restoring the database, and recovering document files.
*   **Regular Testing:** Backups will be periodically tested by performing a full restore to a separate environment. This verifies the integrity of the backups and the effectiveness of the recovery process.

By implementing these security and backup measures, the Vanta Ledger system will provide a secure and resilient platform for managing the family business's critical data, ensuring business continuity and peace of mind.




## 8. Detailed Module Specifications

This section provides a more granular breakdown of each core module within the Vanta Ledger system, detailing their functionalities, key data points, and interactions between the backend API and frontend interfaces. The aim is to provide a clear blueprint for development, ensuring all necessary features are captured and integrated seamlessly.

### 8.1. Companies Module

**Purpose:** To manage the various companies under the family group's umbrella, serving as the primary organizational unit for projects, documents, and financial records.

**Key Functionalities:**

*   **Create/Read/Update/Delete (CRUD) Company Profiles:** Allow administrators to add new companies, view existing ones, modify their details, and archive/delete them.
*   **Company Overview:** Provide a dashboard or summary view for each company, showing aggregated data like total projects, total income/expenses, and key documents.

**Backend (FastAPI):**

*   **Model:** `Company` (as defined in Section 5.1.1).
*   **Schemas:** `CompanyCreate` (for creating new companies), `CompanyRead` (for reading company data, including relationships to projects, documents, and ledger entries).
*   **Router:** `src/vanta_ledger/routers/companies.py`.
    *   `POST /companies`: Create a new company.
    *   `GET /companies`: Retrieve a list of all companies.
    *   `GET /companies/{company_id}`: Retrieve details of a specific company.
    *   `PUT /companies/{company_id}`: Update an existing company's details.
    *   `DELETE /companies/{company_id}`: Delete a company (with appropriate cascade rules or soft delete).

**Frontend (React Web Dashboard):**

*   **Companies List Page:** Displays a table or card view of all companies, with search and filter options. Each entry links to the company's detail page.
*   **Company Detail Page:** Shows comprehensive information about a selected company, including its profile, a list of associated projects, financial summaries, and key documents. Buttons for editing company details.
*   **Create/Edit Company Form:** A form for inputting or modifying company information.

**Data Flow:**

1.  User interacts with the React frontend (e.g., clicks 


the 'Add Company' button).
2.  React sends a request (e.g., `POST /companies`) to the FastAPI backend.
3.  FastAPI validates the data using `CompanyCreate` schema, interacts with the PostgreSQL database via SQLAlchemy to create/update the company record.
4.  FastAPI returns the created/updated `CompanyRead` object to the React frontend.
5.  React updates its UI to reflect the changes.

### 8.2. Projects Module

**Purpose:** To track individual projects undertaken by each company, including their status, financial details, and associated documents.

**Key Functionalities:**

*   **CRUD Project Details:** Allow users to add new projects, view existing ones, modify their attributes, and mark them as completed or cancelled.
*   **Project Overview:** Provide a detailed view for each project, including its financial performance, associated documents, and linked ledger entries.
*   **Link to Company:** Each project must be associated with a specific company.

**Backend (FastAPI):**

*   **Model:** `Project` (as defined in Section 5.1.1).
*   **Schemas:** `ProjectCreate` (for creating new projects, including `company_id`), `ProjectRead` (for reading project data, including nested `CompanyInfo`).
*   **Router:** `src/vanta_ledger/routers/projects.py`.
    *   `POST /projects`: Create a new project, linking it to a company.
    *   `GET /projects`: Retrieve a list of all projects (can be filtered by company).
    *   `GET /projects/{project_id}`: Retrieve details of a specific project.
    *   `GET /companies/{company_id}/projects`: Retrieve all projects for a given company.
    *   `PUT /projects/{project_id}`: Update an existing project's details.
    *   `DELETE /projects/{project_id}`: Delete a project.

**Frontend (React Web Dashboard):**

*   **Projects List Page:** Displays a table or card view of all projects, with filters for company, status, and date range. Each entry links to the project's detail page.
*   **Project Detail Page:** Shows comprehensive information about a selected project, including its client, value, dates, status, description, and lists of associated documents and ledger entries. Buttons for editing project details.
*   **Create/Edit Project Form:** A form for inputting or modifying project information, with a dropdown to select the associated company.

**Data Flow:**

1.  User navigates to the Projects section or clicks 'Add Project'.
2.  React sends a request (e.g., `POST /projects` with `company_id`) to the FastAPI backend.
3.  FastAPI validates the data using `ProjectCreate` schema, interacts with the PostgreSQL database via SQLAlchemy to create/update the project record.
4.  FastAPI returns the created/updated `ProjectRead` object to the React frontend.
5.  React updates its UI to reflect the changes, displaying the new or updated project in the list or detail view.




### 8.3. Documents Module

**Purpose:** To provide a centralized repository for all project-related and company-wide documents, ensuring easy storage, retrieval, version control, and searchability. This module is critical for tender preparation and compliance.

**Key Functionalities:**

*   **Document Upload:** Allow users to upload various file types (PDF, Word, Excel, images) and associate them with a specific company and/or project.
*   **Versioning:** Automatically manage multiple versions of a document, preserving historical changes and allowing users to view or download previous versions.
*   **Metadata Management:** Store and display key metadata for each document, including filename, file path, document type (e.g., Letter of Award, Tax Compliance Certificate, Invoice), upload date, uploader, and expiry date (for certificates).
*   **Search and Filtering:** Enable users to search for documents by keywords, document type, associated company/project, date range, and other metadata.
*   **Preview and Download:** Provide options to preview documents directly within the application and download original files.
*   **Integration with Paperless-ngx:** Leverage Paperless-ngx for OCR processing and initial metadata extraction, with the Vanta Ledger backend handling the structured storage and business logic.

**Backend (FastAPI):**

*   **Model:** `Document` (as defined in Section 5.1.1).
*   **Schemas:** `DocumentCreate` (for uploading new documents and their metadata), `DocumentRead` (for displaying document details), `DocumentUpload` (for handling file uploads).
*   **Router:** `src/vanta_ledger/routers/documents.py`.
    *   `POST /documents/upload`: Handle file uploads, store the file on local storage, and create a `Document` record in the database. This endpoint will also trigger the AI/NLP microservice for content analysis.
    *   `GET /documents`: Retrieve a list of all documents (with filters for company, project, type, etc.).
    *   `GET /documents/{document_id}`: Retrieve details of a specific document.
    *   `GET /documents/{document_id}/versions`: Retrieve historical versions of a document.
    *   `PUT /documents/{document_id}`: Update document metadata (e.g., `doc_type`, `notes`, `expiry_date`). This can also be used to upload a new version of an existing document.
    *   `DELETE /documents/{document_id}`: Delete a document and its associated files.
    *   `GET /documents/{document_id}/download`: Endpoint to serve the actual document file.

**Frontend (React Web Dashboard):**

*   **Document List Page:** Displays a searchable and filterable list of documents, potentially organized by company or project. Each entry shows key metadata and provides actions (view, download, edit, upload new version).
*   **Document Detail Page:** Shows all metadata for a selected document, including its version history. Provides a preview of the document (if supported by the browser) and options to download or upload a new version.
*   **Upload Document Form:** A form for selecting a file, associating it with a company/project, and adding initial metadata. This form will also handle the actual file upload to the backend.

**Data Flow:**

1.  User uploads a document via the React frontend.
2.  The frontend sends the file and initial metadata to `POST /documents/upload` on the FastAPI backend.
3.  FastAPI saves the file to the designated local storage path (e.g., `/docs/<company_name>/<project_name>/`).
4.  FastAPI creates a `Document` record in the PostgreSQL database, including the `file_path` and `version_number`.
5.  FastAPI (or a background task) sends the document to Paperless-ngx for OCR processing and then sends the OCR text to the AI/NLP microservice for structured data extraction.
6.  The extracted structured data is then used to update the `Document` record or populate a `DocumentAnalysis` table, enhancing searchability and reporting capabilities.
7.  The React frontend updates to show the newly uploaded document or its new version.




### 8.4. Ledger Module

**Purpose:** To accurately record and track all financial transactions (income, expenses, owner withdrawals) for each company and project, providing a clear financial overview and supporting financial reporting.

**Key Functionalities:**

*   **Transaction Entry:** Allow users to easily record new income, expense, or owner withdrawal entries, linking them to specific companies and projects.
*   **Transaction Listing:** Display a comprehensive list of all ledger entries, with robust filtering, sorting, and search capabilities (by type, date, amount, company, project, description).
*   **Financial Summaries:** Provide aggregated views of income, expenses, and net balance for selected periods, companies, or projects.
*   **Categorization:** Support categorization of expenses and income for better financial analysis.

**Backend (FastAPI):**

*   **Model:** `LedgerEntry` (as defined in Section 5.1.1).
*   **Schemas:** `LedgerEntryCreate` (for creating new entries), `LedgerEntryRead` (for reading ledger entry details).
*   **Router:** `src/vanta_ledger/routers/ledger.py`.
    *   `POST /ledger`: Create a new ledger entry.
    *   `GET /ledger`: Retrieve a list of all ledger entries.
    *   `GET /ledger/{entry_id}`: Retrieve details of a specific ledger entry.
    *   `GET /companies/{company_id}/ledger`: Retrieve all ledger entries for a given company.
    *   `GET /projects/{project_id}/ledger`: Retrieve all ledger entries for a given project.
    *   `PUT /ledger/{entry_id}`: Update an existing ledger entry.
    *   `DELETE /ledger/{entry_id}`: Delete a ledger entry.

**Frontend (React Web Dashboard):**

*   **Ledger List Page:** Displays a table of all ledger entries. Users can filter by company, project, date range, type (income/expense/withdrawal), and search by description. Columns will include date, type, description, amount, linked company, and linked project.
*   **Add/Edit Ledger Entry Form:** A form for inputting new transactions or modifying existing ones. Fields will include date, type (dropdown), amount, description, and dropdowns to select the associated company and (optionally) project.
*   **Financial Summary Widgets:** Dashboard widgets displaying quick summaries like 


total income, total expenses, and net balance for a selected period.

**Data Flow:**

1.  User navigates to the Ledger section or clicks 'Add Entry'.
2.  React sends a request (e.g., `POST /ledger`) to the FastAPI backend with the transaction details.
3.  FastAPI validates the data using `LedgerEntryCreate` schema, interacts with the PostgreSQL database via SQLAlchemy to create/update the ledger entry.
4.  FastAPI returns the created/updated `LedgerEntryRead` object to the React frontend.
5.  React updates its UI to reflect the changes, displaying the new or updated entry in the ledger list and updating financial summaries.

### 8.5. Users & Authentication Module

**Purpose:** To manage user accounts and control access to the Vanta Ledger system, ensuring data security and integrity. Initially, this will be a simple system for the core family heads, with potential for more granular roles in the future.

**Key Functionalities:**

*   **User Registration (Admin-only):** Administrators can create new user accounts.
*   **User Login:** Authenticate users based on their credentials.
*   **Role-Based Access Control (RBAC):** Assign roles to users (e.g., 'admin', 'viewer') to control their permissions within the system.
*   **User Profile Management:** Allow users to view and update their own profiles (e.g., password change).

**Backend (FastAPI):**

*   **Model:** `User` (as defined in Section 5.1.1).
*   **Schemas:** `UserCreate` (for creating new users), `UserRead` (for reading user data), `UserLogin` (for authentication requests).
*   **Router:** `src/vanta_ledger/routers/users.py` (or `auth.py`).
    *   `POST /auth/login`: Authenticate user credentials and return an authentication token (e.g., JWT).
    *   `GET /users/me`: Retrieve the profile of the currently authenticated user.
    *   `POST /users`: (Admin-only) Create a new user account.
    *   `PUT /users/{user_id}`: (Admin-only or self-update) Update user details or password.
    *   `DELETE /users/{user_id}`: (Admin-only) Delete a user account.
*   **Authentication Strategy:** Implement token-based authentication (e.g., JWT) for securing API endpoints. FastAPI's `Depends` system will be used to inject the authenticated user into route handlers.
*   **Password Hashing:** Store user passwords securely using strong hashing algorithms (e.g., `bcrypt`).

**Frontend (React Web Dashboard):**

*   **Login Page:** A dedicated page for user authentication.
*   **User Management Page (Admin-only):** Displays a list of users, with options to create new users, edit roles, or reset passwords.
*   **User Profile Page:** Allows the logged-in user to view and update their own information.
*   **Protected Routes:** Implement client-side routing protection to ensure that only authenticated users can access certain parts of the application.

**Data Flow:**

1.  User enters credentials on the Login Page.
2.  React sends a `POST /auth/login` request to the FastAPI backend.
3.  FastAPI verifies credentials, generates a JWT token, and returns it to the frontend.
4.  The frontend stores the token (e.g., in local storage) and includes it in subsequent API requests (e.g., in the `Authorization` header).
5.  For protected routes, FastAPI validates the token and extracts user information, allowing or denying access based on the user's role.

### 8.6. Reports & Dashboards Module

**Purpose:** To provide visual summaries and detailed reports of the business data, enabling informed decision-making and facilitating tender preparation and compliance.

**Key Functionalities:**

*   **Interactive Dashboards:** Display key performance indicators (KPIs) and aggregated data through charts, graphs, and summary tables.
*   **Customizable Reports:** Allow users to generate detailed reports based on various criteria (e.g., company, project, date range, document type).
*   **Export Functionality:** Enable exporting reports to common formats like PDF (for printing and official submissions) and Excel/CSV (for further analysis).

**Backend (FastAPI):**

*   **Router:** `src/vanta_ledger/routers/reports.py`.
    *   `GET /reports/summary`: Provide aggregated data for dashboards (e.g., total income/expenses, project counts).
    *   `GET /reports/profit-loss`: Generate profit and loss statements based on filters.
    *   `GET /reports/project-summary/{project_id}`: Generate a detailed summary for a specific project.
    *   `GET /reports/company-profile/{company_id}`: Generate a comprehensive profile for a company, including project history and key documents.
    *   `GET /reports/document-expiry`: List documents nearing expiry.
*   **Report Generation:** Utilize Python libraries (e.g., `ReportLab`, `fpdf2` for PDF generation; `openpyxl` for Excel) to dynamically create report files based on data retrieved from the PostgreSQL database.

**Frontend (React Web Dashboard):**

*   **Dashboard Page:** The main landing page after login, featuring customizable widgets displaying key metrics (e.g., monthly cash flow, top projects by value, recent documents, upcoming deadlines).
*   **Reports Section:** A dedicated section where users can select report types, apply filters, and trigger report generation. Displays a list of generated reports for download.
*   **Print/Export Buttons:** Prominently placed buttons on relevant pages (e.g., Project Detail, Company Detail) to generate and download specific reports.

**Data Flow:**

1.  User selects report criteria on the React frontend.
2.  React sends a request to the appropriate FastAPI report endpoint (e.g., `GET /reports/profit-loss?company_id=X&start_date=Y`).
3.  FastAPI queries the PostgreSQL database, processes the data, and generates the report file (e.g., PDF).
4.  FastAPI returns the generated file as a response, which the browser then downloads.

### 8.7. Future Modules (Phase 2/3)

These modules are planned for later phases of development, building upon the core MVP functionalities.

#### 8.7.1. Subcontractors Module

**Purpose:** To manage information about subcontractors and joint venture partners, linking them to specific projects.

**Key Functionalities:**

*   **CRUD Subcontractor Profiles:** Store contact details, services offered, and contract terms for subcontractors.
*   **Link to Projects:** Associate subcontractors with projects they have worked on.
*   **Performance Tracking:** Potentially track subcontractor performance or payment status.

**Backend (FastAPI):**

*   **Model:** `Subcontractor` (as defined in Section 5.1.1).
*   **Schemas:** `SubcontractorCreate`, `SubcontractorRead`.
*   **Router:** `src/vanta_ledger/routers/subcontractors.py`.

**Frontend (React Web Dashboard):**

*   **Subcontractors List Page:** Displays a list of all subcontractors.
*   **Subcontractor Detail Page:** Shows details and linked projects.
*   **Project Integration:** Allow linking subcontractors when creating/editing projects.

#### 8.7.2. Tender Pipeline Module

**Purpose:** To manage the lifecycle of tender applications, from discovery to award, and track required documents and deadlines.

**Key Functionalities:**

*   **Tender Tracking:** Record details of tenders applied for, including tender number, client, submission date, and status (pending, won, lost, withdrawn).
*   **Document Checklist:** Maintain a checklist of required documents for each tender application.
*   **Deadline Reminders:** Provide alerts for upcoming tender submission deadlines.
*   **Success Rate Analysis:** Track tender win/loss rates over time.

**Backend (FastAPI):**

*   **Model:** `Tender` (as defined in Section 5.1.1).
*   **Schemas:** `TenderCreate`, `TenderRead`.
*   **Router:** `src/vanta_ledger/routers/tenders.py`.

**Frontend (React Web Dashboard):**

*   **Tender List Page:** Displays a list of all tenders, with filters for status and deadlines.
*   **Tender Detail Page:** Shows comprehensive information about a tender, including required documents, submission status, and associated projects.
*   **Dashboard Widget:** A widget on the main dashboard showing upcoming tender deadlines.

#### 8.7.3. Advanced AI/NLP Features

Building upon the initial AI/NLP microservice, future enhancements could include:

*   **Automated Document Tagging:** More sophisticated classification of documents based on content.
*   **Semantic Search:** Allowing natural language queries to find documents based on meaning, not just keywords.
*   **Anomaly Detection:** Identifying unusual patterns in financial data or document content (e.g., unusually high expenses, missing documents).
*   **Predictive Analytics:** Forecasting cash flow or project timelines based on historical data.
*   **AI-Assisted Report Drafting:** Generating initial drafts of reports or summaries based on extracted data.

#### 8.7.4. Notifications & Reminders

*   **Document Expiry Alerts:** Automated notifications for expiring certificates (NCA, Tax Compliance, CR12).
*   **Tender Deadline Reminders:** Alerts for upcoming tender submission dates.
*   **Workflow Notifications:** Notifications for key events (e.g., new project added, large expense recorded).




## 9. Project Timeline and Phased Development

The development of the Vanta Ledger system will follow a phased approach, prioritizing core functionalities for an initial Minimum Viable Product (MVP) and gradually introducing more advanced features. This iterative strategy allows for early deployment, user feedback integration, and efficient resource allocation, especially given the solo development effort.

### 9.1. Phase 1: Minimum Viable Product (MVP)

**Duration:** Approximately 6-8 weeks (realistic, part-time, learning as you go).

**Goal:** Establish the foundational system for managing companies, projects, basic documents, and financial transactions, accessible via a web interface.

**Key Deliverables:**

*   **Backend (FastAPI):**
    *   Core FastAPI application setup (`main.py`, `database.py`, `config.py`).
    *   PostgreSQL database setup and initial Alembic migrations.
    *   CRUD APIs for `Companies`, `Projects`, `Documents` (metadata only, initial upload), and `Ledger Entries`.
    *   Basic `Users` module (admin user creation, login).
*   **Frontend (React Web Dashboard):**
    *   Basic React application setup with routing.
    *   Pages for listing and managing Companies, Projects, Documents, and Ledger Entries.
    *   Forms for creating/editing entries.
    *   Basic display of data from backend APIs (initial API wiring).
*   **Document Management:**
    *   Paperless-ngx installed and running, with initial document OCR processing.
    *   Manual document upload to the system, with files stored locally.
*   **Infrastructure:**
    *   Initial `docker-compose.yml` for backend and PostgreSQL.
    *   Basic local file storage setup.

### 9.2. Phase 2: Core Enhancements and Automation

**Duration:** Approximately 4-6 weeks after MVP deployment.

**Goal:** Improve usability, automate document processing, and introduce more sophisticated data management features.

**Key Deliverables:**

*   **Backend (FastAPI):**
    *   Full `Documents` module implementation (versioning, detailed metadata, file preview).
    *   Improved `Ledger` module (categorization, basic financial summaries).
    *   Initial `AI/NLP Microservice` (entity extraction from OCR text for project/company matching, key fields).
    *   Integration of extracted data into `Document` and `Ledger` models.
*   **Frontend (React Web Dashboard):**
    *   Enhanced Document Library (search, filters, version history view).
    *   Improved Ledger views with filtering and summary dashboards.
    *   Basic reporting functionalities (e.g., simple P&L, project summaries).
*   **Document Management:**
    *   Automated ingestion of documents from Paperless-ngx to Vanta Ledger DB.
    *   Integration of AI/NLP microservice for automated metadata extraction.
*   **Infrastructure:**
    *   Refined `docker-compose.yml` to include AI/NLP microservice.
    *   Automated daily backup scripts for DB and document files.

### 9.3. Phase 3: Advanced Features and Scalability

**Duration:** Ongoing, based on user feedback and evolving needs.

**Goal:** Introduce advanced business intelligence, workflow automation, and expand system capabilities.

**Key Deliverables:**

*   **Backend (FastAPI):**
    *   `Subcontractors` module (CRUD, linking to projects).
    *   `Tender Pipeline` module (tracking bids, deadlines, required documents).
    *   Advanced `Users` and `Authentication` (RBAC, more granular permissions).
    *   Notification and Reminder system (document expiry, tender deadlines).
*   **Frontend (React Web Dashboard):**
    *   Interactive dashboards with advanced analytics (potentially using Metabase).
    *   Comprehensive reporting suite with customizable PDF/Excel exports.
    *   UI for Subcontractors and Tender Pipeline modules.
*   **Mobile (Flutter App):**
    *   Full synchronization with backend, including offline capabilities.
    *   Enhanced mobile features (e.g., photo uploads, simplified reporting).
*   **AI/NLP Microservice:**
    *   Advanced NLP (semantic search, document summarization, anomaly detection).
    *   Integration of local LLMs for more complex tasks.
*   **Infrastructure:**
    *   Consideration for high availability and load balancing if user base or data volume significantly increases.
    *   Enhanced monitoring and logging.

## 10. Conclusion

The Vanta Ledger project represents a strategic initiative to transform informal business practices into a streamlined, digital, and data-driven operation. By leveraging a modular architecture, open-source technologies, and a phased development approach, the system aims to provide a robust, secure, and cost-effective solution tailored to the unique needs of the Kenyan family-owned tendering and construction business.

This comprehensive plan serves as a living document, guiding the development process while remaining flexible enough to adapt to new insights and requirements. The successful implementation of Vanta Ledger will not only enhance operational efficiency and compliance but also empower the family heads with actionable insights, enabling them to make more informed decisions and secure future business opportunities. The journey from scattered records to a centralized digital fortress is a testament to the power of technology in transforming traditional businesses, ensuring they are well-equipped for growth and success in the modern landscape.

---

**Author:** Manus AI
**Date:** July 18, 2025



