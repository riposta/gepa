"""
Generator of manually curated training examples.
Covers 4 IT/telco project types: new, legacy, ai, migration.
No company-specific information.
"""
import json
import uuid
from pathlib import Path

EXAMPLES = [

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE: NEW — brand new systems from scratch
    # ─────────────────────────────────────────────────────────────────────────

    {
        "project_description": (
            "Self-service portal for individual customers of a telecommunications operator. "
            "Features: account management (change data, password, address), "
            "online invoice viewing and payment, service management (activate/deactivate packages), "
            "call and data usage history, service request form with status tracking. "
            "Stack: React 18 + TypeScript, FastAPI, PostgreSQL, Redis for sessions, "
            "payment gateway integration, OAuth2 SSO."
        ),
        "actual_hours": 920,
        "project_type": "new",
        "client_history": "Operator previously delivered a B2B portal (800h, on time). Experienced frontend team.",
        "risk_patterns": "Payment gateway integration historically adds +30% to estimates.",
        "pm_comment": "Testing time and OWASP security hardening were underestimated.",
        "source": "curated",
    },
    {
        "project_description": (
            "Service ticket management system for business customers. "
            "Ticketing with SLA priorities, escalation, assignment to technicians. "
            "Customer panel (web + mobile PWA), dispatcher panel, field service system integration. "
            "SMS/email notifications, KPI reports, management dashboard. "
            "Backend: Node.js + TypeScript, MongoDB, WebSockets for real-time status."
        ),
        "actual_hours": 1040,
        "project_type": "new",
        "client_history": "No history — new client.",
        "risk_patterns": "Real-time components (WebSocket) historically difficult to test — +20%.",
        "pm_comment": "Scope was well defined, estimate was close to actual.",
        "source": "curated",
    },
    {
        "project_description": (
            "API gateway for a microservices ecosystem of a telco operator. "
            "Rate limiting, JWT + API key authentication, routing to 12 backend services, "
            "payload transformation, SLA monitoring, circuit breaker, retry logic. "
            "OpenAPI documentation, developer portal for external partners. "
            "Stack: Kong Gateway + custom Lua plugins, Keycloak, Prometheus + Grafana."
        ),
        "actual_hours": 680,
        "project_type": "new",
        "client_history": "Client has microservices experience — 3 previous projects delivered on time.",
        "risk_patterns": "Custom Lua plugins require specialists — resource availability risk.",
        "pm_comment": "Well estimated project, slight overrun on developer portal documentation.",
        "source": "curated",
    },
    {
        "project_description": (
            "Mobile app iOS + Android for managing phone subscription. "
            "Biometric login, balance and invoice view, top-ups, "
            "tariff plan change, customer support chat, push notifications. "
            "React Native, integration with operator's REST API backend, "
            "Apple Pay / Google Pay for payments."
        ),
        "actual_hours": 1160,
        "project_type": "new",
        "client_history": "Operator had no mobile app before — first implementation.",
        "risk_patterns": "First mobile app for client — no internal review processes and store submission. +25%.",
        "pm_comment": "Delays in configuring Apple Developer Program and Google Play Console.",
        "source": "curated",
    },
    {
        "project_description": (
            "Service provisioning system for B2B customers. Automatic activation of internet, "
            "telephony and TV after contract signing. Integration with 4 OSS/BSS systems, "
            "workflow engine (Camunda), status notifications, rollback on errors. "
            "SLA: provisioning in < 4 business hours. REST + SOAP API for legacy systems."
        ),
        "actual_hours": 1580,
        "project_type": "new",
        "client_history": "Client previously did manual provisioning — integrations with these systems already known.",
        "risk_patterns": "SOAP integrations always require extra time for data mapping — +40%.",
        "pm_comment": "Rollback logic was underestimated — turned out to be the hardest element.",
        "source": "curated",
    },
    {
        "project_description": (
            "B2B portal for operator's trade partners. Wholesale order management, "
            "product catalogue with individual pricing, volume discounts, invoices, "
            "sales reports, API for partner ERP system integration. "
            "Roles and permissions (partner admin, sales rep, finance). "
            "Angular 17, Java Spring Boot, Oracle DB."
        ),
        "actual_hours": 1320,
        "project_type": "new",
        "client_history": "Two previous Java Spring Boot projects — delivered with 10% budget overrun.",
        "risk_patterns": "Individual pricing and discounts — business logic always more complex than assumed.",
        "pm_comment": "Discount logic turned out very complex — 4 discount types instead of planned 2.",
        "source": "curated",
    },
    {
        "project_description": (
            "Data usage monitoring system for prepaid customers. "
            "Real-time MB, SMS, minutes counter. Automatic notifications at 80% and 100% limit. "
            "Data aggregation from 3 billing systems, Redis cache, "
            "mobile and web API. Load: 500k active sessions simultaneously."
        ),
        "actual_hours": 760,
        "project_type": "new",
        "client_history": "Client built a similar system 2 years ago (slightly smaller scale) — 640h.",
        "risk_patterns": "Scaling to 500k sessions — performance tests always reveal problems.",
        "pm_comment": "Performance tests and Redis optimization took 2x longer than planned.",
        "source": "curated",
    },
    {
        "project_description": (
            "Electronic contract management system for business customers. "
            "Contract generation from Word/PDF templates, electronic signature (qualified e-signature), "
            "contract repository with search, renewal reminder notifications, "
            "multi-level approval workflow, integration with CRM and ERP."
        ),
        "actual_hours": 840,
        "project_type": "new",
        "client_history": "No history with electronic signature systems.",
        "risk_patterns": "Qualified e-signature — certification and legal testing always extend the project.",
        "pm_comment": "Electronic signature certification took 6 weeks instead of planned 2.",
        "source": "curated",
    },
    {
        "project_description": (
            "Phone number management platform (Number Management System). "
            "Number pools, reservations, customer allocations, number porting (MNP), "
            "national registry integration, reporting, change audit. "
            "Handling 50 million numbers, high availability 99.99%."
        ),
        "actual_hours": 2200,
        "project_type": "new",
        "client_history": "Critical telco system — client never implemented a project of this class.",
        "risk_patterns": "Telco-grade systems with 99.99% HA requirement: every infrastructure element doubled.",
        "pm_comment": "Failover and disaster recovery tests took 3 months. Good thing a buffer was planned.",
        "source": "curated",
    },
    {
        "project_description": (
            "Simple landing page with registration form for internet service. "
            "Multi-step form (personal data → package selection → confirmation), "
            "real-time validation, integration with lead queuing system, "
            "A/B tests, Google Analytics. Stack: Next.js, Tailwind CSS."
        ),
        "actual_hours": 180,
        "project_type": "new",
        "client_history": "Client regularly commissions small web projects — good experience.",
        "risk_patterns": "No risks — simple scope.",
        "pm_comment": "Delivered on time and within budget.",
        "source": "curated",
    },
    {
        "project_description": (
            "Queue and appointment management system for retail stores. "
            "Registration kiosk (tablet), queue display (TV), "
            "SMS notifications about upcoming queue, advisor panel, "
            "wait time and service reports, CRM integration. "
            "50 stores, 200 workstations."
        ),
        "actual_hours": 640,
        "project_type": "new",
        "client_history": "Client had a similar system for 10 stores — now scaling to 50.",
        "risk_patterns": "Scaling from 10 to 50 stores — per-location configuration always time-consuming.",
        "pm_comment": "Per-store location configuration took 20% more time than assumed.",
        "source": "curated",
    },
    {
        "project_description": (
            "5G radio network planning tool. "
            "Coverage visualization on map (Mapbox GL), KML/shp file import, "
            "antenna placement optimization algorithm, PDF/Excel report export. "
            "Web application for network engineers. Vue.js + Python backend + PostGIS."
        ),
        "actual_hours": 1100,
        "project_type": "new",
        "client_history": "Specialized GIS tool — client had no such projects before.",
        "risk_patterns": "Optimization algorithms and GIS — expert domain knowledge required, specialist availability risk.",
        "pm_comment": "Optimization algorithm turned out computationally very complex — extra work on performance.",
        "source": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE: LEGACY — modernization and maintenance of old systems
    # ─────────────────────────────────────────────────────────────────────────

    {
        "project_description": (
            "Modernization of billing system written in COBOL (1990s). "
            "Migration of business logic to Java 17 + Spring Boot. "
            "Rewriting 200 COBOL programs, maintaining compatibility with output file formats, "
            "comparative regression tests (old vs new system running in parallel for 6 months), "
            "code documentation (no documentation in original)."
        ),
        "actual_hours": 4800,
        "project_type": "legacy",
        "client_history": "Critical system, running continuously for 28 years. Zero documentation.",
        "risk_patterns": "COBOL migration without documentation — discovering hidden business logic is the biggest risk. +80%.",
        "pm_comment": "Project took 2x longer than planned — discovered 40 undocumented business rules.",
        "source": "curated",
    },
    {
        "project_description": (
            "Upgrade of network management system from Java 8 + Struts 2 to Java 21 + Spring Boot 3 + React. "
            "Refactoring 350k lines of code, migration from Oracle 11g to Oracle 19c, "
            "replacing JSP with new React frontend, API modernization (REST instead of SOAP), "
            "regression tests for 800 test cases."
        ),
        "actual_hours": 3200,
        "project_type": "legacy",
        "client_history": "OSS system, 12 years in production. Previous upgrade (Java 6→8) took 1800h.",
        "risk_patterns": "SOAP → REST migration while maintaining compatibility with external integrations.",
        "pm_comment": "Identified 15 external systems integrated via SOAP — each required separate work.",
        "source": "curated",
    },
    {
        "project_description": (
            "Refactoring of complaints handling module — monolithic PHP 5.6 → PHP 8.2 + Laravel. "
            "Rewriting 80k lines of code, database schema modernization (MySQL), "
            "adding unit tests (target coverage 70%), CI/CD pipeline, "
            "preserving all functionality, zero downtime deployment."
        ),
        "actual_hours": 1440,
        "project_type": "legacy",
        "client_history": "Client already refactored orders module (PHP 5.6→7.4, 900h). This module is more complex.",
        "risk_patterns": "Rewriting without regression tests is risky — many edge cases in complaints logic.",
        "pm_comment": "Adding tests from scratch took 35% of project time — worth it for risk reduction.",
        "source": "curated",
    },
    {
        "project_description": (
            "Modernization of wholesale order management system — Oracle Forms 6i to web. "
            "Migration of 120 Oracle Forms to Angular + REST API web application. "
            "Preserving all business rules, Oracle data migration, "
            "user training (300 people), parallel operation for 3 months."
        ),
        "actual_hours": 2600,
        "project_type": "legacy",
        "client_history": "System from 1998. Never modernized. Key to operator's operations.",
        "risk_patterns": "Oracle Forms migration — many hidden triggers and PL/SQL procedures. +60% to estimate.",
        "pm_comment": "Discovered 200 PL/SQL procedures with business logic not in documentation.",
        "source": "curated",
    },
    {
        "project_description": (
            "CRM system performance optimization — page response time increased from 2s to 45s. "
            "SQL profiling (Oracle), optimization of 150 slow queries, indexes, table partitioning, "
            "introducing cache (Redis), data archival (5 years history to cold storage). "
            "Target: return to < 3s for 95% of requests."
        ),
        "actual_hours": 520,
        "project_type": "legacy",
        "client_history": "CRM running for 8 years — performance issues building up for 2 years.",
        "risk_patterns": "Optimizing existing DB schema without rebuild — hard to predict effects before profiling.",
        "pm_comment": "Identified 3 key N+1 queries responsible for 70% of degradation — accurate diagnosis.",
        "source": "curated",
    },
    {
        "project_description": (
            "Upgrade and hardening of RADIUS server for PPPoE authentication — "
            "migration from FreeRADIUS 2.x to FreeRADIUS 3.x on new hardware, "
            "EAP-TLS implementation, new LDAP integration, "
            "failover tests, documentation, handling 2 million sessions per day."
        ),
        "actual_hours": 380,
        "project_type": "legacy",
        "client_history": "Critical infrastructure element — last upgrade was 6 years ago.",
        "risk_patterns": "Migrating a live authentication system — zero downtime required, maintenance window max 30 minutes.",
        "pm_comment": "Pre-migration tests were key — cut-over went smoothly in 15 minutes.",
        "source": "curated",
    },
    {
        "project_description": (
            "Decommission and replacement of wholesale customer billing system. "
            "Old system: RPG on IBM AS/400 (iSeries), new: Java + PostgreSQL + Jasper Reports. "
            "Data migration of 15 years of history, parallel operation for 6 months, "
            "finance department training (50 people), auditor certification."
        ),
        "actual_hours": 3800,
        "project_type": "legacy",
        "client_history": "AS/400 — last programmer who knew RPG left 2 years ago.",
        "risk_patterns": "No RPG/AS400 experts on the market — understanding logic from source code without documentation.",
        "pm_comment": "Reverse engineering 25 years of business logic from RPG took 8 months.",
        "source": "curated",
    },
    {
        "project_description": (
            "Migration of employee portal from Liferay 6.2 to Liferay DXP 2024. "
            "25 portlets, 60k users, Active Directory integration, "
            "content migration, graphic theme, 15 custom portlets to rebuild. "
            "Preserving SSO and role-based permissions."
        ),
        "actual_hours": 1200,
        "project_type": "legacy",
        "client_history": "Client had previous Liferay migration (5.x → 6.2) — 700h, delivered on time.",
        "risk_patterns": "Custom Liferay portlets — API changed significantly between versions.",
        "pm_comment": "7 of 15 portlets required rewriting from scratch due to Liferay API changes.",
        "source": "curated",
    },
    {
        "project_description": (
            "Security hardening of telco OSS-class system — network management system running for 10 years. "
            "Security audit (150 control points), fix implementation, "
            "updating 45 dependencies (CVE), WAF deployment, "
            "network segmentation, security logs to SIEM, ISO 27001 certification."
        ),
        "actual_hours": 960,
        "project_type": "legacy",
        "client_history": "Last security audit 4 years ago. Very large security technical debt.",
        "risk_patterns": "Security hardening of old systems — dependencies often vulnerable, regression after update.",
        "pm_comment": "Updating 12 dependencies caused regression requiring additional work.",
        "source": "curated",
    },
    {
        "project_description": (
            "Rewriting tariff rules engine from PL/SQL (40k lines) to Java microservice. "
            "Pricing rules for 200 tariff plans, receipt testing (10k test cases), "
            "shadow mode — parallel operation of old and new for 3 months with result comparison. "
            "Zero tolerance for billing errors."
        ),
        "actual_hours": 2800,
        "project_type": "legacy",
        "client_history": "Tariff engine — most important billing element. One error = million in claims.",
        "risk_patterns": "Tariff engines: every rule has exceptions, every exception has exceptions. +50% to estimate.",
        "pm_comment": "Discovered 35 undocumented rules in PL/SQL during code analysis.",
        "source": "curated",
    },
    {
        "project_description": (
            "Modernization of paper invoice printing and distribution system. "
            "Old system: Perl scripts + cron + matrix printer. "
            "New: Java microservice, PDF generation (iText), "
            "integration with postal service provider API, shipment tracking, "
            "electronic archive. 200k invoices per month."
        ),
        "actual_hours": 680,
        "project_type": "legacy",
        "client_history": "Simple scope — Perl scripts well documented.",
        "risk_patterns": "Integration with external postal provider — API may change.",
        "pm_comment": "Project went smoothly — Perl was well documented, which is rare.",
        "source": "curated",
    },
    {
        "project_description": (
            "Refactoring of customer service monolith — 1.2 million lines of Delphi code. "
            "Extracting 6 modules into separate services, "
            "keeping Firebird database unchanged, "
            "new REST API for each service, "
            "gradual migration without stopping production (strangler fig pattern)."
        ),
        "actual_hours": 5200,
        "project_type": "legacy",
        "client_history": "Monolith developed for 18 years — 6 different teams left their mark.",
        "risk_patterns": "Delphi experts hard to find on the market. Monolith with hidden dependencies between modules.",
        "pm_comment": "Identified circular dependencies between modules requiring 4 months of analysis before coding.",
        "source": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE: AI — ML/AI/LLM projects
    # ─────────────────────────────────────────────────────────────────────────

    {
        "project_description": (
            "Mobile customer churn prediction model. "
            "ML pipeline: feature extraction from billing and CRM data (12 months history, "
            "500+ features), model training (XGBoost, LightGBM, ensemble), "
            "threshold optimization, explainability (SHAP), "
            "API for daily prediction for 5 million customers, "
            "retention department dashboard, A/B test with control group."
        ),
        "actual_hours": 1680,
        "project_type": "ai",
        "client_history": "Client previously had simple logistic regression scoring — wants ML with better quality.",
        "risk_patterns": "Feature engineering on billing data — data quality usually worse than assumed.",
        "pm_comment": "Cleaning and normalizing data from 3 different billing systems took 40% of project.",
        "source": "curated",
    },
    {
        "project_description": (
            "Customer service chatbot based on LLM (GPT-4 / Claude). "
            "Handling 50 most frequent customer questions (FAQ, order statuses, invoices), "
            "integration with CRM and billing systems via API, "
            "escalation to human agent, conversation logging, "
            "analytics dashboard, fine-tuning on historical transcripts, "
            "multilingual support (EN, PL, UA)."
        ),
        "actual_hours": 1240,
        "project_type": "ai",
        "client_history": "Client has existing customer service center — chatbot to offload 30% of traffic.",
        "risk_patterns": "LLM integration with transactional systems — hallucinations critical with financial data.",
        "pm_comment": "Guardrails against hallucinations and adversarial tests took 2x longer than planned.",
        "source": "curated",
    },
    {
        "project_description": (
            "Anomaly detection system in telecommunications network. "
            "Analysis of data streams from 10k network devices (NetFlow, SNMP), "
            "Isolation Forest + Autoencoder models for anomaly detection, "
            "event correlation, automatic alerts for NOC, "
            "real-time Grafana dashboard, ticketing system integration."
        ),
        "actual_hours": 1480,
        "project_type": "ai",
        "client_history": "Operator has extensive monitoring system experience — but first ML project.",
        "risk_patterns": "Network device data has many gaps and noise — preprocessing critical.",
        "pm_comment": "Choosing anomaly threshold was difficult — required 2 months of calibration with NOC team.",
        "source": "curated",
    },
    {
        "project_description": (
            "Offer recommendation engine for individual customers. "
            "Collaborative filtering + content-based for upgrade and add-on recommendations. "
            "Real-time A/B tests, push notification personalization, "
            "e-commerce platform and CRM integration, "
            "business metrics monitoring (CTR, conversion), "
            "MLflow for model versioning."
        ),
        "actual_hours": 1360,
        "project_type": "ai",
        "client_history": "Client ran manual marketing campaigns — first AI personalization.",
        "risk_patterns": "Cold start problem for new customers. Behavioral data sparse for prepaid.",
        "pm_comment": "Cold start required a separate approach for 40% of base — underestimated in planning.",
        "source": "curated",
    },
    {
        "project_description": (
            "NLP pipeline for automatic classification and routing of service tickets. "
            "Classification into 45 categories, entity extraction (customer number, address, service type), "
            "sentiment analysis, automatic responses for simple tickets, "
            "BERT model fine-tuned on 200k historical tickets, "
            "interface for agents to correct predictions."
        ),
        "actual_hours": 960,
        "project_type": "ai",
        "client_history": "Client handles 50k tickets per month — manual classification is a bottleneck.",
        "risk_patterns": "Fine-tuning BERT on telco-specific jargon requires large amounts of labeled data.",
        "pm_comment": "Labeling training data (2000 tickets) by domain experts — 3 weeks.",
        "source": "curated",
    },
    {
        "project_description": (
            "Radio network failure prediction (predictive maintenance). "
            "Telemetry analysis from 8000 BTS/NodeB/eNodeB base stations, "
            "failure prediction models 7 days ahead (random forest + LSTM), "
            "technical inspection prioritization, field service system integration, "
            "cost savings through prevention rather than failure repair."
        ),
        "actual_hours": 1880,
        "project_type": "ai",
        "client_history": "Operator has extensive network monitoring systems — high quality data.",
        "risk_patterns": "Predicting rare failures — imbalanced classes, precision/recall trade-off.",
        "pm_comment": "Class balancing and threshold tuning with asymmetric error costs took much time.",
        "source": "curated",
    },
    {
        "project_description": (
            "Automatic tagging and semantic search of customer service knowledge base. "
            "Embedding knowledge base articles (sentence-transformers), "
            "vector store (Weaviate), semantic search API, "
            "CRM and chatbot integration, content editor interface, "
            "search quality monitoring (human feedback loop)."
        ),
        "actual_hours": 720,
        "project_type": "ai",
        "client_history": "10k articles in knowledge base — classic keyword search no longer sufficient.",
        "risk_patterns": "Embedding quality depends on article content quality — many outdated.",
        "pm_comment": "Updating 30% of knowledge base articles by editors was necessary before deployment.",
        "source": "curated",
    },
    {
        "project_description": (
            "Computer vision for network infrastructure inspection from drones. "
            "Damage detection on antenna and mast photos (YOLOv8), "
            "damage type classification (cracks, corrosion, mechanical), "
            "mobile app for technicians, network asset management integration, "
            "photo processing pipeline (10k photos per month)."
        ),
        "actual_hours": 1560,
        "project_type": "ai",
        "client_history": "Innovative project — no historical data on similar deployments.",
        "risk_patterns": "Labeling data (infrastructure damage) requires certified engineers — costly and time-consuming.",
        "pm_comment": "Collecting 5000 labeled photos took 4 months — first and hardest phase.",
        "source": "curated",
    },
    {
        "project_description": (
            "Dynamic pricing for roaming services. "
            "Real-time price optimization model based on demand, network capacity, "
            "competitor prices (web scraping), historical patterns. "
            "Reinforcement learning (bandit algorithm), A/B testing, "
            "billing system integration, revenue management dashboard."
        ),
        "actual_hours": 2100,
        "project_type": "ai",
        "client_history": "Client has BI experience — but first RL project in production environment.",
        "risk_patterns": "RL in production — wrong reward can lead to unintended system behavior.",
        "pm_comment": "Simulation environment before production deployment was key — took 3 months.",
        "source": "curated",
    },
    {
        "project_description": (
            "Automatic technical report generation from network logs. "
            "Pipeline: syslog/NetFlow logs → preprocessing → LLM (Claude) → PDF/Word report. "
            "Report templates for NOC, sales, management. "
            "Automated email delivery schedule, "
            "recipient feedback to improve generated content quality."
        ),
        "actual_hours": 580,
        "project_type": "ai",
        "client_history": "Reports generated manually by analysts — 40h/week savings.",
        "risk_patterns": "Prompt engineering for technical reports requires iterations with recipients.",
        "pm_comment": "Iterations with report recipients took 6 weeks — but the final result was very good.",
        "source": "curated",
    },
    {
        "project_description": (
            "Packet network capacity optimization using ML. "
            "Traffic prediction (LSTM on 3 years of data), "
            "automatic capacity expansion recommendations, "
            "what-if simulator for network planners, "
            "network management system integration, "
            "planning department dashboard."
        ),
        "actual_hours": 1720,
        "project_type": "ai",
        "client_history": "Operator has high quality historical traffic data — good ML starting point.",
        "risk_patterns": "Traffic prediction 12+ months ahead — model accuracy drops drastically for long horizons.",
        "pm_comment": "Managing business expectations about prediction accuracy was a key challenge.",
        "source": "curated",
    },
    {
        "project_description": (
            "Proof of concept: AI assistant for network specialists based on RAG. "
            "Knowledge base: hardware technical documentation (5000 documents), "
            "configuration procedures, historical failure logs. "
            "LangChain + Claude, web interface, response evaluation (RAGAS). "
            "Goal: PoC in 8 weeks, 20 pilot users."
        ),
        "actual_hours": 320,
        "project_type": "ai",
        "client_history": "First LLM project in the organization — PoC to evaluate value before investment.",
        "risk_patterns": "PoC: limited scope, acceptable quality 'good enough' — not production.",
        "pm_comment": "PoC delivered in 7 weeks. Production deployment decision made after positive feedback.",
        "source": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # TYPE: MIGRATION — infrastructure, data, platform transfers
    # ─────────────────────────────────────────────────────────────────────────

    {
        "project_description": (
            "On-premise data center migration to AWS (lift-and-shift + optimize). "
            "150 virtual servers → EC2/ECS, "
            "database migration (Oracle → RDS Aurora, MongoDB → DocumentDB), "
            "network: VPN + Direct Connect, "
            "storage: SAN → S3 + EFS, "
            "disaster recovery, CloudWatch monitoring, IAM redesign. "
            "Zero downtime for critical systems."
        ),
        "actual_hours": 4200,
        "project_type": "migration",
        "client_history": "Client had no cloud workloads before — first cloud migration.",
        "risk_patterns": "First cloud migration: learning curve, networking changes, IAM policies — +50%.",
        "pm_comment": "Networking and IAM redesign took 2x longer than planned — archetypal problems.",
        "source": "curated",
    },
    {
        "project_description": (
            "Oracle 12c database migration (3TB) to PostgreSQL 16. "
            "Schema conversion (ora2pg + manual adjustments), stored procedure migration (PL/SQL → PL/pgSQL), "
            "data migration with integrity preservation, "
            "application regression tests (12 applications use this database), "
            "cutover plan with 4h maintenance window."
        ),
        "actual_hours": 1640,
        "project_type": "migration",
        "client_history": "Client did smaller Oracle→PG migration (500GB) 2 years ago — 800h, with minor issues.",
        "risk_patterns": "PL/SQL → PL/pgSQL: Oracle packages have no equivalent — refactoring required.",
        "pm_comment": "280 stored procedures required manual conversion due to Oracle-specific SQL.",
        "source": "curated",
    },
    {
        "project_description": (
            "Migration of 8 services from bare metal to Kubernetes (on-premise). "
            "Containerization (Dockerfile for each service), "
            "Helm charts, Ingress/NetworkPolicy configuration, "
            "persistent volumes for stateful services, "
            "CI/CD pipeline (GitLab CI → ArgoCD), "
            "monitoring (Prometheus + Grafana), "
            "load testing after migration."
        ),
        "actual_hours": 1080,
        "project_type": "migration",
        "client_history": "Client had 3 services on K8s (360h). Now scaling to whole organization.",
        "risk_patterns": "Stateful services (databases) in K8s require special attention on storage and backup.",
        "pm_comment": "Persistent volumes and stateful workload backup took 30% of project — well estimated.",
        "source": "curated",
    },
    {
        "project_description": (
            "Data lake migration from on-premise Hadoop/HDFS to Databricks on Azure. "
            "Migration of 200TB data, rewriting 150 Spark jobs (Scala → PySpark), "
            "Delta Lake format, Unity Catalog for governance, "
            "MLflow pipeline migration, "
            "training for 25 data scientists and data engineers."
        ),
        "actual_hours": 2800,
        "project_type": "migration",
        "client_history": "Hadoop for 7 years — very large technical debt. Client wants modern stack.",
        "risk_patterns": "Scala → PySpark: API differences, incompatibility of some libraries.",
        "pm_comment": "20 of 150 jobs had hardcoded HDFS paths — required deep rework.",
        "source": "curated",
    },
    {
        "project_description": (
            "Document management system migration from FileNet P8 to SharePoint Online (Microsoft 365). "
            "2 million documents, preserving metadata and version history, "
            "permission migration (150 AD groups), "
            "business application integration via Graph API, "
            "user training (500 people)."
        ),
        "actual_hours": 1480,
        "project_type": "migration",
        "client_history": "FileNet P8 running for 12 years — no internal expertise, vendor support expiring.",
        "risk_patterns": "FileNet metadata migration → SharePoint — different object models.",
        "pm_comment": "Mapping 80 FileNet document types to SharePoint content types took a month.",
        "source": "curated",
    },
    {
        "project_description": (
            "VoIP system migration from Cisco CUCM to Cisco Webex Calling (cloud PBX). "
            "2500 users, 180 locations, number migration (DID), "
            "device configuration (IP phones, softphone), "
            "call center integration, "
            "IT helpdesk and end user training."
        ),
        "actual_hours": 860,
        "project_type": "migration",
        "client_history": "Client knows Cisco — previous CUCM migration (v8 → v11) 520h.",
        "risk_patterns": "DID number migration in live environment — maintenance window per location.",
        "pm_comment": "Planning maintenance windows for 180 locations was logistically complex.",
        "source": "curated",
    },
    {
        "project_description": (
            "E-commerce platform migration from Magento 1.9 to Magento 2.4. "
            "100k products, 500k customers, order history (3 years), "
            "migration of 25 custom modules (API rewriting), "
            "new graphic theme (PWA), "
            "ERP and warehouse system integration."
        ),
        "actual_hours": 2200,
        "project_type": "migration",
        "client_history": "Client had no previous Magento migrations — but experienced with PHP and e-commerce.",
        "risk_patterns": "Magento 1→2: completely different architecture — M1 modules need rewriting from scratch.",
        "pm_comment": "8 of 25 modules turned out impossible to migrate — rewritten from scratch.",
        "source": "curated",
    },
    {
        "project_description": (
            "Email migration (25k mailboxes) from Lotus Notes 9 to Microsoft 365 Exchange Online. "
            "Email migration (5 years archive), contacts, calendars, "
            "Lotus Notes applications (15 databases) → SharePoint + Power Apps, "
            "DNS cutover, MX configuration, DKIM/DMARC, "
            "user training."
        ),
        "actual_hours": 1340,
        "project_type": "migration",
        "client_history": "Lotus Notes since 1996 — client never had cloud.",
        "risk_patterns": "Lotus Notes databases often contain hidden business processes — inventory critical.",
        "pm_comment": "Inventoried 47 Notes databases instead of planned 15 — each is a separate scope.",
        "source": "curated",
    },
    {
        "project_description": (
            "Lift-and-shift of 30 web applications to Azure Kubernetes Service. "
            "Containerization (Docker), AKS configuration, "
            "Azure Container Registry, Azure DevOps pipelines, "
            "Azure Monitor + Application Insights, "
            "Key Vault for secrets, "
            "Private Endpoints for security."
        ),
        "actual_hours": 1860,
        "project_type": "migration",
        "client_history": "5 of 30 applications already on Azure — client knows the platform.",
        "risk_patterns": "Applications with hard-coded connection strings — require refactoring before containerization.",
        "pm_comment": "12 applications had secrets coded in source — forced refactoring before migration.",
        "source": "curated",
    },
    {
        "project_description": (
            "Network monitoring system migration (Cacti + Nagios) to Zabbix 6.4 + Grafana. "
            "1200 monitored devices, migration of 800 templates, "
            "trigger and alert configuration, "
            "PagerDuty integration for escalation, "
            "Grafana dashboards per network type (core, access, radio). "
            "Parallel operation for 2 months."
        ),
        "actual_hours": 760,
        "project_type": "migration",
        "client_history": "Client uses Nagios for 10 years — well documented configuration.",
        "risk_patterns": "Nagios → Zabbix: different template concepts — conversion is not 1:1.",
        "pm_comment": "Template conversion took 30% more than planned — but Grafana dashboards were well received.",
        "source": "curated",
    },

    # ─────────────────────────────────────────────────────────────────────────
    # ADDITIONAL — scale and diversity extension
    # ─────────────────────────────────────────────────────────────────────────

    {
        "project_description": (
            "Microservice for recurring payment handling (subscriptions). "
            "Automatic monthly charge collection, failed transaction handling (retry logic), "
            "payment card management (PCI-DSS tokenization), "
            "SMS/email notifications, financial reporting, "
            "integration with 2 payment gateways (Stripe + local)."
        ),
        "actual_hours": 780,
        "project_type": "new",
        "client_history": "Client offers subscriptions but payment handling is manual.",
        "risk_patterns": "PCI-DSS compliance: audit and certification always extends project by 6-8 weeks.",
        "pm_comment": "PCI-DSS SAQ D certification took 8 weeks — but 4 were planned.",
        "source": "curated",
    },
    {
        "project_description": (
            "Fleet management system for operator's service vehicles. "
            "GPS tracking (500 vehicles), route and service order planning, "
            "mobile app for technicians (React Native), "
            "asset management integration, "
            "performance and cost reports, "
            "speeding and zone violation alerts."
        ),
        "actual_hours": 1120,
        "project_type": "new",
        "client_history": "Client manages fleet manually — first telematics deployment.",
        "risk_patterns": "Integration with GPS devices from different manufacturers — no protocol standard.",
        "pm_comment": "GPS protocols from different manufacturers: 4 different data formats requiring separate parsers.",
        "source": "curated",
    },
    {
        "project_description": (
            "Internal developer portal platform (Internal Developer Platform). "
            "API catalog (AsyncAPI + OpenAPI), technical documentation (Docusaurus), "
            "self-service infrastructure (Backstage), CI/CD templates, "
            "GitLab, Jira, Confluence integration. "
            "Improving productivity of 300 developers."
        ),
        "actual_hours": 1440,
        "project_type": "new",
        "client_history": "Organization has 12 development teams — no consistent standards.",
        "risk_patterns": "Backstage requires significant configuration and adoption effort — often underestimated.",
        "pm_comment": "Backstage plugins and integrations took 2x more than documentation suggested.",
        "source": "curated",
    },
    {
        "project_description": (
            "CDN modernization for video content delivery (IPTV). "
            "Replacing Varnish 4 with Varnish 7 + new VCL configuration, "
            "adding L2 cache layer (Redis), "
            "origin shield, purge API, "
            "hit ratio and latency monitoring, "
            "handling 10Gbps peak traffic."
        ),
        "actual_hours": 420,
        "project_type": "legacy",
        "client_history": "CDN running for 5 years — Varnish 4 reaching EOL support.",
        "risk_patterns": "VCL between versions — breaking changes in syntax and behavior.",
        "pm_comment": "VCL migration from V4 to V7 had breaking changes — but well documented by Varnish.",
        "source": "curated",
    },
    {
        "project_description": (
            "Regression test automation for billing system. "
            "Test framework (Pytest + Selenium), "
            "600 test cases for billing processes, "
            "CI/CD integration (GitLab CI), "
            "smoke tests after every deploy, "
            "reporting (Allure), "
            "test environment with anonymized production data."
        ),
        "actual_hours": 860,
        "project_type": "new",
        "client_history": "Regression tests done manually by 6 QA engineers — 2 weeks per release.",
        "risk_patterns": "Selenium test automation is brittle — any UI change can cause flaky tests.",
        "pm_comment": "Using Page Object Model from the start was a good decision — tests remain stable.",
        "source": "curated",
    },
    {
        "project_description": (
            "Identity management system migration from Microsoft AD + LDAP to Azure AD B2C + Entra ID. "
            "80k users, account migration, attribute synchronization, "
            "MFA, SSPR, Conditional Access Policies configuration, "
            "updating 40 applications to OAuth2/OIDC (from LDAP bind), "
            "helpdesk training."
        ),
        "actual_hours": 1600,
        "project_type": "migration",
        "client_history": "Client has 40 applications with LDAP auth — each requires separate work.",
        "risk_patterns": "Applications with LDAP bind: many legacy apps don't support OAuth2 — adapter or refactoring.",
        "pm_comment": "8 applications required deep auth refactoring — no simple adapter possible.",
        "source": "curated",
    },
    {
        "project_description": (
            "Sentiment analysis for customer opinions from all channels. "
            "Data integration from: call center (ASR transcripts), email, chat, social media, NPS surveys. "
            "Fine-tuning BERT-large model, "
            "management dashboard (real-time NPS, topics, trends), "
            "alerts on sudden sentiment drop for product/region."
        ),
        "actual_hours": 1140,
        "project_type": "ai",
        "client_history": "Client analyzes NPS manually once per quarter — needs real-time.",
        "risk_patterns": "Call center transcripts have low quality (noise, accents) — ASR preprocessing difficult.",
        "pm_comment": "ASR transcript quality required an additional correction module — unplanned scope.",
        "source": "curated",
    },
    {
        "project_description": (
            "DSL access network management system (xDSL management system). "
            "DSLAM configuration API, line profiling, troubleshooting tool for technicians, "
            "CRM integration (customer line parameter view), "
            "bulk provisioning, line quality degradation alerts (SNR, attenuation). "
            "Stack: Python + Django, PostgreSQL, NETCONF/YANG."
        ),
        "actual_hours": 1380,
        "project_type": "new",
        "client_history": "Operator manages 500k DSL lines — current CLI tools inefficient.",
        "risk_patterns": "NETCONF/YANG integration with devices from different vendors — YANG model incompatibilities.",
        "pm_comment": "YANG models from different DSLAM vendors were incompatible — separate adapters for each.",
        "source": "curated",
    },
    {
        "project_description": (
            "Customer data analytics platform (Customer Data Platform). "
            "Data unification from 8 sources (CRM, billing, network, mobile app, web), "
            "single customer view, predictive segmentation, "
            "marketing tool integration, "
            "Kafka + Spark Streaming pipeline, lakehouse on S3 + Delta Lake."
        ),
        "actual_hours": 3200,
        "project_type": "new",
        "client_history": "Client has data in silos — first CDP implementation.",
        "risk_patterns": "Data quality from 8 sources: each has different keys and formats — deduplication very difficult.",
        "pm_comment": "Identity resolution (linking customer records from different systems) took 35% of project.",
        "source": "curated",
    },
    {
        "project_description": (
            "Automatic product description generation in telco catalogue using LLM. "
            "Templates per product category, tone of voice guidelines, "
            "A/B conversion tests AI vs manual descriptions, "
            "editor approval workflow, "
            "PIM (Product Information Management) integration, "
            "10k products to describe."
        ),
        "actual_hours": 460,
        "project_type": "ai",
        "client_history": "Client has PIM with 10k products — descriptions written manually by editors.",
        "risk_patterns": "LLM generates content requiring verification — approval workflow critical.",
        "pm_comment": "Calibrating prompts per product category took longer than assumed — many iterations with editors.",
        "source": "curated",
    },
    {
        "project_description": (
            "CI/CD platform migration from Jenkins (on-premise) to GitLab CI/CD (cloud). "
            "200 pipelines, Jenkinsfile → .gitlab-ci.yml configuration migration, "
            "runner configuration, SonarQube integration, Nexus → GitLab Packages, "
            "training for 80 developers. Gradual migration — 20 pipelines per month."
        ),
        "actual_hours": 720,
        "project_type": "migration",
        "client_history": "Jenkins for 8 years — large technical debt, many shared libraries.",
        "risk_patterns": "Shared Jenkins libraries: no equivalent in GitLab CI — refactoring required.",
        "pm_comment": "Jenkins shared libraries required rewriting as GitLab CI components — 4 weeks extra work.",
        "source": "curated",
    },
    {
        "project_description": (
            "Network configuration management system (Network Configuration Management). "
            "Automatic configuration backups for 3000 devices (routers, switches, firewalls), "
            "configuration diff, rollback, compliance check, "
            "ticketing integration (changes require a ticket), "
            "Web UI + REST API. Stack: Python + Ansible + PostgreSQL + React."
        ),
        "actual_hours": 1280,
        "project_type": "new",
        "client_history": "Configuration backups done manually via scripts — no consistency or change history.",
        "risk_patterns": "3000 devices from different vendors — Ansible modules have varying maturity.",
        "pm_comment": "Old devices without Ansible support required custom SSH modules — 15% of devices.",
        "source": "curated",
    },
    {
        "project_description": (
            "BI system expansion with real-time analytics module. "
            "Lambda architecture: batch layer (Spark) + speed layer (Kafka + Flink), "
            "real-time KPI dashboard in Grafana, "
            "business alerts (sales drop, churn increase), "
            "8 new operational reports."
        ),
        "actual_hours": 1560,
        "project_type": "new",
        "client_history": "Client has working batch BI system — expanding with real-time.",
        "risk_patterns": "Flink and Kafka require specialists — and are difficult to test in distributed mode.",
        "pm_comment": "Testing failure scenarios in distributed streaming was very time-consuming.",
        "source": "curated",
    },
    {
        "project_description": (
            "Consolidation of 4 monitoring systems (Zabbix, Nagios, Prometheus, Dynatrace) "
            "to single Dynatrace Full Stack platform. "
            "Agent configuration on 400 servers, instrumentation of 60 applications, "
            "alert migration (300 rules), Davis AI dashboards, "
            "old system deprecation, documentation."
        ),
        "actual_hours": 940,
        "project_type": "migration",
        "client_history": "4 monitoring tools = chaos — NOC team checks 4 panels.",
        "risk_patterns": "Dynatrace OneAgent on legacy JVM can cause performance issues.",
        "pm_comment": "2 applications on old JVMs had agent issues — forced JVM upgrade.",
        "source": "curated",
    },
    {
        "project_description": (
            "SIEM deployment (Security Information and Event Management) — Splunk Enterprise. "
            "Integration of 35 log sources (firewalls, servers, applications, AD), "
            "80 threat detection rules (MITRE ATT&CK), "
            "incident response playbooks, "
            "SOC dashboard, ticketing integration, "
            "security analyst training."
        ),
        "actual_hours": 1620,
        "project_type": "new",
        "client_history": "Client has no SIEM — security incidents detected with delay.",
        "risk_patterns": "Splunk: log volumes always larger than assumed — license and storage costs.",
        "pm_comment": "Log volumes were 3x larger than projected — collection architecture redesign.",
        "source": "curated",
    },
    {
        "project_description": (
            "New billing API version (REST v3) with backward compatibility to v1/v2. "
            "12 new endpoints, API versioning, "
            "old endpoint deprecation (18-month plan), "
            "optional GraphQL gateway, "
            "OpenAPI 3.1 documentation, Python/Java SDK, "
            "contract tests (consumer-driven contracts)."
        ),
        "actual_hours": 1020,
        "project_type": "legacy",
        "client_history": "API v1 and v2 used by 40 external partners — backward compatibility critical.",
        "risk_patterns": "Contract tests with 40 partners — each has different interpretation of API contract.",
        "pm_comment": "Coordinating consumer-driven contracts with 40 external partners took 2 months.",
        "source": "curated",
    },
    {
        "project_description": (
            "Personal data consent management platform (Consent Management Platform). "
            "GDPR and ePrivacy compliance, customer consent registry, "
            "web/mobile widget for consent collection, API for marketing systems, "
            "DPO report exports, right to be forgotten (data deletion from 12 systems)."
        ),
        "actual_hours": 1080,
        "project_type": "new",
        "client_history": "Client received a data protection authority fine — urgent CMP deployment.",
        "risk_patterns": "Integration with 12 systems for right to be forgotten — each integration separate.",
        "pm_comment": "2 legacy systems had no data deletion API — required manual procedures.",
        "source": "curated",
    },
    {
        "project_description": (
            "CPE device order handling module for business customers. "
            "Device configuration (router, ONT, set-top box) via ZeroTouch Provisioning API, "
            "shipment tracking, activation, post-installation auto-diagnostics, "
            "customer portal for device management, "
            "warehouse and logistics integration."
        ),
        "actual_hours": 1460,
        "project_type": "new",
        "client_history": "CPE provisioning done manually by technicians — 3 visits per customer.",
        "risk_patterns": "ZeroTouch Provisioning with devices from different vendors — incomplete TR-369 standardization.",
        "pm_comment": "TR-369 (USP) support from one vendor was incomplete — separate adapter required.",
        "source": "curated",
    },
    {
        "project_description": (
            "Helpdesk system migration from Remedy ITSM to ServiceNow. "
            "Migration of 5 years of ticket history (200k records), "
            "ITIL workflow configuration (Incident, Problem, Change, Request), "
            "monitoring integration (Zabbix alerts → ServiceNow), "
            "custom application for telco infrastructure management in ServiceNow. "
            "600 users."
        ),
        "actual_hours": 1760,
        "project_type": "migration",
        "client_history": "Remedy ITSM for 10 years — heavily customized, very rigid.",
        "risk_patterns": "Remedy customizations often impossible to transfer 1:1 to ServiceNow.",
        "pm_comment": "30% of Remedy customizations required redesign for ServiceNow — business decision to simplify.",
        "source": "curated",
    },
]


def generate_curated(output_dir: str = "gepa/data/training") -> int:
    out = Path(output_dir)
    out.mkdir(parents=True, exist_ok=True)

    written = 0
    for example in EXAMPLES:
        fname = out / f"curated_{uuid.uuid4().hex[:8]}.json"
        fname.write_text(json.dumps(example, ensure_ascii=False, indent=2))
        written += 1

    return written


if __name__ == "__main__":
    import sys
    output_dir = sys.argv[1] if len(sys.argv) > 1 else "gepa/data/training"
    count = generate_curated(output_dir)
    print(f"Saved {count} examples to {output_dir}/")

    # Statistics
    types = {}
    hours = []
    for ex in EXAMPLES:
        t = ex.get("project_type", "?")
        types[t] = types.get(t, 0) + 1
        hours.append(ex["actual_hours"])

    print(f"\nType distribution: {types}")
    print(f"Hours range: {min(hours)}h - {max(hours)}h")
    print(f"Median: {sorted(hours)[len(hours)//2]}h")
