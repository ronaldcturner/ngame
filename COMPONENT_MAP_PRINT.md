# NGAME Component Map — Print Version

> Three-part segmented diagram for print publication.
> Connector circles **①** and **②** link the pages: the same symbol that closes one page opens the next.

---

## Figure 1-a — Data Extraction & CPI Analysis

```mermaid
flowchart TD
    A["Data Source
    QuickBooks API or Wave GraphQL"] --> B[Data Extraction Agent]
    B --> C[Ontology Builder]
    C --> D[Today TTL Snapshot]
    F[Yesterday TTL Snapshot] --> E[CPI Analysis Agent]
    D --> E
    E --> G["17-Element Phi-Array"]
    G --> CONN1(("①"))

    style CONN1 fill:#ffffff,stroke:#000000,stroke-width:2px,font-weight:bold
```

*Continues on Figure 1-b at connector ①*

---

## Figure 1-b — Mode Decision & Anomaly Identification

```mermaid
flowchart TD
    CONN1(("①")) --> H{"Mode?"}
    H -->|"Training Mode"| I[Matrix Management Agent]
    I --> J["NGAME_Training_Matrix.xlsx"]
    H -->|"Fraud Analysis Mode"| K[Churn Comparison Agent]
    J --> K
    K --> L["Anomaly Identification Agent
    (Top 3)"]
    L --> CONN2(("②"))

    style CONN1 fill:#ffffff,stroke:#000000,stroke-width:2px,font-weight:bold
    style CONN2 fill:#ffffff,stroke:#000000,stroke-width:2px,font-weight:bold
```

*Continues from Figure 1-a at connector ①  ·  Continues on Figure 1-c at connector ②*

---

## Figure 1-c — Risk Analysis & Warning Generation

```mermaid
flowchart TD
    CONN2(("②")) --> M[Account Mapping Agent]
    M --> N[LLM Analysis Agent]
    O["Asset_Misappropriation.ttl"] --> N
    N --> P[Management Warning Agent]
    P --> Q["NGAME_Fraud_Analysis*.json"]
    P --> R["management_dashboard.json"]

    style CONN2 fill:#ffffff,stroke:#000000,stroke-width:2px,font-weight:bold
```

*Continues from Figure 1-b at connector ②*
