# Preliminary Invention Evaluation Report

## US 8,905,955 B2 — Locomotion Assisting Device and Method

**Run status:** SAVED
**Evaluation date:** 2026-08-16
**Evidence basis:** supplied patent PDF; Google Patents records; targeted Google Patents queries; PubMed metadata; FDA device-regulatory guidance.

> Preliminary research only. This is not legal advice, a formal patentability opinion, an infringement opinion, or a freedom-to-operate analysis.

## Executive summary

US 8,905,955 B2 covers a powered lower-limb exoskeleton control method. The user selects a locomotion mode, and a controller actuates motorized leg joints to straighten the leg braces for standing from sitting or bend them for sitting from standing. Dependent claims add tilt-sensor halting, ground-force trend verification, and joint-angle deviation monitoring.

The patent has an October 13, 2008 priority date and is part of a broader ReWalk/Lifeward family. Related family members disclose ground-force-based stance recognition, gait control, stair control, and user-intention signaling. The issued claims in this patent are narrower than the full specification and are principally directed to mode-selected sit/stand actuation with optional closed-loop safety supervision.

The field is technically and commercially relevant but crowded. Earlier Goffer/ReWalk material discloses much of the powered exoskeleton, mode-control, sensor, and sit/stand architecture. The review did not establish a single pre-filing reference that discloses every limitation of claim 1, but it did establish substantial combination-obviousness exposure. A definitive novelty or inventive-step conclusion requires full claim construction, prosecution-history review, date-qualified prior-art mapping, and a complete patent-database search.

## Submission record

| Field | Record |
|---|---|
| Title | Locomotion Assisting Device and Method |
| Patent | US 8,905,955 B2 |
| Inventors | Amit Goffer; Chaya Zilberstein |
| Original applicant | Argo Medical Technologies Ltd. |
| Later assignee | ReWalk Robotics Ltd.; current Google Patents listing Lifeward Ltd. |
| Priority date | 2008-10-13 |
| U.S. filing date | 2013-01-07 |
| Grant date | 2014-12-09 |
| Disclosure history | NOT ESTABLISHED from the supplied record |
| Sale-offer history | NOT ESTABLISHED from the supplied record |
| Prototype/clinical evidence | NOT ESTABLISHED from the supplied record |

## Technology profile

The invention is a closed-loop control system for a wearable powered exoskeleton. A user command selects a maneuver. The controller commands motorized hip/knee or related joints and uses tilt, ground-force, and joint-angle signals to verify that the maneuver follows an expected trajectory. An abnormal signal can trigger an alert, suspension, halt, or return toward a stable stance.

### Feature-benefit map

| Feature | Benefit |
|---|---|
| Trunk and leg braces | Transfers powered forces to the user's limbs |
| Motorized joints | Enables standing, sitting, walking, and stairs |
| Mode-selection control | Gives the user direct maneuver control |
| Ground-force sensors | Supports stance recognition and movement verification |
| Tilt sensor | Supports falling/unsafe-posture detection |
| Joint-angle sensor | Detects abnormal movement trajectory |
| Controller and alerts | Coordinates motion and safety intervention |

### Classification candidates

- A61H3/00 — appliances aiding disabled persons to walk
- A61H1/0237 — lower-limb bending/stretching apparatus
- A61H2201/1207 — electric or magnetic driving means
- A61H2201/5007 — computer-controlled apparatus
- A61H2201/5058 — sensors or detectors
- A61H2201/5061 — force sensors
- B25J9/0006 — exoskeletons
- A61F5/0102 — articulated orthopedic braces/orthoses

These are search candidates, not newly assigned legal classifications.

## Issued-claim analysis

Claim 1 requires an exoskeleton with a trunk support, leg braces, limb-segment braces, motorized joints, ground-force sensors, and a controller. It further requires receiving a control-panel signal selecting a locomotion mode and actuating the joints to straighten for standing or bend for sitting.

Claims 2–8 add tilt sensing, halting after a fall indication, ground-force input, increasing/decreasing-force verification, and joint-angle deviation halting.

## Prior-art and landscape findings

### Key references reviewed

| Reference | Relevance |
|---|---|
| US 7,153,242 B2 | Earlier Goffer powered gait-locomotor apparatus with motorized braces, gait/standing/sitting modes, tilt and joint sensing. Ground-force-sensor limitation was not established from the reviewed record. |
| US 8,096,965 B2 | Same priority family; discloses ground-force sensing, stance classification, mode selection, sitting, standing, gait, stairs, and sensor-based control. Requires family/priority analysis rather than casual treatment as third-party prior art. |
| US 8,348,875 B2 | Related divisional family member with overlapping locomotion, force, and tilt-control disclosure. |
| US 9,526,668 B2 | Related family branch emphasizing locomotion/stair procedures. |
| US 10,792,210 B2 | Vanderbilt powered lower-limb orthosis with autonomous sit/stand/walking control using joint-angle architecture and no required foot-load instrumentation; later priority date. |
| US 10,130,547 B2 | Later ReWalk sitting-support architecture using coordinated joint movement and extendible support columns. |

### Per-gate assessment

| Gate | Assessment | Evidence state |
|---|---|---|
| Utility | High practical utility | Established from disclosed architecture and modes |
| Novelty | Not resolved as a legal conclusion; no single reviewed reference was mapped to every claim-1 limitation | Work layer |
| Inventive step | Moderate combination-obviousness exposure | Work layer; motivation and effective dates require verification |
| Unexpected result | Not established | No comparative performance data supplied |
| Commercial readiness | Not established | Product identity/adoption evidence not completed |
| Current enforceability | Requires verification | Google Patents status is explicitly non-legal |

### Causal bridge test

The principal bridge is integrating a ground-force-sensor-equipped exoskeleton architecture with a control-panel-selected sit/stand sequence. The earlier record establishes the components and general objective, but the precise pre-filing combination, motivation to combine, reasonable expectation of success, and any unexpected result remain unresolved. `bridge_status: UNTRAVERSED`; `bridge_work_state: REQUIRES_VERIFICATION`.

## Literature search

Relevant metadata included:

- Choi et al., “Compact Hip-Force Sensor for a Gait-Assistance Exoskeleton System,” *Sensors* (2018), DOI 10.3390/s18020566.
- Yeung et al., “Design of an exoskeleton ankle robot for robot-assisted gait training of stroke patients,” IEEE ICORR (2017), DOI 10.1109/ICORR.2017.8009248.
- Kim et al., “Admittance control of an upper limb exoskeleton—reduction of energy exchange,” IEEE EMBC (2012), DOI 10.1109/EMBC.2012.6347475.

The literature establishes force sensing and closed-loop exoskeleton control as active technical fields. It did not establish a pre-filing academic publication disclosing the complete claim-1 combination. This is not a confirmed absence finding because the search was not exhaustive across all engineering databases, theses, conference archives, and non-English sources.

## Market and regulatory assessment

Primary markets include powered mobility exoskeletons, spinal-cord-injury rehabilitation, gait training, and sit/stand assistive systems. The buyer set includes users, rehabilitation clinics, hospitals, payers, distributors, and medical-device manufacturers.

Commercial strengths include a concrete control architecture, an identifiable medical use case, and safety supervision. Risks include high validation burden, fitting/training complexity, reimbursement barriers, calibration sensitivity, and a crowded patent landscape.

FDA guidance establishes that medical devices are regulated under the FD&C Act and Title 21 CFR through risk-based controls and possible 510(k), De Novo, PMA, HDE, or exemption pathways. The device-specific classification and pathway were not established in this run. Preliminary regulatory burden: **High**.

No market-size or CAGR figure is included because a consistent, reconstructable market-sizing source was not established.

## Potential partners

Candidate pathways, not exclusivity conclusions:

1. Lifeward Ltd. — current listed portfolio owner and direct family/product relevance.
2. Ekso Bionics — commercial rehabilitation-exoskeleton and feedback/control capabilities.
3. Parker-Hannifin — powered mobility, actuator, and safety-monitoring capabilities.
4. Vanderbilt University — relevant autonomous sit/stand/walking control research.
5. Rehabilitation hospitals and universities — clinical validation and usability studies.

## Operational audit

The following remain open:

- complete public-disclosure and sale-offer chronology;
- USPTO prosecution and maintenance-fee review;
- complete worldwide family status;
- full Espacenet/second-database search;
- exact pre-filing claim-element mapping;
- prosecution-based double-patenting and disclaimer analysis;
- unexpected-result/performance evidence;
- commercial product-identity and adoption evidence;
- exact FDA classification;
- verified licensing interest.

## Reproducible source log

- https://patents.google.com/patent/US8905955B2/en
- https://patents.google.com/patent/US8096965B2/en
- https://patents.google.com/patent/US8348875B2/en
- https://patents.google.com/patent/US7153242B2/en
- https://patents.google.com/patent/US9526668B2/en
- https://patents.google.com/patent/US10130547B2/en
- https://patents.google.com/patent/US10792210B2/en
- https://www.accessdata.fda.gov/scripts/cdrh/cfdocs/cfpmn/pmn.cfm
- https://www.fda.gov/medical-devices/device-advice-comprehensive-regulatory-assistance/how-study-and-market-your-device
- PubMed searches for `powered lower limb exoskeleton control force sensor` and `exoskeleton sit-to-stand robotic assistance`.
