# The 15-Step Scientific Writing Workflow (Drake & Han Framework)

Based on *Drake & Han (PLOS Computational Biology, 2025)*: "How to write a scientific paper in fifteen steps".

This framework follows the **logic of discovery** rather than the superficial logic of presentation, separating the work of *thinking* from the work of *phrasing*.

---

## Phase I: Core Anchor and Narrative Flow

### Step 1: Formulate the Working Thesis
- Write the single main point of your study as one short, declarative sentence:
  $$\text{Subject} + \text{Active Verb} + \text{Phenomenon / Scope}$$
- *Example*: "Phase-conditioned multiresolution discriminators prevent pitch-synchronous high-frequency aliasing in lightweight neural vocoders."
- Every paragraph in the manuscript must illuminate this single thesis. If a detail does not advance this thesis, cut it.

### Step 2: Establish the Two-Part Narrative Arc
Answer four core narrative questions:
1. What did we want to learn?
2. Why did we need to learn this?
3. What did we do?
4. What do we know now?
- Center the narrative on a **two-part arc** (e.g., Theory + Experiment; Diagnostic Failure Analysis + Algorithmic Solution; Model Formulation + Empirical Evaluation). One part is too simple to be publishable; three or more parts become unfocused.

---

## Phase II: Methods and Results (Atoms of Evidence)

### Step 3: Enumerate What You Did (Numbered Methods)
- Write an itemized list of actions without writing prose paragraphs:
  1. Extracted 80-bin mel-spectrograms with 25 ms Hann window and 10 ms hop size.
  2. Aligned phonetic intervals using Montreal Forced Aligner (MFA).
  3. Computed bandwise Log-Spectral Distance (LSD) across 4 frequency subbands.

### Step 4: Pair Every Method with its Rationale ("To-Clauses")
- For every item in Step 3, write an infinitive clause stating *why*:
  - *"To evaluate high-frequency energy preservation under acoustic mismatch, bandwise LSD was computed across 4 frequency subbands."*
- Group these linked method-rationale pairs; each group forms the basis of a Methods paragraph.

### Step 5: Itemize Raw Results
- Results are the empirical atoms of new knowledge.
- Every result must map to a method in Step 3, and every method must yield a result.
- Write each result as a clean, unadorned observation:
  - *Result 1*: "Avocodo reduced subband 4 LSD by 1.82 dB compared to HiFi-GAN."
  - *Result 2*: "Voicing decision error remained within 2.1% across all speaker conditions."

---

## Phase III: Framing the Research Space (Swales CARS Model)

### Step 6: Outline Introduction Using Swales's CARS Model
Create A Research Space (CARS) through three explicit moves:
- **Move 1: Establish Territory**
  - Claim centrality (why the broad domain matters to speech/ML).
  - Make topic generalizations (agreed-upon background).
  - Review prior work.
- **Move 2: Create a Niche**
  - Carve out a distinct gap: counter-claim, indicate a gap, question-raising, or highlight an unresolved bottleneck.
- **Move 3: Occupy the Niche**
  - Announce study objectives or hypotheses ("Here, we propose...").
  - Briefly foreshadow findings.
  - State the bulleted contributions.

---

## Phase IV: Discussion, Interpretations, and Caveats

### Step 7: Formulate Findings from Results
- **Finding = Interpretation of results placed in scientific context.**
- A finding often synthesizes several results.
- *Check*: Draw a bipartite graph between Results (Step 5) and Findings (Step 7).
  - Any orphan result must be cut or linked.
  - Any orphan finding unsupported by results must be deleted.

### Step 8: Draft the List of Problem Items (Anticipated Reviewer Objections)
- Itemize all caveats, assumptions, failure modes, boundary limitations, and empirical anomalies as a numbered list.
- Acknowledge where baselines outperform the proposal or where domain shifts degrade scores.

### Step 9: Pair Every Problem Item with an Honest Scientific Response
- For each problem item in Step 8, provide a 1:1 paired response:
  - A qualification (bounding the claim),
  - A synthesis (explaining the underlying trade-off), or
  - An experimental check (quantifying the impact).

### Step 10: Formulate the Closing Thesis
- Final paragraph must not end on a whimper or generic "further research is needed".
- End with: (i) Restatement of the unifying insight; (ii) A concrete practical deployment guideline; or (iii) A precise open research question.

---

## Phase V: Paragraph Architecture and Assembly

### Step 11: Write Boldface Purpose Statements
- Before writing prose, write a single boldface sentence declaring the exact job of each paragraph:
  - **[Purpose: Explain why pitch-synchronous STFT fails in unvoiced fricatives and motivates multiband processing.]**
- Keep these bold markers during drafting and revision; remove them only in final proofing.

### Step 12: Integrate Figures with Narrative Flow
- Figures exist to provide visible proof of the thesis.
- *Figure Caption Rule*: The first sentence of every caption must be a full declarative sentence (Subject + Verb) serving as a standalone title.
- Reading the sequence of caption topic sentences alone must tell the full paper story.

### Step 13: Craft Strong Topic Sentences
- The first sentence of each paragraph must announce its scope:
  - Declaration of finding, turning point, complication, or development.

### Step 14: Craft Forward-Looking Concluding Sentences
- The final sentence of each paragraph must close its announced theme and provide an organic bridge/segue into the next paragraph's premise.

### Step 15: Draft 3–6 Supporting Sentences
- Add only sentences that directly advance the paragraph's declared purpose.
- If a sentence does not advance the purpose, strike it out immediately.
