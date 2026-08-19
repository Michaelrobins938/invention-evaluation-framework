# Technology Profile — US5215088

## 1. Idea Description (Plain Language)

A three-dimensional array of tiny semiconductor needles (electrodes) mounted on a rigid silicon base, designed to be inserted into the brain's cortex to interface with neurons. The electrodes are shaped like spires (tapered from base to tip), each at least 1mm long, allowing them to penetrate to the depth where neurons responsible for visual perception reside (~1.5mm below the surface). Multiplexing circuitry on the back of the base allows each electrode to be individually addressed with minimal wiring. The device is primarily intended as a cortical implant for restoring vision to blind patients by stimulating neurons to produce visual sensations (phosphenes).

## 2. Rapid Domain Orientation

**Key terms in this field:**
- **Neural interface / Brain-computer interface (BCI)** — device that connects neural tissue to electronics
- **Cortical implant** — device implanted in the cerebral cortex
- **Vision prosthesis** — device to restore sight to blind individuals
- **Phosphenes** — perceived spots of light produced by electrical stimulation of visual cortex
- **Electrode array** — matrix of electrodes for recording/stimulating neural activity
- **Microelectrode** — electrode with micron-scale features
- **Neural recording/stimulation** — electrical interface with neurons
- **Biocompatibility** — materials compatible with living tissue
- **Charge transfer** — transduction of electronic to ionic current at electrode-tissue interface

**What I don't yet understand:**
- Current state-of-the-art in 3D neural electrode arrays (post-1993 developments)
- How this compares to Utah Array (Blackrock Microsystems) which appears to be a commercial descendant
- Regulatory pathway for cortical implants (FDA HDE/PMA)
- Long-term biocompatibility and stability of the described materials
- Whether the thermomigration/glass melt fabrication methods are still used

## 3. Feature-Benefit Map

| Feature | Technical Detail | User-Facing Benefit |
|---------|-----------------|---------------------|
| 3D spire-shaped electrodes | Tapered semiconductor columns, ≥1000μm length | Penetrates to neuron depth (~1.5mm) for more effective stimulation/recording vs. 2D surface arrays |
| Rigid silicon base | Monocrystalline n-doped silicon, 1.7mm thick | Provides structural integrity for insertion and chronic implantation |
| Electrical isolation at base | Thermomigration (p-n junctions) or glass melt channels | Prevents crosstalk between electrodes; enables individual addressing |
| Multiplexing circuitry | AND gates, X/Y shift registers on back side | Only 5 lead wires needed regardless of electrode count; reduces surgical complexity |
| Charge transfer material | Pt, Ir, or IrOx at distal ends | Efficient electronic-to-ionic charge transduction; lower stimulation currents (1-100μA vs ~3mA for 2D) |
| Tapered/spire geometry | Large cross-section at base, pointed tips | Gradual tissue spreading during insertion minimizes trauma; tips pierce tissue effectively |
| Two fabrication methods | Thermomigration OR glass melt isolation | Flexible manufacturing options; different isolation characteristics |
| Pneumatic/mechanical inserter | Spring-loaded or pneumatic impact mechanism | Rapid insertion prevents tissue dimpling/deformation; consistent placement |
| Passivation coating | Polyimide or SiN/SiO2 | Prevents unwanted charge transfer between tissue and array; long-term stability |

## 4. Innovation Assessment

**What differs from known approaches?**
- **vs. 2D surface arrays**: This invention moves electrodes into the third dimension, penetrating to neuron depth rather than sitting on the cortical surface. This reduces stimulation current requirements by ~100x (μA vs mA) and reduces electrode interaction effects.
- **vs. individual wire electrodes**: The integrated multiplexing circuitry eliminates the need for individual wire connections to each electrode, enabling practical electrode counts.
- **vs. prior 3D arrays**: The specific spire-shaped tapering and the two fabrication methods (thermomigration, glass melt) for creating isolated 3D structures from bulk silicon appear to be novel combinations.

**Combination-obviousness exposure:**
- The individual elements (semiconductor electrodes, multiplexing, 3D arrays, charge transfer materials) were all known. The novelty appears to be in the **specific integration**: 3D spire-shaped silicon electrodes + thermomigration/glass melt isolation + on-chip multiplexing + charge transfer coating.
- **Risk level**: Moderate. A motivated combination argument could reconstruct this from prior-art components (silicon micromachining was well-established by 1989; multiplexing was known; electrode arrays were known).

**Specific technical elements claimed as unique:**
- The specific fabrication process: dicing saw cuts in 3D to create pillars from bulk semiconductor
- Thermomigration-based isolation (from prior art by Cline et al., but applied in this specific way)
- Glass melt isolation in kerfs between electrodes
- The combination of spire shaping via anisotropic etching with the above isolation methods

**Design-space position:**
- This appears to be an early (1989) exploration of 3D silicon neural interfaces. The commercial descendant is likely the "Utah Array" (Blackrock Microsystems), which is a well-known BCI product. This patent may be the foundational IP for that product line.

## 5. Unexpected-Result Gate

**Status: NOT ESTABLISHED**

The patent describes working models and SEM images of fabricated arrays, but does not present quantitative performance data comparing the 3D array to 2D alternatives in a controlled study. The claim that lower currents reduce pathogenic problems and electrode interaction is logical and expected from first principles (closer proximity = less current needed), not an unexpected result.

- **Performance data proposition**: ESCALATION_REQUIRED
- **Barrier type**: insufficient_technical_demonstration

## 6. Regulatory Burden

**Rating: HIGH**

**Governing regime:**
- **FDA**: 21 CFR 882.8955 — Electrode, Neural, Cortical (Class III medical device)
- **Regulatory pathway**: Premarket Approval (PMA) or Humanitarian Device Exemption (HDE) for implants
- **Clinical trials required**: Yes — IDE (Investigational Device Exemption) for human studies
- **Biocompatibility testing**: ISO 10993 series required for implant materials
- **Reasoning**: Cortical implants are Class III medical devices requiring the highest level of FDA scrutiny. The device contacts brain tissue directly, creating significant safety risks. Long-term biocompatibility, electrical safety, and efficacy must be demonstrated through clinical trials.

## 7. Development Stage

**Classification: Prototype (with working models described)**

**Evidence:**
- Working pneumatic inserter described with specific dimensions (0.477 cm ID tube, 1.76g piston)
- SEM images of fabricated arrays (FIGS. 17-20) demonstrate physical realization
- Multiple fabrication methods demonstrated (thermomigration and glass melt)
- Specific etching processes validated (swirl etch, static etch)

**Next milestones for commercialization:**
1. Biocompatibility testing (6-12 months)
2. Chronic implantation studies in animal models (12-24 months)
3. FDA Pre-Submission meeting to define regulatory pathway
4. IDE application for human clinical trials
5. Phase I clinical trial (safety, 2-3 years)
6. Phase II clinical trial (efficacy, 2-3 years)
7. PMA submission and review (1-2 years)

**Estimated timeline to commercialization**: 8-15 years (if pursued from this prototype stage)

## 8. Classification Seed (IPC/CPC Candidates)

| Code | Official Title | Source |
|------|---------------|--------|
| A61B 5/04 | Electrodes specially adapted for measuring or recording electrical signals from muscles or nerves | IPC (from patent) |
| A61N 1/05 | Electrodes specially adapted for electrotherapy; Electrodes specially adapted for implantation into the body | IPC (inferred) |
| A61N 1/36 | Implantable neurostimulators for stimulating brain or spinal cord | IPC (inferred) |
| H01L 21/027 | Manufacturing semiconductor devices using semiconductor material with isolation structures | CPC (fabrication method) |
| H01L 29/06 | Semiconductor devices adapted as rectifiers, amplifiers, oscillators or switches with potential barriers | CPC (semiconductor electrode structure) |
| H01R 43/00 | Apparatus or processes specially adapted for the manufacture of electrets | CPC (electrode array manufacture) |

## 9. Proposition Ledger

| Proposition ID | Version | Schema | Status | Description |
|---------------|---------|--------|--------|-------------|
| P-03-001 | v1 | technical_profile | ESTABLISHED | 3D spire-shaped silicon electrode array with multiplexing |
| P-03-002 | v1 | innovation_assessment | ESTABLISHED | Combination of known elements; moderate obviousness exposure |
| P-03-003 | v1 | performance_data | NOT_ESTABLISHED | Quantitative performance comparison vs. 2D arrays |
| P-03-004 | v1 | regulatory_regime | ESTABLISHED | FDA Class III; PMA/HDE pathway; HIGH burden |
| P-03-005 | v1 | development_stage | ESTABLISHED | Prototype stage with working models |
| P-03-006 | v1 | classification_seed | ESTABLISHED | A61B 5/04, A61N 1/05, A61N 1/36 (initial candidates) |

## 10. What I Still Don't Understand

1. **Current state-of-the-art**: How have 3D neural electrode arrays evolved since 1993? Is this patent the foundation for the Utah Array/Blackrock Microsystems?
2. **Patent family**: Are there continuation patents with broader claims? What is the full family tree?
3. **Commercial history**: Was this technology ever commercialized? What happened to the IP?
4. **Comparison to modern BCIs**: How does this compare to Neuralink, BrainGate, and other modern neural interface approaches?
5. **Long-term performance**: What are the chronic implantation results? Do the electrodes maintain isolation and functionality over years?
6. **Fabrication scalability**: Can the thermomigration/glass melt processes be scaled for mass production?
7. **Inventor current status**: Are the inventors still active in this field? Have they filed related patents?

---

*Profile generated from extracted patent text (US5215088.pdf) on 2026-08-18.*
