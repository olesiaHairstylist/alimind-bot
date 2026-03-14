AliMind — System Architecture v1
AliMind is a quiet city assistant built around reliable public information. The system transfers official
and open data sources into a Telegram bot interface to provide fast, structured access for everyday
life in the city.
1. Core Principle
• AliMind does not create information.
• The system collects and structures public and official sources.
• Telegram is used only as the interface layer.
2. Data Flow
• Source websites
• Parsers
• Data validation
• Normalization
• Snapshot storage
• Telegram bot responses
3. Information Layers
• City events (pharmacies, outages)
• Important city services
• Residence permit information (documents and rules)
• Transport and infrastructure
• Real estate information
• Active life (sports and activities)
4. Service Layer
• Partner cards embedded inside sections
• Partners provide real services in the city
• No aggressive advertising
5. Monetization Layer
• Lead delivery through partner requests
• Token model for receiving leads
• Payment only for delivered requests
6. City Events Engine
• Duty pharmacies
• Water outages
• Electricity outages
• Updated daily through sources
7. Infrastructure
• Telegram bot (aiogram)
• Server (VPS)
• Scheduler for updates
• Data stored in JSON snapshots
8. Geographic Model
• Pilot city: Alanya
• Architecture allows expansion to other cities
9. Interface Philosophy
• Minimal buttons
• Short answers
• No noise or marketing pressure
• Honest message when data is missing
10. Strategic Goal
• Become a reliable everyday city assistant
• Provide fast orientation in city life
• Build a calm ecosystem of useful services