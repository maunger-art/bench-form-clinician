# Benchmark content guardrails

These are hard guardrails for AI-generated blog posts. Benchmark is a specific product with
a specific feature set. Content must describe **only** what Benchmark actually does, in the
language Benchmark uses. Anything below marked "do not reference" must never appear as a
Benchmark feature, recommendation, or capability — not even in passing or as an example.

When a topic would naturally pull in an out-of-scope concept (e.g. an ACL article "wanting" to
mention the ACL-RSI or 90% limb symmetry), either reframe it in Benchmark's terms (percentage
of expected score, normative comparison) or leave it out. Accuracy over completeness.

---

## What Benchmark measures

### Patient-reported outcomes (PROMs) — the ONLY two PROMs in the platform
- **Patient-Specific Functional Scale (PSFS):** patients identify their own functional
  limitations and rate them on a 0–10 scale.
- **Three-dimensional pain score:** the mean of pain **frequency, intensity and duration**.

> Do **not** reference any other validated outcome measure as a Benchmark feature —
> including KOOS, DASH, ASES, Oxford Shoulder Score, VISA-A, or any condition-specific scale.

### Physical performance — four domains
1. **Range of movement.** Accepts data from **any inclinometer tool**. Technology-agnostic.
2. **Endurance.** Timed holds or maximum-repetition protocols.
   *Do not reference VO2 max, lactate threshold, or equipment-based endurance testing.*
3. **Strength.** Technology-agnostic. Accepts **handheld dynamometer** data and **gym-based
   lifts**. Gym-based data is compared against **Strengthlevel.com** normative data; handheld
   dynamometer data against **peer-reviewed literature** normatives. Results are expressed as a
   **percentage of normative expectation** matched to age, sex and weight.
   *Do not reference isokinetic dynamometry or force-plate-based strength testing as features.*
4. **Power.** Jumps and throws. Uses smartphone apps (e.g. **MyJump2**), **medicine balls**, or
   **tape measures**. Force plates / jump mats *can* be used, but always mention the cheaper
   options (smartphone app / tape measure). Technology-agnostic.

---

## How Benchmark expresses results
- **Primary output:** raw score vs the patient's **expected score**, and as a **percentage of
  normative expectation** for their age, sex and weight cohort.
- **No limb symmetry.** Benchmark does **not** calculate a limb symmetry index, does not compare
  left to right, and does not use any fixed symmetry threshold.
  *Do not reference 90% LSI, the "10% rule", or any fixed symmetry threshold.*
- **MCID and expected rate of change** are provided alongside PROM scores to aid interpretation.
- **Activity level** is collected against **NHS guidelines** and flags patients below
  recommended levels.

---

## What Benchmark does with results
- Suggests exercises when a patient falls **below normative thresholds** on a test.
- Recommends specific **training parameters**: sets, reps, load, rest, frequency, and total
  weekly volume per muscle group and movement pattern. Provides **progressions and regressions**.
- Tracks results **longitudinally**, visualising objective data alongside PROMs over time.
- Generates **AI-assisted clinical documentation** via audio transcription — the clinician
  records during/after a session, audio is transcribed and structured into clinical notes.
  (Live in the current version.)

---

## What Benchmark does NOT do — never present these as features
- Hamstring-to-quadriceps ratio.
- Differentiating eccentric / concentric / isometric strength modes.
- Rate of force development.
- Force plates or ground-reaction-force analysis.
- Qualitative movement analysis of any kind.
- Neuromuscular control, dynamic valgus, landing strategy, or movement quality assessment.
- ACL-RSI, Tampa Scale, IKDC, KOOS, or any psychological-readiness or condition-specific scale.
- Time-based progression criteria.

---

## Language

**Use:** percentage of expected score · normative comparison · measurable and comparable
criteria · PSFS · three-dimensional pain score · technology-agnostic · Strengthlevel normative
data (for gym-based testing) · single-leg hop distance · drop-jump RSI.

**Avoid:** eccentric deficit · neuromuscular control · movement quality · dynamic assessment ·
force plate *as a Benchmark feature* · kinesiophobia · ACL-RSI · time-based criteria · 90%
symmetry · the 10% rule · isokinetic · any condition-specific PROM not listed above.

---

## Common AI over-reach to actively avoid
AI-generated physio content routinely references these — Benchmark includes **none** of them:
isokinetic strength testing · force plates as a Benchmark measurement tool · ground-contact
time from force plates · rate of force development · movement-screening tools (e.g. FMS) ·
balance/proprioception testing · psychological-readiness questionnaires · graft-maturation
timelines · blood-flow-restriction protocols · wearable-sensor or accelerometer data ·
condition-specific PROMs beyond PSFS and the three-dimensional pain scale.
