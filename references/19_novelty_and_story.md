# Novelty, Story, and the One Clear Contribution

A paper is not a collection of experiments. It is a short, rigorous, evidence-based technical story with one clear contribution and a takeaway readers care about. This file turns that into artifacts you can check.

---

## 1. The three pillars (clear by the end of the introduction)

| Pillar | Question | Example form |
|---|---|---|
| **The What** | what is the one to three specific, novel claims in a cohesive theme? | "We show that X achieves Y under condition Z." |
| **The Why** | what rigorous evidence supports them? | strong baselines, experiments that distinguish hypotheses |
| **The So What** | why should the community care? | tie to a recognised open problem or practice |

If the contribution cannot be said in one sentence, there is no paper yet. Thesis test:

> We introduce [artifact or idea] for [task] that enables [capability] by [technical insight], and we show [evidence].

If this becomes a list of modules, compress the modules into one insight first.

---

## 2. What kind of novelty is it?

Name the type. It determines the story pattern and the evidence a reviewer will demand.

| Type | The paper's claim | Evidence reviewers expect | Do not claim |
|---|---|---|---|
| New problem or task | this question matters and was not posed | a precise definition, a first baseline set, a metric that fits | a method contribution if there is none |
| New method | this mechanism does something prior ones cannot | fair baselines, controlled ablation isolating the mechanism, cost | gains explained by scale or tuning |
| New evaluation or protocol | prior measurement misses X | evidence the new measure tracks something real (human judgments), robustness, reliability | that the benchmark ranks methods "correctly" without validation |
| New resource | this data or tool enables Y | provenance, licence, quality control, agreement, baselines on it | coverage beyond what was collected |
| New finding or analysis | we learned Z about existing systems | controlled analysis, replication, alternative explanations ruled out | causal language from observation |
| New theory | this guarantee or limit holds | assumptions stated, proof, tightness or empirical check | relevance beyond the assumptions |

---

## 3. The novelty delta (before writing Related Work)

Fill the table in `paper_story.md`:

| Closest work (verified key) | What it does | What it cannot do | What this work adds | Experiment isolating the difference |
|---|---|---|---|---|

Then answer in two sentences: **why is the delta not just scale, data, or tuning?** and **what would a reviewer cite to say "this was done before"?** If you cannot answer, search again (`12`), narrow the claim, or add the experiment that isolates the delta.

Defensible wording while the search is incomplete: "We propose", "We formulate", "Under the tested protocol", "On [dataset], our results indicate". Wording that needs an exhaustive, recorded search: "first", "universally", "outperforms all".

---

## 4. Novelty statement templates

- Problem: "No existing [protocol / dataset / metric] distinguishes [A] from [B], so [consequence]. We introduce ..."
- Method: "[Prior line] assumes [assumption]. We drop it by [mechanism], which [what changes], and show [evidence]."
- Evaluation: "[Metric] collapses [dimensions], hiding [failure]. We separate them and show that [finding] on [n] systems."
- Finding: "Contrary to [common belief], [observation], which we trace to [cause] using [controlled experiment]."

Each template ends in evidence, not adjectives.

---

## 5. The novelty thread (flow around the novelty)

The reader must meet the novelty at every stage, in different words:

| Place | How the novelty appears |
|---|---|
| Title and abstract sentence 1 | the contribution is named |
| Introduction, Niche then Occupy | the gap, then "here we ..." with the key idea |
| Related Work | the delta paragraph on the closest work |
| Method | components marked as new, each with the failure it addresses and its advantage |
| Experiments | each research question maps to a contribution; the ablation isolates the novelty |
| Discussion and Limitations | what was learned and where the novelty stops |
| Conclusion | the contribution restated once, with its strongest evidence |

Put 3 to 5 **Novelty keywords** in `paper_story.md`. Verify with `python3 scripts/paper_check.py PROJECT thread`: each section must contain at least one of them (the figure and diagram tools also mark new components visually).

---

## 6. Story patterns

- **A. Gap between two research lines:** "Line A solves ...; Line B solves ...; neither supports ...; we introduce ..."
- **B. Executable workflow or system:** "Existing methods produce X but practice needs Y; Y is hard because [two failure modes differ]; we separate them." Emphasise interfaces, verification, recovery.
- **C. Benchmark or evaluation:** "Prior evaluations measure ...; they miss ...; we introduce a protocol that tests ...; it reveals ..." Do not claim a method contribution.
- **D. Method insight:** "We observe that ...; this suggests ...; we operationalise it by ..." The observation must be easy to understand and backed by analysis.

Avoid the "naive method then our patch" story unless the paper really is one small fix; motivate from a gap prior work naturally leaves open. Name concurrent work and state the relationship without making it the central opponent.

---

## 7. Claim strength ladder

| Level | Meaning | Where it may appear |
|---|---|---|
| Strong | directly supported by experiments or proof | abstract, introduction, conclusion |
| Careful | partial, mixed, or assumption-dependent | with qualified wording and scope |
| Aspirational | motivation or future direction | introduction motivation, discussion; never results prose |
| Forbidden | contradicted or unsupported | nowhere |

Use "shows" for direct evidence, "suggests" for limited evidence, "is consistent with" for non-causal interpretation. Prefer "supports", "enables", "connects" over "solves" for open problems.

## 8. Naming test

Choose names tied to the task, mechanism, or metaphor. Avoid generic names that already describe a category; avoid names implying a single unified model when the contribution is a workflow; check collisions in related work. The project name becomes the website name (no venue names).

## 9. Contribution test (each bullet)

What is new? Why is it nontrivial? What advantage does it give? What evidence supports it? Rewrite or drop contributions that are only implementation details. Two to four contributions, ideally three, each tied to a table or ablation (`01_ieee_lab_rules.md`).
