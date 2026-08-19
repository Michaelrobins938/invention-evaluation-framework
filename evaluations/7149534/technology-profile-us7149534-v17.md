# Technology Profile — US 7,149,534 B2

## Plain-language description

Mobile handsets in a cellular network share GPS assistance data peer-to-peer.
A GPS-equipped phone that successfully receives satellite signals generates
assistance data (ephemeris, almanac, reference time, reference location,
ionospheric corrections) and transmits it over the cellular network to peer
handsets that need it, so those peers can acquire satellites and compute their
position faster or in signal-poor environments. The invention adds a
hierarchical-group structure: handsets form ad-hoc or profile-driven groups
with levels and prioritized sub-groups, decide which requests to answer and
whose data to trust (privacy and trust profiles), and coordinate scheduled
sharing so group members take turns refreshing assistance data.

## Feature-to-benefit map

| Feature | User-facing or system benefit | Evidence |
|---|---|---|
| Peer handset acts as GPS-assistance server | Improves time-to-first-fix and sensitivity for requesting handset without network assistance coverage | US7149534B2, abstract; summary; spec pp. 3–4 |
| Assistance data set (ephemeris, almanac, TOW, reference location, ionospheric corrections) | Lets a disadvantaged (e.g., indoor) handset acquire satellites and compute position | US7149534B2, summary; spec pp. 3–4 |
| Hierarchical groups with levels and prioritized sub-groups | Enables prioritized querying (highest-priority sub-group first) and structured information sharing | US7149534B2, claims 3–6; spec pp. 5–6 |
| Ad-hoc / profile-driven group formation | Groups form with or without user initiation based on shared services or user profiles | US7149534B2, claims 7–9; spec pp. 5–6 |
| Trust levels (inner circle / outer circle / world) | Client accepts assistance only from sufficiently trusted peer sources; falls back to secure fixed server | US7149534B2, spec pp. 5–6 |
| Privacy and performance profiles | User controls disclosure of position/aiding info and limits assistance-request frequency (e.g., one per 30 min) | US7149534B2, claims 9–10, 31; spec pp. 5, 7–8 |
| Scheduled periodic data collection | Group members take turns refreshing 2–4-hour ephemeris, keeping all members current via cheap messaging | US7149534B2, claims 36, 44; spec pp. 6–7 |
| Compilation of data from multiple peers | Requesting handset sorts combined data (e.g., by age) to assemble full satellite coverage | US7149534B2, spec pp. 4–5 |

## Innovation assessment

- **What differs from known approaches:** Prior art (US 5,365,450 Schuchman;
  US 5,418,538 and US 5,883,594 Lau) delivered GPS assistance from the cellular
  network infrastructure (fixed nodes). The claimed delta is that a *peer mobile
  device* supplies assistance data over the network, i.e., mobile-as-server, plus
  the hierarchical-group, trust, privacy, and coordinated-scheduling machinery.
- **Combination-obviousness exposure:** Present and significant. Peer-to-peer
  messaging, cellular telephony, GPS assistance data, and group/membership
  concepts were each known. The operative derivation question is whether prior
  art motivated the specific "mobile terminal generates and transmits GPS
  assistance data to a remote mobile terminal via the cellular network" combination
  with the hierarchical-group trust structure. Combination novelty is claimed,
  but derivation risk is the operative question, absent an unexpected result.
- **Claimed as unique:** mobile-generated-and-relayed GPS assistance data over a
  cellular network (claims 1, 15, 23, 37); hierarchical/sub-group and
  priority-based transmission and trust decisions; profile-defined membership
  and transmission; periodic scheduled refresh and automatic transmission.
- **Design-space position:** The inventors' cited-art field (GPS assistance via
  network, assisted GPS for cellular) indicates exploration of network-based
  assistance delivery. This patent sits at the peer-to-peer variant of that
  design space — mobile devices as both client and server — rather than a
  fixed-node server variant.

## Unexpected-result gate

No comparative performance data (e.g., time-to-first-fix measurements, sensitivity
improvements, network-traffic impact) is established by the supplied record. The
proposition enters the work layer with barrier type `insufficient_technical_demonstration`.

## Regulatory scope estimate

The technology is a consumer mobile-communications method (GPS assistance data
sharing between cellular handsets). It is not a medical device or a safety-critical
regulated product. Governing regime for the underlying radio devices is FCC RF/EMC
rules (e.g., 47 CFR Parts 15/22) and the jurisdiction's spectrum/type-approval rules
for handsets; the disclosed method itself introduces no new product-class
authorization. Scope-level burden is **Low** for the method, with the caveat that
handset-level regulatory compliance is a device-manufacturing matter, not an
invention-specific one.

## Development stage

Patent-disclosed method/architecture. Implementation feasibility is plausible given
assisted-GPS and cellular-messaging (SMS/WAP/IP) technologies described in the record,
but no prototype, field trial, or commercial deployment evidence is established from
this intake. Next milestones: demonstration of the mobile-as-server messaging flow on
an A-GPS handset; group-formation and trust-profile protocol design; field test in
network-assisted and unassisted coverage areas; standardization/implementation
assessment (3GPP A-GPS assistance delivery remains the incumbent path).

## Classification candidates

Candidates, not established classifications for the complete invention:

- H04W 4/02 / H04W 4/029 — location-based services (USPTO CPC scheme; candidate).
- H04W 4/20 — services using short message services (SMS) (USPTO CPC scheme; candidate).
- H04W 84/18 — self-organizing/ad-hoc networks (USPTO CPC scheme; candidate).
- G01S 19/05 — providing aiding data to a satellite receiver (USPTO CPC scheme; candidate).
- G01S 19/46 — determining position based on aiding/terrestrial data (USPTO CPC scheme; candidate).
- G01S 19/254 / G01S 19/27 — ephemeris/almanac aiding (USPTO CPC scheme; candidate).
- H04L 67/104 — peer-to-peer networks (USPTO CPC scheme; candidate).
- H04Q 7/20 (IPC, shown on front page); H04M 11/04 (IPC, shown on front page).
- USPC 455/456.6, 455/404.2, 342/357.09 (shown on front page).

## What remains unclear

1. Whether the peer-to-peer assistance approach was implemented in any product or standard.
2. Actual performance benefit (time-to-first-fix/sensitivity) versus network-based assistance.
3. Current ownership, maintenance-fee status, and enforceability (a separate
   current-status check is required; the patent granted December 12, 2006).
4. Any pre-filing public disclosure or offer for sale.
5. Relationship to the later dominant assisted-GPS (A-GPS/SUPL) infrastructure
   that standardized network-based assistance delivery.
