# Market Analysis — US 7,149,534 B2

## Market boundary

The direct technology area is **assisted GPS / location determination for mobile
communications devices** — the provision of GPS assistance data (ephemeris,
almanac, reference time/location, ionospheric corrections) to handsets, and the
location-based services that depend on it (E-911, navigation, location-based
advertising, fleet/asset tracking). Adjacent areas: peer-to-peer/cooperative
positioning, GNSS assistance infrastructure (SUPL/A-GPS), and location analytics.

**Critical status context:** the target US grant is recorded as **EXPIRED
(adjusted expiration 2023-04-04)**. Direct licensing of the US7149534B2 grant is
therefore closed. The market analysis below addresses the technology area and the
commercial context in which the invention's concepts operate, not a live licensing
opportunity for the expired US grant. Family-level rights (EP1356314B1,
DE60138650T, etc.) require a separate current-status check.

## Industry classification (NAICS)

| Field | Value | Basis |
|---|---|---|
| NAICS code (primary) | 334220 | Radio and Television Broadcasting and Wireless Communications Equipment Manufacturing — official definition includes manufacturing of wireless communications equipment; GPS-enabled mobile device manufacturing is an activity match. 2022 edition. |
| NAICS code (service-layer context) | 517312 | Wireless Telecommunications Carriers (except Satellite) — the network layer in which the disclosed method operates. 2022 edition. |
| Taxonomy source | US Census Bureau NAICS 2022 | Official classification authority |

Classification is an activity/product-manufacturing match, not a claim that the
patent itself is classified in NAICS (patents are not NAICS-classified).

## Industry trend data (US Census CBP 2022)

| NAICS | Establishments | Employees | Annual payroll ($000) | 1st-qtr payroll ($000) |
|---|---|---|---|---|
| 334220 (wireless comm equipment mfg) | 664 | 49,776 | 6,074,114 | 1,565,710 |
| 334290 (other comm equipment mfg) | 334 | 12,762 | 1,005,404 | 233,355 |
| 517312 (wireless carriers) | 25,798 | 260,496 | 18,964,583 | 5,656,701 |

Establishment size brackets (NAICS 334220): <5 emp: 201; 5–9: 116; 10–19: 95;
20–49: 111; 50–99: 61; 100–249: 47; 250–499: 16; 500–999: 10; 1000+: 7.

Source: US Census Bureau CBP 2022 downloadable file `cbp22us.zip`, national rows
(`lfo=-`). These are industry aggregates; they do not establish A-GPS-specific
revenue, shipment value, or market size.

## Opportunity structure

- **Product/service:** GPS assistance data delivery for mobile positioning
  (network-based A-GPS, and the peer-to-peer variant disclosed in the target).
- **Need:** fast, accurate mobile location for E-911, navigation, LBS; the
  disclosed method addresses cells lacking network-fixed-node assistance.
- **Purchaser vs end consumer:** carriers/device OEMs purchase positioning
  capability; end users consume location services.
- **Channel:** cellular network infrastructure, device software/firmware,
  standards (3GPP A-GPS/SUPL).
- **Price point / frequency:** infrastructure/software licensing; recurring
  service fees.

## Technical maturity vs commercial readiness

| Dimension | Status | Evidence |
|---|---|---|
| Patent disclosure | CONFIRMED PRESENT | US7149534B2 specification and claims |
| Engineering feasibility | High (components and combination are standard integration) | A-GPS literature (Zadeh, Kingdon, Pihl); landscape |
| Prototype evidence | NOT ESTABLISHED | No prototype record in the supplied intake |
| Production evidence | NOT ESTABLISHED | No production record in the supplied intake |
| Commercial adoption evidence | NOT ESTABLISHED | No product-identity link established; dominant A-GPS path (SUPL/3GPP) is network-fixed-node, not peer-mobile |

Adoption of the specific peer-mobile assistance mechanism is NOT ESTABLISHED. The
technology area (A-GPS/LBS) is mature and widely deployed; the specific mechanism
disclosed in the target is not established as commercially embodied.

## Competitive landscape

- **Direct competitors (peer/cooperative positioning):** none established as
  commercially dominant; the peer-mobile assistance concept appears in post-filing
  patents (Samsung US20100007553, Broadcom US20090079622, GNSS-assistance
  propagation references) but no commercial product-identity link is established.
- **Indirect competitors (network A-GPS):** Qualcomm (gpsOne/SUPL), Broadcom/CSR
  (SiRF GNSS), u-blox, and carrier infrastructure — the dominant, deployed path.
- **Future:** cooperative/context-aware positioning research (Morosi 2013/2014,
  Dovis 2014) indicates continued academic interest, not commercial deployment.

## SWOT

**Strengths:** well-specified disclosure of peer-mobile assistance with
hierarchical-group, trust, privacy, and scheduled-coordination machinery; the
concept anticipates later cooperative-positioning research and patenting.

**Weaknesses:** no performance, prototype, production, or adoption evidence in the
supplied record; the US grant is expired; the dominant A-GPS path remained
network-fixed-node, suggesting the peer-mobile path was commercially secondary.

**Opportunities:** the concept is relevant to modern cooperative positioning,
V2X, and device-to-device GNSS assistance; the expired patent's concepts are
available for use (no licensing needed for the US grant).

**Threats:** network A-GPS (SUPL/3GPP) is entrenched; peer-mobile assistance adds
trust/privacy overhead; no established commercial embodiment of the peer-mobile
mechanism; family-level rights status requires separate diligence.

## Commercial actionability

Scored on the technology area (not the expired US grant):

| Dimension | Score | Rationale |
|---|---|---|
| Market size | High | A-GPS/LBS is a large, mature market (334220: 664 establishments, ~$6.1B payroll; 517312: 25,798 establishments, ~$19.0B payroll) |
| Growth | Medium | Mature A-GPS market; cooperative positioning is emerging research |
| Accessibility | Low | The specific peer-mobile mechanism has no established commercial embodiment; trust/privacy/standardization barriers |
| Competitive intensity | High | Entrenched network A-GPS (Qualcomm, Broadcom, u-blox) |

Two "low/medium" accessibility signals → commercial actionability for the specific
peer-mobile mechanism is **Indeterminate-to-Limited** on the current evidence. The
technology area is large and mature, but the specific mechanism's commercial
readiness and adoption are not established. This is not a financial forecast or
legal opinion.

## Counterfactual-exclusivity audit

No "only partner" or "no other pathway" claim is made. The strongest identified
commercial pathway for the technology area is network A-GPS infrastructure
(SUPL/3GPP); the peer-mobile variant is a secondary, unestablished pathway.
Alternatives (cooperative positioning, V2X) are identified but not established as
commercial.
