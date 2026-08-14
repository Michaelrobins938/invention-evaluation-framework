# Quickstart prompt

After installing the skill, copy-paste this into your agent tool:

---

Evaluate this invention using the invention-evaluation-engine skill.

The invention submission is in the file `examples/tesla-us433700/submission.md`
inside the installed `invention-evaluation-engine` skill folder. Read it, then
run the complete nine-phase pipeline and produce the final report.

---

When the run finishes, compare the output with
`examples/tesla-us433700/report-tesla-us433700-e2e-v15.md` (the validated
reference report). The pipeline performs live web searches, so the run takes
several minutes and needs network access.