# Invention Evaluation Framework

> **Evidence-constrained AI evaluation of inventions, patents, technology, intellectual property, commercialization potential, and market opportunity.**

[![Framework](https://img.shields.io/badge/framework-Invention%20Evaluation-blue)](#)
[![Evidence](https://img.shields.io/badge/evidence-constrained-green)](#)
[![Patent Analysis](https://img.shields.io/badge/patent-analysis-orange)](#)
[![Commercial Analysis](https://img.shields.io/badge/commercial-analysis-purple)](#)

**Repository:** [Michaelrobins938/invention-evaluation-framework](https://github.com/Michaelrobins938/invention-evaluation-framework?utm_source=chatgpt.com)

---

## Overview

The **Invention Evaluation Framework** is an evidence-constrained evaluation engine for analyzing inventions and intellectual property across the dimensions that actually matter when deciding whether an invention is worth developing, licensing, investing in, commercializing, researching further, or abandoning.

It combines:

* invention and patent extraction
* claim-domain decomposition
* prior-art analysis
* novelty and anticipation assessment
* obviousness analysis
* patent-family and rights analysis
* patent-landscape analysis
* scientific literature analysis
* technology maturity assessment
* commercialization analysis
* market opportunity analysis
* competitive analysis
* potential partner identification
* evidence sufficiency assessment
* uncertainty decomposition
* evidence recovery
* constraint propagation
* confidence classification
* operational auditing
* consumer-facing report generation

The system is designed around a simple principle:

> **An evaluation should never appear more certain than the evidence supporting it.**

That means the framework does not treat an LLM-generated statement as a fact merely because the statement sounds plausible.

Instead, propositions are decomposed, sourced, classified, challenged, recovered where possible, and explicitly marked when evidence remains insufficient or unavailable.

---

# Why This Exists

Most AI-generated invention evaluations have a fundamental problem.

They are very good at producing something that **looks like an evaluation**.

They are much worse at determining whether the evaluation is actually supported.

A conventional AI-generated report might say:

> "The market is worth $3.2 billion and growing at 14.5% CAGR."

But where did those numbers come from?

A model might say:

> "The patent is novel."

But novel relative to which references?

It might say:

> "The company has an exclusive license."

But does the source establish the license itself, the exclusivity, the field of use, and the financial terms?

Those are different propositions.

The Invention Evaluation Framework treats them as different propositions.

---

# Core Philosophy

The framework is built around **evidence-constrained reasoning** rather than narrative generation.

### Traditional AI report generation

```text
SOURCE
  ↓
LLM
  ↓
Narrative
```

This makes it extremely easy for unsupported assumptions to become indistinguishable from established facts.

### Invention Evaluation Framework

```text
                         SOURCE MATERIAL
                               │
                               ▼
                       ┌─────────────────┐
                       │ SOURCE EXTRACTION│
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ CLAIM / DOMAIN  │
                       │ DECOMPOSITION   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ PROPOSITION      │
                       │ REGISTRY         │
                       └────────┬────────┘
                                │
                    ┌───────────┴───────────┐
                    ▼                       ▼
             ┌──────────────┐       ┌──────────────┐
             │ EVIDENCE      │       │ CONSTRAINTS  │
             │ RETRIEVAL     │       │ & RIGHTS     │
             └──────┬───────┘       └──────┬───────┘
                    │                       │
                    └───────────┬───────────┘
                                ▼
                       ┌─────────────────┐
                       │ EVIDENCE         │
                       │ SUFFICIENCY      │
                       │ CONTROLLER       │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ ANALYTICAL       │
                       │ LAYERS           │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ DECISION MODEL   │
                       └────────┬────────┘
                                │
                                ▼
                       ┌─────────────────┐
                       │ HUMAN-FRIENDLY   │
                       │ REPORT           │
                       └─────────────────┘
```

The result is not merely a generated report.

It is an **auditable evaluation artifact**.

---

# What the Framework Evaluates

An invention is not a single question.

The framework separates evaluation into multiple domains.

## 1. Technology

Questions include:

* What does the invention actually do?
* What is the underlying mechanism?
* What technical problem does it solve?
* What are the essential technical components?
* What differentiates it from known approaches?
* How mature is the technology?
* Has it been demonstrated?
* Has it been commercialized?
* What manufacturing requirements exist?
* What scalability limitations exist?
* What technical failure modes exist?

---

## 2. Intellectual Property

Questions include:

* What patent protects the invention?
* Is the patent active?
* Has it expired?
* What is the filing date?
* What is the priority chain?
* Are continuations or related patents active?
* What is the current family-level IP position?
* Is there meaningful portfolio depth?
* Does the target patent still provide exclusivity?
* Are there blocking patents?
* Is freedom-to-operate likely to be constrained?

The framework deliberately distinguishes:

```text
TARGET PATENT STATUS
        ≠
FAMILY STATUS
        ≠
PORTFOLIO STATUS
        ≠
FREEDOM TO OPERATE
```

An expired patent does not automatically mean the technology is free of IP constraints.

---

# 3. Novelty & Prior Art

The system analyzes individual claim limitations rather than simply asking an LLM:

> "Is this patent novel?"

A claim can be represented as:

```text
CLAIM
 ├── limitation A
 ├── limitation B
 ├── limitation C
 ├── limitation D
 └── limitation E
```

Each reference is then mapped against those limitations.

Example:

| Claim limitation | Prior Art A | Prior Art B | Target |
| ---------------- | ----------: | ----------: | -----: |
| Feature A        |           ✓ |           ✓ |      ✓ |
| Feature B        |           ✓ |           ✗ |      ✓ |
| Feature C        |           ✗ |           ✓ |      ✓ |
| Feature D        |           ✗ |           ✗ |      ✓ |

This allows the engine to distinguish:

### Anticipation

A single prior-art reference contains all necessary claim limitations.

from:

### Combination / obviousness exposure

Multiple references may collectively suggest the claimed combination.

Those are not the same legal question.

---

# 4. Obviousness

The framework does not treat:

> "Nobody found an identical document"

as equivalent to:

> "The invention was non-obvious."

Instead it evaluates factors such as:

* motivation to combine
* technological proximity
* mechanism displacement
* known problem/known solution relationships
* bridge evidence
* combination evidence
* temporal ordering
* whether the specific combination is actually evidenced

A particularly important concept is the **bridge**.

```text
KNOWN TECHNOLOGY A
        │
        │ ?
        ▼
CLAIMED TECHNOLOGY B
```

If the evidence does not establish the path from A to B, the system should not fabricate one.

---

# 5. Literature Analysis

Scientific literature provides a different evidence layer from patent literature.

The framework can evaluate:

* state of the art
* technological adoption
* performance
* clinical validation
* safety
* limitations
* competing architectures
* citation activity
* experimental evidence
* long-term performance
* commercialization signals

This is especially important for inventions where patent documents alone cannot establish whether the underlying technology actually works in practice.

---

# 6. Market Analysis

The framework evaluates:

* market need
* target customers
* market segments
* industry structure
* competitive environment
* growth signals
* commercialization barriers
* regulatory burden
* purchasing behavior
* potential applications
* market-entry constraints
* potential partners

But there is an important distinction:

> **A market estimate is not automatically a market fact.**

The system therefore distinguishes between:

### Established

Supported by structured or authoritative evidence.

### Partially established

Directionally supported but lacking sufficient precision.

### Inferred

Generated from available evidence or industry benchmarks.

### Not established

The evidence is insufficient.

### Unavailable by constraint

The information may exist but cannot reasonably be recovered, such as confidential licensing terms.

---

# 7. Commercialization

The framework asks a more useful question than:

> "Is this invention valuable?"

It asks:

> **"Where does the value actually reside?"**

Possible answers include:

* the original patent
* active continuation patents
* manufacturing know-how
* regulatory approvals
* clinical validation
* customer relationships
* installed base
* proprietary materials
* specialized fabrication
* data
* complementary IP
* brand
* distribution
* network effects
* specific applications

This distinction is critical for expired patents.

---

# 8. Partner Analysis

Potential partners can be classified by role:

### Current licensee

Existing commercialization relationship.

### IP owner

Current rights holder.

### Potential licensee

Organization that could potentially commercialize the technology.

### Technology partner

Organization providing complementary capabilities.

### Manufacturing partner

Organization capable of producing the technology.

### Clinical partner

Organization capable of supporting validation or deployment.

The framework is designed to avoid treating a company name as automatically meaning:

> "This company is interested in this invention."

A potential partner is an **analytical recommendation**, not evidence of commercial intent.

---

# Evidence Architecture

The central architectural concept is the **proposition**.

Every important conclusion can be decomposed into smaller claims.

For example:

```text
P-08-005
Licensing Terms
│
├── P-08-005a
│   Exclusive licensee = Blackrock Neurotech
│
├── P-08-005b
│   License type = exclusive commercial
│
├── P-08-005c
│   Field of use = neural interfaces / BCI
│
├── P-08-005d
│   Royalty rate
│
├── P-08-005e
│   Upfront payment
│
└── P-08-005f
    Milestones
```

This matters because different parts can have different evidence states.

For example:

```text
P-08-005a  ESTABLISHED
P-08-005b  ESTABLISHED
P-08-005c  ESTABLISHED
P-08-005d  NOT_ESTABLISHED
P-08-005e  NOT_ESTABLISHED
P-08-005f  NOT_ESTABLISHED
```

The parent proposition therefore cannot honestly be represented as completely established.

---

# Evidence States

The framework uses evidence states to prevent false certainty.

Typical states include:

| State                       | Meaning                                                            |
| --------------------------- | ------------------------------------------------------------------ |
| `ESTABLISHED`               | Sufficient supporting evidence exists                              |
| `PARTIALLY_ESTABLISHED`     | Some components are supported, but the complete proposition is not |
| `NOT_ESTABLISHED`           | Evidence is insufficient                                           |
| `ESCALATION_REQUIRED`       | Additional investigation is required                               |
| `UNAVAILABLE_BY_CONSTRAINT` | Information cannot reasonably be recovered                         |
| `INFERRED`                  | Analytical inference rather than directly established fact         |
| `CONFIRMED_PRESENT`         | Evidence confirms the relevant condition exists                    |

The exact state vocabulary can evolve with framework versions.

---

# Evidence Debt

A key concept in the framework is **evidence debt**.

Evidence debt occurs when a conclusion cannot yet be responsibly classified because supporting evidence is missing.

For example:

```text
Market Size
    ↓
$3.25B
    ↓
Source quality insufficient
    ↓
PARTIALLY_ESTABLISHED
    ↓
Evidence Recovery Queue
```

The system should not silently convert the number into a fact.

Instead it records the debt.

---

# Evidence Recovery Controller

The Evidence Recovery Controller determines whether unresolved propositions should be:

1. researched further
2. escalated
3. decomposed
4. downgraded
5. classified as unavailable by constraint

This prevents a common failure mode in automated research:

```text
SEARCH FAILED
    ↓
MODEL GUESSES
    ↓
GUESS BECOMES FACT
```

The intended behavior is:

```text
SEARCH FAILED
    ↓
RECORD FAILURE
    ↓
CLASSIFY MISSINGNESS
    ↓
ATTEMPT RECOVERY
    ↓
IF RECOVERY FAILS
    ↓
EXPLICITLY PRESERVE UNCERTAINTY
```

---

# Constraint Propagation

Not every proposition is independently researchable.

Some constraints propagate through the evaluation.

For example:

```text
Patent expired
      │
      ├── Target patent exclusivity = unavailable
      │
      └── Family-level analysis still required
                    │
                    ▼
             Active continuations
                    │
                    ▼
            FTO risk remains
```

The system therefore distinguishes between:

**"This patent is expired."**

and:

**"The technology is free to commercialize."**

The first may be established.

The second does not automatically follow.

---

# Rights & Family Graph

The framework treats patent relationships as a graph rather than a flat list.

Conceptually:

```text
                    ┌────────────────┐
                    │ Priority /      │
                    │ Filing Origin   │
                    └───────┬────────┘
                            │
                  ┌─────────┴─────────┐
                  ▼                   ▼
             Parent Patent       CIP / Continuation
                  │                   │
                  ▼                   ▼
              Expired             Active
                                      │
                             ┌────────┴────────┐
                             ▼                 ▼
                         Continuation      Improvement
```

This allows the evaluation to reason about:

* expired parents
* active descendants
* continuations
* continuation-in-part relationships
* related portfolios
* rights holders
* licensing relationships

rather than stopping at the target patent.

---

# Claim-Domain Decomposition

Patent claims often contain multiple technical domains.

A claim may simultaneously involve:

* mechanical structure
* materials
* electronics
* software
* manufacturing
* chemistry
* biological interaction

The framework decomposes those domains before conducting evidence searches.

This improves retrieval because the search space becomes:

```text
CLAIM
 ├── STRUCTURE
 ├── MATERIAL
 ├── FUNCTION
 ├── MANUFACTURING
 ├── SIGNAL PATH
 └── APPLICATION
```

rather than one enormous natural-language query.

---

# Search Exhaustion

The framework does **not** treat:

> "The search returned nothing"

as:

> "No evidence exists."

Instead, research exhaustion requires an explicit exhaustion proof.

Conceptually:

```text
No result
   ≠
No evidence
```

The system therefore maintains a distinction between:

* search attempted
* search incomplete
* source unavailable
* source inaccessible
* evidence not found
* evidence contradicted
* evidence exhausted

This is particularly important in patent landscapes.

---

# Patent Landscape Analysis

The landscape layer examines:

* patent families
* applicants
* assignees
* jurisdictions
* filing periods
* technology clusters
* portfolio concentration
* active versus expired rights
* potential blocking positions

The output is intended to answer:

> **"Who controls this technical territory?"**

rather than merely:

> "What patents exist?"

---

# Commercial Scoring

The framework produces high-level scores for dimensions such as:

## Technology

Factors can include:

* clinical validation
* fabrication maturity
* scalability
* biocompatibility
* technical differentiation
* development maturity

## IP

Factors can include:

* original patent status
* continuation depth
* portfolio depth
* expiration impact
* active family members
* blocking risk

## Market

Factors can include:

* market size
* growth
* competition
* regulatory barriers
* customer need
* commercialization accessibility

Scores are intended as **decision-support signals**, not objective universal valuations.

A score of `5/6` does not mean:

> "This technology is 83.3% good."

It means the evaluated factors collectively indicate a strong position within the framework's scoring model.

---

# The Human Layer

One of the framework's most important architectural directions is the separation between:

## Evidence representation

What the system knows and how it knows it.

and:

## Human representation

How the system explains what that information means.

The framework therefore aims to produce reports at multiple levels.

### Executive Layer

> What is this?

> Does it work?

> Is it protected?

> Is there a market?

> What is the biggest risk?

> What should I do?

### Commercial Layer

> Who buys it?

> What applications matter?

> Who controls the IP?

> Who are the competitors?

> What are the commercialization paths?

### Technical Layer

> What does Claim 1 actually require?

> Which references disclose each limitation?

> What evidence supports the conclusion?

> Where is the obviousness bridge?

### Audit Layer

> Which propositions remain unresolved?

> What searches were performed?

> Which constraints prevented recovery?

> Which conclusions were inferred?

The framework should **not force an executive to read the audit trail to understand the opportunity.**

The audit trail exists for those who need it.

---

# Consumer-Friendly Reporting

A major design objective is that the final report should be understandable to someone who is **not** a patent attorney, scientist, engineer, or data scientist.

The report therefore follows a progressive-disclosure model.

```text
                 THE BOTTOM LINE
                       │
                       ▼
                WHAT IT MEANS
                       │
                       ▼
                 WHAT TO DO
                       │
                       ▼
               WHY WE BELIEVE IT
                       │
                       ▼
                TECHNICAL DETAIL
                       │
                       ▼
                 AUDIT TRAIL
```

The system should not dumb down the analysis.

It should **translate it**.

For example:

### Internal representation

```text
P-06-005:
PARTIALLY_ESTABLISHED

Human use duration = 30,000+ aggregate days
SAE = 0
Maximum longevity = 9+ years
Chronic yield = <25%
Yield decay = ~2% / month
```

### Human representation

> **The technology has a strong human safety record, but long-term functional stability is more complicated.**
>
> Human use and safety evidence are strong, while electrode performance can decline over time. The evaluation therefore separates **safety** from **long-term recording performance** rather than treating them as one claim.

Same evidence.

Better communication.

---

# Report Design Principles

Generated reports should follow these rules.

## 1. Answer before explaining

The reader should know the conclusion before seeing the supporting machinery.

## 2. Plain English before jargon

Use:

> "The original patent has expired."

before:

> `Legal status = EXPIRED`

## 3. Explain every important uncertainty

Do not merely say:

> `PARTIALLY_ESTABLISHED`

Explain **why**.

## 4. Separate evidence from inference

Never present an inference using the visual language of an established fact.

## 5. Progressive disclosure

Complex evidence should be available without dominating the primary experience.

## 6. Preserve traceability

Every important conclusion should remain traceable back to evidence.

## 7. Never manufacture precision

A market estimate of `$3.25B` should not visually imply the same certainty as a verified patent expiration date.

---

# Example Evaluation

One representative evaluation is the analysis of:

## US 5,215,088 — Three-Dimensional Electrode Device

The evaluation identified a technology that became the foundation of the **Utah Array** neural interface platform.

The original patent is expired, but the surrounding intellectual-property portfolio contains later active patents.

The evaluation therefore demonstrates a central principle of the framework:

> **An expired patent can still represent commercially important technology without the expired patent itself providing current exclusivity.**

The report distinguishes:

```text
ORIGINAL PATENT
     ↓
EXPIRED

TECHNOLOGY
     ↓
COMMERCIALIZED

FAMILY / PORTFOLIO
     ↓
ACTIVE RIGHTS REMAIN

MARKET
     ↓
REAL COMMERCIAL ACTIVITY

LICENSING
     ↓
STRUCTURE ESTABLISHED
FINANCIAL TERMS UNKNOWN
```

This is precisely the kind of distinction the framework is designed to preserve.

---

# What the Framework Is Not

The framework is **not**:

* a substitute for patent counsel
* a legal opinion
* a formal patent validity opinion
* a freedom-to-operate opinion
* a valuation by a certified valuation professional
* a regulatory determination
* a guarantee of commercialization success
* a substitute for clinical review
* a substitute for independent market research

It is an **evidence-based decision-support system**.

The distinction is deliberate.

---

# Why Evidence-Constrained Matters

Large language models are extremely capable of synthesizing information.

They are also capable of producing extremely convincing unsupported claims.

In an invention evaluation, that is dangerous.

Consider these statements:

> "The patent expired."

> "The patent is commercially valuable."

> "The company has an exclusive license."

> "The license generates 5% royalties."

> "The market is worth $3.25B."

These have radically different evidentiary requirements.

The framework treats them separately.

---

# Evidence Hierarchy

The system favors evidence according to its relevance and authority.

Typical evidence categories include:

```text
PRIMARY / AUTHORITATIVE
    Patent records
    Government records
    Regulatory records
    Court records
    Original scientific papers
    Corporate filings
    Official institutional records

SECONDARY
    Peer-reviewed reviews
    Established databases
    Industry reports
    Reputable technical publications

TERTIARY
    News
    Market summaries
    Aggregators
    Search results

INFERENCE
    Model-generated estimates
    Derived calculations
    Industry benchmarks
    Analytical conclusions
```

The framework should preserve the distinction between these categories.

---

# Confidence Is Not the Same as Importance

An important conclusion may have low confidence.

A minor conclusion may have extremely high confidence.

For example:

```text
Patent expiration date
HIGH confidence
HIGH importance

Exact market size
LOW confidence
HIGH importance

Potential partner
MODERATE confidence
MODERATE importance
```

The framework therefore avoids collapsing everything into one generic confidence score.

---

# Evidence Sufficiency

A proposition is evaluated based on whether the available evidence is sufficient for the **specific proposition being asserted**.

This prevents scope creep.

For example:

### Evidence supports:

> "Blackrock is an exclusive licensee."

That does not automatically support:

> "Blackrock pays 5% royalties."

And it certainly does not support:

> "Blackrock pays $2 million upfront."

Each requires its own evidence.

---

# Evidence Debt vs. Unavailable Information

These are intentionally different.

## Evidence debt

Information should theoretically be recoverable.

Example:

> A performance study exists, but the system has not yet retrieved or verified it.

Action:

**Research further.**

## Unavailable by constraint

The information is inherently inaccessible.

Example:

> Confidential royalty terms in a private license agreement.

Action:

**Record the limitation and stop pretending the answer is known.**

This distinction prevents endless research loops.

---

# Operational Audit

Every evaluation should have an operational audit layer.

The audit can record:

* pipeline stages executed
* source acquisition
* extraction status
* search status
* evidence recovery
* unresolved propositions
* constraints
* rights analysis
* claim mapping
* landscape coverage
* rendering status
* report generation status

This makes debugging and quality assurance possible.

---

# Control State

Each evaluation maintains a control state describing the current epistemic condition of the run.

Example:

```text
Run:
RUN-US5215088-v18-20260819120000

Legal Status:
EXPIRED

Bridge:
PARTIALLY_GROUNDED

Evidence Recovery:
ACTIVE

Unestablished Propositions:
4

Constraints:
0
```

The control state exists so the report cannot accidentally imply that the evaluation is more complete than it actually is.

---

# Reproducibility

An evaluation should produce enough metadata to reconstruct:

* what was evaluated
* when it was evaluated
* which framework version was used
* what source material was used
* which evidence was recovered
* which propositions were unresolved
* which constraints were active
* what report version was rendered

Example:

```text
Invention:
US5215088

Framework:
v1.7

Run:
RUN-US5215088-v18-20260819120000

Evaluation Date:
2026-08-19
```

This makes historical comparisons possible when the framework itself evolves.

---

# Versioning

Framework versions should represent **behavioral changes**, not merely cosmetic changes.

Examples of meaningful version changes:

```text
v1.0
Initial evaluation pipeline

v1.5
Evidence sufficiency architecture

v1.6
Evidence recovery and proposition decomposition

v1.7
Control-state and uncertainty improvements
```

Future releases may introduce:

* improved claim decomposition
* stronger evidence recovery
* expanded patent-family reasoning
* improved market evidence controls
* better commercial reasoning
* consumer-layer report generation
* improved visual reporting
* benchmark suites
* regression testing

---

# Suggested Architecture

At a conceptual level:

```text
┌───────────────────────────────────────────────┐
│                 INPUT LAYER                   │
│                                               │
│ PDF / Patent / Invention Submission / URLs    │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│               EXTRACTION LAYER                │
│                                               │
│ Text extraction                               │
│ Metadata extraction                           │
│ Claim extraction                              │
│ Technical element extraction                  │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│             STRUCTURAL ANALYSIS               │
│                                               │
│ Claim-domain decomposition                    │
│ Technical decomposition                       │
│ Proposition generation                        │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│                RESEARCH LAYER                 │
│                                               │
│ Patent search                                 │
│ Prior art                                     │
│ Literature                                    │
│ Market evidence                               │
│ Corporate / licensing evidence                │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│              EVIDENCE LAYER                   │
│                                               │
│ Evidence mapping                              │
│ Confidence                                    │
│ Missingness                                   │
│ Evidence debt                                 │
│ Recovery                                      │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│             REASONING LAYER                   │
│                                               │
│ Novelty                                       │
│ Anticipation                                  │
│ Obviousness                                   │
│ Rights                                        │
│ Commercialization                             │
│ Market                                        │
│ Competition                                   │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│             DECISION LAYER                    │
│                                               │
│ Opportunity                                   │
│ Risk                                          │
│ Commercial actionability                      │
│ Recommended next steps                        │
└───────────────────────┬───────────────────────┘
                        │
                        ▼
┌───────────────────────────────────────────────┐
│              PRESENTATION LAYER               │
│                                               │
│ Executive report                              │
│ Commercial report                             │
│ Technical report                              │
│ Evidence audit                                │
└───────────────────────────────────────────────┘
```

---

# Design Principle: One Evidence Model, Many Views

The system should not maintain separate truth models for:

* executive reports
* technical reports
* HTML
* Markdown
* JSON
* dashboards

Instead:

```text
                    EVIDENCE GRAPH
                         │
           ┌─────────────┼─────────────┐
           ▼             ▼             ▼
       Executive     Commercial     Technical
         View          View           View
           │             │             │
           └─────────────┼─────────────┘
                         ▼
                    Audit Trail
```

This prevents the executive summary from drifting away from the underlying evidence.

---

# Recommended Output Model

A future standardized evaluation object could resemble:

```json
{
  "invention": {
    "id": "US5215088",
    "title": "Three-Dimensional Electrode Device"
  },
  "control_state": {
    "legal_status": "EXPIRED",
    "bridge": "PARTIALLY_GROUNDED",
    "evidence_recovery": "ACTIVE"
  },
  "scores": {
    "technology": 5,
    "ip": 3,
    "market": 3
  },
  "findings": [],
  "propositions": [],
  "evidence": [],
  "risks": [],
  "opportunities": [],
  "recommendations": []
}
```

The actual implementation may differ.

The important principle is that **the report should be downstream of structured evaluation state**, rather than being the primary data structure.

---

# Recommended Report Contract

Every generated report should answer these questions.

## The invention

**What is it?**

## The technology

**How does it work?**

## The problem

**What problem does it solve?**

## The differentiation

**What makes it different?**

## The evidence

**Does it actually work?**

## The IP

**Is it protected?**

## The landscape

**Who else controls this space?**

## The market

**Who would pay for it?**

## The competition

**What alternatives exist?**

## The risks

**What could kill the opportunity?**

## The opportunity

**Where is the strongest commercial path?**

## The decision

**What should happen next?**

---

# Five Decision Questions

The entire framework can ultimately be reduced to five executive questions:

### 1. Is it real?

Does the underlying technology work?

### 2. Is it differentiated?

Does it meaningfully differ from existing technology?

### 3. Is it protectable?

Is there meaningful IP protection available?

### 4. Is it valuable?

Is there a customer, market, or strategic application?

### 5. Is it actionable?

Can someone realistically do something with the opportunity?

These questions provide the human-facing spine of the report.

The detailed technical machinery exists to answer them responsibly.

---

# Example: Expired Patent

An expired patent should not automatically produce:

> **Opportunity = Low**

Nor should commercialization automatically produce:

> **Opportunity = High**

Instead:

```text
Patent expired
      │
      ▼
Original exclusivity gone
      │
      ├──────────────┐
      ▼              ▼
Technology       Active family
validated        members
      │              │
      └──────┬───────┘
             ▼
      Commercial value
             │
             ▼
       FTO analysis
             │
             ▼
     Application-specific
        opportunity
```

This is the kind of reasoning the framework is designed to automate.

---

# Regulatory Analysis

For regulated technologies, the framework can identify:

* regulatory classification
* approval pathways
* investigational pathways
* clinical requirements
* safety requirements
* manufacturing requirements
* biocompatibility requirements
* jurisdiction-specific barriers

However:

> Regulatory information is decision support, not regulatory advice.

The system should explicitly distinguish:

```text
FDA clearance
≠
FDA approval
≠
FDA authorization for every use
≠
Commercial freedom
```

---

# SWOT

SWOT analysis is generated downstream of established findings and analytical conclusions.

It should not be a generic LLM brainstorming exercise.

For example:

### Strength

Must trace to evidence.

### Weakness

Must trace to evidence or explicitly identified technical limitation.

### Opportunity

Should connect to a market or application.

### Threat

Should connect to a competitor, technology, regulatory barrier, IP constraint, or other identifiable risk.

---

# Opportunity Assessment

The framework can express opportunities in structured form:

| Field                | Description                 |
| -------------------- | --------------------------- |
| Sector               | Broad industry              |
| Sub-sector           | Specific market             |
| Industry             | Commercial classification   |
| Product / Service    | What would be sold          |
| Market Need          | Problem being solved        |
| Purchaser            | Who buys                    |
| Distribution         | How it reaches them         |
| Estimated Market     | Evidence-qualified estimate |
| Commercial Barrier   | Key constraint              |
| Opportunity Strength | Framework assessment        |

This turns the report from a patent summary into a **commercial decision tool**.

---

# Competitive Landscape

Competition should be evaluated across technology architectures rather than company names alone.

For example:

```text
INTRACORTICAL
    │
    ├── Rigid penetrating arrays
    │
    ├── Flexible penetrating arrays
    │
    └── High-density arrays

CORTICAL SURFACE
    │
    ├── ECoG
    ├── µECoG
    └── Flexible cortical arrays

MINIMALLY INVASIVE
    │
    └── Endovascular interfaces
```

This makes technological substitution visible.

A competitor does not necessarily need to make the same product.

They may solve the same customer problem through a different architecture.

---

# Failure Modes

The framework is explicitly designed to catch several common AI-analysis failures.

## Hallucinated evidence

A model claims a source establishes something it does not.

### Mitigation

Evidence-level proposition mapping.

---

## Unsupported precision

A market is reported as exactly `$3.25B` despite weak evidence.

### Mitigation

Epistemic classification and market-source qualification.

---

## Legal-status confusion

An expired parent is interpreted as an unencumbered technology.

### Mitigation

Rights/family graph and constraint propagation.

---

## Search failure interpreted as absence

No prior art is found, therefore no prior art exists.

### Mitigation

Search exhaustion controls.

---

## Citation laundering

A citation is attached to a paragraph even though the source supports only one sentence.

### Mitigation

Atomic propositions and evidence mapping.

---

## Executive-summary drift

The report's opening claims become stronger than the underlying analysis.

### Mitigation

Generate human-facing language downstream from established findings.

---

## Renderer data loss

The underlying analysis contains information that disappears during report generation.

### Mitigation

Structured report contracts and renderer validation.

---

# Renderer Philosophy

The renderer is not merely a document formatter.

It is a **semantic presentation layer**.

It must preserve:

* hierarchy
* evidence state
* confidence
* source attribution
* uncertainty
* section relationships
* tables
* claims
* recommendations

A beautiful report that silently drops evidence is worse than an ugly report that preserves it.

Therefore:

> **Rendering correctness is part of evaluation correctness.**

---

# Validation

The framework should validate both:

## Analytical correctness

Did the engine reach a defensible conclusion?

and:

## Presentation correctness

Did the final report faithfully represent the conclusion?

These are separate tests.

```text
SOURCE
  ↓
ANALYSIS
  ↓
STRUCTURED RESULT
  ↓
RENDERER
  ↓
FINAL REPORT
```

A failure at any stage can corrupt the final product.

---

# Testing Strategy

The framework should support several classes of tests.

## Unit Tests

Test individual components:

* claim extraction
* proposition generation
* status classification
* evidence mapping
* score calculation
* report transformation

## Integration Tests

Test interactions:

```text
Patent
 → Extraction
 → Claim Mapping
 → Evidence
 → Evaluation
 → Report
```

## Regression Tests

Run known inventions through newer framework versions.

This is particularly important because improvements to evidence handling can unintentionally alter previously correct conclusions.

## Evidence Tests

Verify that:

* unsupported claims are downgraded
* missing evidence is recorded
* citations map to the correct propositions
* constraints propagate
* unavailable information is not fabricated

## Renderer Tests

Verify:

* all expected sections appear
* evidence tables render
* headings preserve hierarchy
* page breaks work
* tables do not disappear
* executive summaries contain the correct findings
* appendix information remains available

---

# Benchmarking

The framework should eventually maintain a benchmark corpus of inventions with known evaluation characteristics.

Possible benchmark dimensions:

| Benchmark            | What it tests          |
| -------------------- | ---------------------- |
| Prior-art retrieval  | Search quality         |
| Claim mapping        | Element-level accuracy |
| Novelty              | Anticipation reasoning |
| Obviousness          | Combination reasoning  |
| Legal status         | Rights accuracy        |
| Evidence sufficiency | Epistemic discipline   |
| Market evidence      | Source quality         |
| Commercialization    | Business reasoning     |
| Report fidelity      | Renderer correctness   |

The objective is not merely:

> "Did the LLM produce a good report?"

It is:

> **"Did the system preserve the boundary between evidence and inference?"**

---

# Security & Trust

Because invention evaluations may contain confidential intellectual property, deployments should assume that submissions can contain sensitive information.

Important operational considerations include:

* do not expose private patent drafts unnecessarily
* protect uploaded invention documents
* avoid logging confidential source text
* protect API credentials
* separate user submissions from public research sources
* preserve provenance
* avoid publishing confidential evaluations unintentionally

---

# Legal Disclaimer

This framework provides automated research and analytical decision support.

It does **not** constitute:

* legal advice
* patent prosecution advice
* patent validity opinion
* infringement opinion
* freedom-to-operate opinion
* investment advice
* medical advice
* regulatory advice
* valuation certification

Patent status, ownership, licensing, infringement, validity, and enforceability should be independently verified by qualified professionals where material decisions depend on them.

---

# Intended Users

The framework is designed for:

### Inventors

Determine whether an invention has meaningful technical and commercial potential.

### Universities

Evaluate technology-transfer opportunities.

### Technology Transfer Offices

Prioritize inventions for licensing and commercialization.

### Patent Professionals

Accelerate technical and landscape research.

### Corporate R&D

Evaluate external inventions and emerging technologies.

### Investors

Screen technology opportunities before deeper diligence.

### Founders

Determine whether an invention can support a commercial product.

### Researchers

Understand the state of the art and competitive landscape.

### Analysts

Produce structured, evidence-traceable technology evaluations.

---

# Strategic Use Cases

The framework can support decisions such as:

```text
Should we patent this?
        ↓
Should we license this?
        ↓
Should we build this?
        ↓
Should we invest in this?
        ↓
Should we acquire this?
        ↓
Should we partner with this organization?
        ↓
Should we abandon this opportunity?
```

---

# What Makes This Different

The framework is not primarily differentiated by:

> "It uses AI."

AI is the implementation mechanism.

The important differentiation is the **evaluation architecture**.

### 1. Proposition-level reasoning

Complex conclusions are decomposed into atomic claims.

### 2. Evidence sufficiency

The system tracks whether evidence actually supports each claim.

### 3. Explicit uncertainty

Unknowns remain unknown.

### 4. Evidence recovery

Missing evidence becomes a research task rather than a hallucination opportunity.

### 5. Rights-aware reasoning

Expired patents, active family members, and licensing constraints are separated.

### 6. Claim-level prior-art mapping

Novelty analysis occurs at the limitation level.

### 7. Human translation

Technical analysis is converted into understandable decision support.

### 8. Auditability

The path from source → proposition → conclusion remains inspectable.

---

# The Core Mental Model

The framework can be summarized as:

```text
                  INVENTION
                     │
                     ▼
              WHAT IS CLAIMED?
                     │
                     ▼
             WHAT IS EVIDENCED?
                     │
                     ▼
             WHAT IS STILL UNKNOWN?
                     │
                     ▼
              WHAT RIGHTS EXIST?
                     │
                     ▼
             WHAT MARKET EXISTS?
                     │
                     ▼
             WHAT COULD GO WRONG?
                     │
                     ▼
              WHAT IS THE UPSIDE?
                     │
                     ▼
              WHAT SHOULD WE DO?
```

That is the product.

Everything else is implementation.

---

# Roadmap

The framework is actively evolving.

## Evidence Architecture

* [x] Proposition decomposition
* [x] Evidence-state classification
* [x] Evidence recovery controller
* [x] Evidence debt tracking
* [x] Constraint propagation
* [x] Rights/family graph
* [ ] More automated evidence contradiction detection
* [ ] Cross-source evidence triangulation
* [ ] Evidence provenance graph visualization
* [ ] Automated evidence-quality scoring

## Patent Analysis

* [x] Claim extraction
* [x] Claim-domain decomposition
* [x] Prior-art mapping
* [x] Anticipation assessment
* [x] Obviousness analysis
* [x] Patent family analysis
* [ ] Expanded jurisdictional analysis
* [ ] Improved FTO-oriented analysis
* [ ] Automated claim-chart generation

## Commercial Analysis

* [x] Market analysis
* [x] Competitive landscape
* [x] Opportunity assessment
* [x] Partner identification
* [ ] Structured market-data providers
* [ ] Better pricing evidence
* [ ] TAM/SAM/SOM evidence architecture
* [ ] Commercial scenario modeling
* [ ] Revenue opportunity modeling

## Reporting

* [x] Markdown reports
* [x] HTML reports
* [x] Evidence tables
* [x] Operational audit
* [x] Confidence indicators
* [ ] Executive-first report architecture
* [ ] Consumer-friendly language layer
* [ ] Progressive disclosure
* [ ] Interactive evidence exploration
* [ ] Decision dashboards
* [ ] Report quality validation

## Benchmarking

* [x] Real-world invention evaluations
* [x] Regression evaluation
* [ ] Formal benchmark corpus
* [ ] Golden evidence sets
* [ ] Claim-mapping accuracy benchmarks
* [ ] Evidence-sufficiency benchmarks
* [ ] Cross-model evaluation

---

# Current Development Direction

The project is moving from:

> **AI-generated invention reports**

toward:

> **An evidence-constrained invention intelligence system.**

That distinction matters.

The goal is not simply to generate longer reports.

The goal is to build a system where:

```text
MORE DATA
      ↓
BETTER EVIDENCE
      ↓
BETTER STRUCTURED REASONING
      ↓
BETTER DECISION SUPPORT
```

while maintaining:

```text
UNKNOWN
  ↓
UNKNOWN
```

instead of:

```text
UNKNOWN
  ↓
LLM GUESS
  ↓
CONFIDENT PARAGRAPH
```

---

# Design Principles

The project follows several non-negotiable principles.

### Evidence before confidence.

Never increase confidence merely because the narrative sounds convincing.

### Atomic propositions before synthesis.

Break complex claims apart before evaluating them.

### Unknown is a valid result.

The system must be able to say:

> "We don't know."

### Search failure is not evidence of absence.

An incomplete search cannot prove that something does not exist.

### Expiration is not freedom-to-operate.

An expired patent can coexist with active continuation and improvement rights.

### Commercialization is evidence of value, not proof of future value.

Past adoption matters, but it does not guarantee future commercial success.

### Market estimates must carry epistemic labels.

A model-generated estimate should never masquerade as verified market data.

### Legal conclusions require appropriate caution.

The system supports legal research. It does not replace legal counsel.

### The report should explain, not intimidate.

Technical rigor and human readability are not competing objectives.

---

# Philosophy of the Output

A good invention evaluation should leave the reader knowing:

> **What this invention is.**

> **Why it matters.**

> **What evidence supports it.**

> **What remains uncertain.**

> **Who controls the relevant IP.**

> **Where the commercial opportunity exists.**

> **What could destroy that opportunity.**

> **And what should happen next.**

If the reader finishes the report and still has to ask:

> "Okay, but what does this actually mean?"

then the evaluation is not finished.

---

# Contributing

Contributions are welcome in areas including:

* evidence architecture
* patent analysis
* scientific literature retrieval
* market research
* claim mapping
* uncertainty modeling
* evaluation benchmarks
* report generation
* visualization
* renderer validation
* testing
* documentation

When contributing, prioritize **correctness and traceability over impressive-looking output**.

A smaller system that correctly identifies uncertainty is more valuable than a larger system that confidently invents answers.

---

# Research Contributions

The framework is intended to contribute to a broader class of problems involving:

* AI-assisted intellectual-property analysis
* evidence-constrained reasoning
* automated technology assessment
* proposition-level uncertainty
* AI research provenance
* automated commercialization analysis
* structured patent intelligence
* human-readable scientific decision support

The central research question is:

> **How can an AI system perform complex invention evaluation while maintaining an explicit boundary between what the evidence establishes, what can reasonably be inferred, and what remains unknown?**

---

# Project Status

**Active development**

Current framework line:

**Invention Evaluation Engine v1.7**

The architecture is undergoing continued refinement around:

* evidence sufficiency
* evidence recovery
* patent-family reasoning
* claim-domain decomposition
* market evidence qualification
* report fidelity
* consumer-facing presentation
* operational auditing

The system should be considered a research and decision-support platform rather than a finished legal or commercial due-diligence product.

---

# Author

**Michael F. Robinson**

Marketing Science Engineer · AI Systems Architect · Data Pipeline Engineer

Founder, Forsythe Publishing & Marketing

Creator of the Invention Evaluation Framework.

---

# License

See [`LICENSE`](LICENSE) for the applicable license.

---

# Final Perspective

The Invention Evaluation Framework is built around a deceptively simple idea:

> **An invention is not valuable because an AI says it is valuable.**

Its value emerges from the intersection of:

```text
                 TECHNOLOGY
                     │
                     ▼
                 EVIDENCE
                     │
                     ▼
             INTELLECTUAL PROPERTY
                     │
                     ▼
                  MARKET
                     │
                     ▼
              COMMERCIAL PATH
                     │
                     ▼
                  ACTION
```

The job of the framework is to make those relationships explicit.

Not to manufacture certainty.

Not to turn every invention into an opportunity.

Not to bury the reader under an avalanche of P-03-001 identifiers and six-point gauges.

But to answer the question that ultimately matters:

# **What is this invention actually worth pursuing, why, how certain are we, and what should happen next?**