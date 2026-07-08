# NGAME Figures — Captions, Alt-Text, and Long Descriptions

Drop-in copy for the manuscript, formatted per the AAA **Manuscript Preparation Guide**
and **Alt-Text Guidelines for Authors**.

**Placement rule (AAA):** In the article text, include the figure **caption only**. Put the
`[Alt-Text]` line directly under the caption, and the `[Long Description]` line under that.
Figure graphics are submitted as **separate files** (one per figure / per panel).

**Compliance notes**
- Alt-text is **≤150 characters (with spaces)**, contains **no symbols/markup** (phi, mean,
  standard deviation, z-score are spelled out), does not begin with "Figure X shows…", and ends
  with a period.
- These are **complex visuals (flowcharts)**, so each carries a **Long Description** (no length
  limit; rendered as a digital footnote/URL).
- **Multi-panel:** Figure 7 has Panel A and Panel B — each panel is a separate graphic with its
  **own** alt-text and long description; fonts/sizes are identical across panels.
- **Formats:** EPS (preferred vector) + PDF/SVG provided; **600-dpi greyscale** line-art PNGs
  provided for hardcopy. Color files are for the digital edition.
- Figures 4, 6, 7 are the authors' **original work** (no reuse permission needed). If Figure 1
  (ACFE Fraud Tree) is included, add: *Source: Adapted from Association of Certified Fraud
  Examiners 2024.*

---

## FIGURE 4. NGAME Agent Interaction Network
*(Landscape orientation; full-page-width plate.)*

**Files:** `figures/Figure4_agent_network.eps` (color, preferred) · `.pdf` · `.svg` ·
`figures/Figure4_agent_network_gray.eps` · `figures/Figure4_agent_network_gray_600dpi.png`

`[Alt-Text]` Flowchart of NGAME agents grouped into orchestration, data sources, statistical detection, and interpretation and alerting, feeding FRP alerts.

`[Long Description]` A flowchart of the NGAME architecture in four groups. (1) Orchestration: a Phase 1 Director Agent runs training; a Fraud Analysis Flow Manager runs daily analysis. (2) Data and knowledge sources: the QuickBooks Online API, daily ontology snapshots, the training matrix, a rolling buffer, and the asset-misappropriation taxonomy. (3) Statistical detection across eighteen transaction types: data extraction, churn persistence index analysis with a dollar-weighted variant, a sequence slow-burn detector, churn comparison by z-score, and top-three anomaly identification. (4) Interpretation and alerting: account mapping, a local language-model analysis, a deterministic misappropriation-scoring anchor, and a credit-card watch, all feeding a management warning agent that issues high, medium, or low alerts to the Financially Responsible Person.

---

## FIGURE 6. NGAME Training Flow

**Files:** `figures/Figure6_training_flow.eps` (color, preferred) · `.pdf` · `.svg` ·
`figures/Figure6_training_flow_gray.eps` · `figures/Figure6_training_flow_gray_600dpi.png`

`[Alt-Text]` Flowchart of NGAME training: each day extract QuickBooks data, compute CPI, append a matrix column, then derive the baseline mean and deviation.

`[Long Description]` A flowchart of the training pipeline. (1) Management sets the number of training workdays. (2) Each day, the Data Extraction Agent pulls QuickBooks data and writes the current ontology snapshot for eighteen transaction types. (3) The prior snapshot is rotated to become the comparison baseline; day one only establishes that baseline. (4) From day two, the churn persistence index is computed per transaction type as the Jaccard overlap of yesterday and today, alongside a dollar-weighted variant. (5) The Matrix Management Agent appends each day as a new column. (6) After all days, the system derives a per-type baseline mean and standard deviation, plus a dollar-weighted baseline, stored as the training matrix that persists until activity patterns or the chart of accounts change.

---

## FIGURE 7. NGAME Daily Fraud Analysis

*Two panels. In the text, place the figure caption, then the panel descriptions below it:*
- **Panel A:** Detection and triage (Layers 1–2).
- **Panel B:** Interpretation and alerting (Layers 3–4).

### Figure 7, Panel A — Detection & Triage
**Files:** `figures/Figure7_PanelA.eps` (color, preferred) · `.pdf` · `.svg` ·
`figures/Figure7_PanelA_gray.eps` · `figures/Figure7_PanelA_gray_600dpi.png`

`[Alt-Text]` Flowchart of NGAME detection: extract daily data, compute churn index, score deviation by z-score, and rank the top three anomalies.

`[Long Description]` A flowchart of the daily detection and triage stage. (1) At end of workday, the Data Extraction Agent writes the day's ontology snapshot for eighteen transaction types; an optional anomaly injection supports testing. (2) A credit-card watch runs in parallel, independent of the training matrix. (3) The churn persistence index and a dollar-weighted variant are computed and appended to a rolling buffer. (4) A sequence detector computes a multi-day geometric mean to catch slow-burn anomalies once enough days accumulate. (5) Churn comparison scores each transaction type as a z-score against the trained mean and standard deviation, raising high or medium composite alarms. (6) Differences are ranked and the top three anomalies are identified, then passed, with the credit-card flags, to Panel B.

### Figure 7, Panel B — Interpretation & Alerting
**Files:** `figures/Figure7_PanelB.eps` (color, preferred) · `.pdf` · `.svg` ·
`figures/Figure7_PanelB_gray.eps` · `figures/Figure7_PanelB_gray_600dpi.png`

`[Alt-Text]` Flowchart of NGAME alerting: map anomalies to accounts, interpret with a language model and ACFE anchor, then warn the FRP.

`[Long Description]` A flowchart of the interpretation and alerting stage. (1) The top three anomalies from Panel A are mapped to the relevant chart-of-accounts entries. (2) A local language model interprets the flagged accounts against the asset-misappropriation taxonomy, cross-checked by a deterministic scoring anchor based on ACFE scheme priors. (3) The credit-card flags from Panel A are also routed forward. (4) A management warning agent combines these inputs into a risk level and confidence and delivers the warning, via dashboard or email, to the Financially Responsible Person.

---

## File inventory (in `docs/drafts/figures/`)

| Figure | Editable source | Color (digital) | Greyscale (hardcopy) |
|---|---|---|---|
| Fig 4 (landscape) | `Figure4_agent_network.dot` | `.eps` `.pdf` `.svg` | `_gray.eps`, `_gray_600dpi.png` |
| Fig 6 | `Figure6_training_flow.dot` | `.eps` `.pdf` `.svg` | `_gray.eps`, `_gray_600dpi.png` |
| Fig 7 Panel A | `Figure7_PanelA.dot` | `.eps` `.pdf` `.svg` | `_gray.eps`, `_gray_600dpi.png` |
| Fig 7 Panel B | `Figure7_PanelB.dot` | `.eps` `.pdf` `.svg` | `_gray.eps`, `_gray_600dpi.png` |

*Combined (un-split) Figure 7 retained for reference: `Figure7_daily_fraud_analysis.{dot,pdf,svg,png}`.*
*Square 2x2 Figure 4 variant also retained: `Figure4-SQUARE_agent_network.{mmd,svg,png}`.*
