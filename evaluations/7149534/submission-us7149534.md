# Invention Submission — US 7,149,534 B2 (Peer to Peer Information Exchange for Mobile Communications Devices)

> Structured submission record captured per `skill-02-gather-invention-submission`.
> Source: user-provided PDF `US7149534.pdf` from Downloads, text-extracted to
> `source/US7149534.txt`. Facts below are drawn from the patent front page,
> abstract, specification, and claims. No inventor interview was conducted;
> fields requiring an inventor statement are explicitly marked as not established.

## 1. Inventors, assignee, and dates

- Inventors: L. Scott Bloebaum, Cary, NC (US); Havish Koorapaty, Cary, NC (US).
- Assignee: Ericsson Inc., Research Triangle Park, NC (US).
- Application: US 09/767,461, filed January 23, 2001.
- Prior publication: US 2002/0098849 A1, published July 25, 2002.
- Patent grant: US 7,149,534 B2, December 12, 2006.
- Patent term extended or adjusted under 35 U.S.C. 154(b) by 801 days.
- Submission date: 2026-08-18 (evaluation intake date).

## 2. Title and technical field

- Title: Peer to Peer Information Exchange for Mobile Communications Devices.
- Technical field: cellular telephony, GPS-equipped mobile radiotelephones,
  peer-to-peer information sharing, GPS assistance data (almanac, ephemeris,
  reference time, reference location, ionospheric corrections), and hierarchical
  ad-hoc group formation over a wireless communications network.
- Classification shown on the patent: Int. Cl. H04Q 7/20, H04M 11/04;
  USPC 455/456.6, 455/404.2, 342/357.09. Field of search spans 455/456.x,
  342/357.x, 709/2xx, 713/200, 701/2xx.

## 3. Short description

Mobile communications devices connected to a cellular network can share data by
acting as both clients and servers: a GPS-equipped handset generates GPS
assistance data from satellite signals it receives and transmits that data
over the cellular network to peer handsets, which use it to determine a
reference location. The invention also discloses hierarchical groups of mobile
devices (including sub-groups and priorities) for information sharing, with
profile- and trust-based control over which requests are answered and whose
data is accepted.

## 4. Detailed description

The preferred embodiment is a cellular telephone with an integrated GPS
receiver. A handset in a favorable signal environment demodulates GPS
navigation messages (ephemeris, almanac, clock corrections), stores them, and
computes its own position. A second handset needing position assistance sends
a query (via the radio base stations and core network) either to a specific
peer or to all group members; the responding handset may supply a list of
visible satellites with ephemeris and clock corrections, approximate
time-of-week (TOW), approximate position, ionospheric/differential
corrections, and satellite almanac. The requesting handset may compile data
from multiple peers and sort it (e.g., by data age).

Additional disclosed aspects:

- **Hierarchical groups.** Groups may have one or more levels and sub-groups;
  each sub-group may be assigned a priority. A phone needing assistance queries
  the highest-priority sub-group first, then lower-priority ones. Requests may
  be classified by hierarchy level, and a handset may choose to respond or not
  based on profile and classification. Responses may be accepted only from
  certain group members.
- **Group formation.** Groups form ad-hoc, with or without user initiation,
  or automatically based on user profiles (e.g., profile indicates joining a
  group for a class of information-sharing service when one is found). A group
  leader/host may maintain membership and enforce privacy constraints; a
  server within the cellular or backbone network may alternatively maintain
  group membership and status.
- **Trust model.** Because peer-supplied assistance data is not guaranteed
  valid, a client may assign trust levels to groups (e.g., inner circle =
  family, outer circle = friends and associates, world = everyone else) and
  accept assistance accordingly, falling back to a secure fixed server if no
  trusted peer source meets criteria.
- **Coordinated sharing techniques.** (a) Regularly scheduled collection: group
  members take turns downloading ephemeris (valid 2-4 hours) directly from
  satellites and distributing it to peers via cheap messaging, staggering
  schedules so one member refreshes every 2 hours. (b) Supply from a peer with
  good signal-to-noise ratio to a peer in a disadvantaged environment (e.g.,
  indoor) via the cellular infrastructure. (c) Relaying data from a network
  assistance area to a handset travelling into an unassisted area. (d) Cost
  reduction by sharing a single network-assisted download among the group.
- **Other data.** Exchange of phone numbers, e-mail addresses, database
  synchronization, games, music files. Communication over SMS, WAP, or IP.
  Data may also be exchanged during an ongoing voice call.
- **Privacy and performance profiles.** Users control privacy of position and
  aiding information (globally or per user/group). Profiles may encode desired
  standby/talk time trade-offs, e.g., limiting assistance requests to one every
  30 minutes or on an as-needed basis.
- **Applications.** GPS-assistance-sharing applications downloadable from a web
  portal, possibly as a browser plug-in.

## 5. Background / related research identified in the record

The patent discusses the requirement for a cellular phone to know its cell,
location-sensitive applications (targeted advertising, travel directions,
enhanced 911), and the desirability of providing GPS assistance data to
handsets to improve time-to-first-fix and sensitivity. It cites prior
network-based assistance approaches: US 5,365,450 (Schuchman et al.), US
5,418,538 (Lau), US 5,883,594 (Lau). It identifies the problem that a
GPS-equipped phone may sit in a cell lacking GPS assistance data, and the
desire for an alternate source.

## 6. Innovation claims stated in the patent

- **Claim 1 (independent, apparatus):** a mobile terminal comprising a GPS
  receiver to receive GPS data, a cellular transceiver to communicate with a
  wireless communications network, wherein the terminal generates GPS
  assistance data from the received GPS data and transmits the GPS assistance
  data to a remote mobile terminal via the wireless communications network.
- **Claim 15 (independent, apparatus):** a mobile terminal with a cellular
  transceiver, wherein the terminal receives GPS assistance data via the
  wireless network generated by a remote mobile terminal from GPS data the
  remote received, and determines a reference location from that assistance
  data.
- **Claim 23 (independent, method):** receiving GPS data from an external
  source, generating GPS assistance data, determining whether to transmit the
  assistance data to a remote mobile terminal, and transmitting it based on
  that determination.
- **Claim 37 (independent, method):** receiving GPS assistance data from a
  remote mobile terminal, determining whether to trust that data as valid, and
  determining a reference location based on it.
- Dependent features: group membership (hierarchical, sub-groups, priorities,
  ad-hoc, geographic proximity, profile-defined membership); trust decisions
  based on hierarchy level/sub-group/priority; transmission responsive to
  request or automatic; periodic retrieval and distribution; profiles for
  transmission decisions.

## 7. Proof-of-concept and commercialization status

- Proof-of-concept status: Not established from the supplied patent PDF alone.
- Product commercialization evidence: Not established from the supplied patent
  PDF alone.
- Production or sales evidence: Not established from the supplied patent PDF
  alone.
- Development stage for this record: Patent-disclosed implementation;
  engineering maturity and commercial readiness require separate evidence.

## 8. IP posture

- Patent family / continuity: none disclosed on the front page beyond the
  application; the notice states a 801-day term adjustment under 35 U.S.C.
  154(b).
- Government rights: none disclosed in the record.
- Patent term/status: the supplied PDF confirms grant on December 12, 2006, but
  current enforceability and expiration require a separate current-status check;
  this evaluation is not an FTO opinion.

## 9. Public disclosure and sale-offer history

- Public disclosure before the January 23, 2001 filing date: **NOT ESTABLISHED**.
  No inventor statement or complete disclosure history was supplied.
- Patent publication dates established from the PDF: US 2002/0098849 A1 on
  July 25, 2002; US 7,149,534 B2 on December 12, 2006. These are post-filing
  disclosures.
- Sale offer / commercial offer dates: **NOT ESTABLISHED**.
- Required follow-up: obtain an inventor or rights-holder statement covering
  talks, publications, demonstrations, offers for sale, grants, and social-media
  disclosures, each with a date. This intake gap remains in the Operational
  Audit and must not be silently treated as "none."

## 10. Intake limitations

This is a public-patent test run, not an inventor interview. Patent-record facts
are separated from unestablished proof-of-concept, disclosure-history,
commercialization, and current legal-status propositions. Patentability and
regulatory statements in any downstream report are preliminary and not legal
advice.
