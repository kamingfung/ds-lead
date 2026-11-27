# Actionable Feedback & Specifications Grading Guide

Adapted from Ambrose et al. (*How Learning Works: Seven Research-Based Principles for Smart Teaching*, 2010) and Linda Nilson (*Specifications Grading: Restoring Rigor, Motivating Learners, and Saving Faculty Time*, 2014).

---

## 1. The Ambrose Feedback Framework

Feedback is one of the single most powerful drivers of learner learning, but only when it meets four specific criteria:

```
┌────────────────────────────────────────────────────────┐
│               4 CRITERIA OF IMPACTFUL FEEDBACK         │
├─────────────────┬──────────────────────────────────────┤
│ 1. Goal-Directed│ Tied explicitly to the stated ILO   │
│ 2. Targeted     │ Specifies exact strengths and errors │
│ 3. Timely       │ Arrives while work is still fresh    │
│ 4. Actionable   │ Tells learner how to adjust next step│
└─────────────────┴──────────────────────────────────────┘
```

### Contrast: Vague vs. Actionable Feedback

| Ineffective / Vague Feedback | Actionable / Evidence-Based Feedback |
|---|---|
| *"Good job on the boundary layer plot."* | *"Your boundary layer potential temperature plot correctly identifies the capping inversion at 850 hPa. Notice how the lapse rate steepens below 900 hPa—label the convective mixed layer explicitly in your next draft."* |
| *"Weak discussion of model error."* | *"Your model evaluation mentions RMSE, but does not identify the source of bias. To improve, compare daytime vs. nighttime residual errors to evaluate whether turbulent mixing parameterizations are underestimating night-time cooling."* |
| *"You are naturally gifted at math."* (Person praise - promotes fixed mindset) | *"Your step-by-step derivation of the hydrostatic equation is clear and rigorous. Your persistence in checking the unit dimensional balance caught an early error."* (Process praise - promotes growth mindset) |

---

## 2. Specifications Grading (Nilson)

Traditional partial-credit point deduction creates high grading overhead and causes learners to obsess over points rather than understanding. **Specifications Grading** shifts the focus to mastery of standards.

### Core Architecture:
1. **Pass / Revise Thresholds (Binary Specs)**: Every assignment has clear, objective specifications that define high-quality, professional work. Submissions are marked either **Satisfactory (Meets Specs)** or **Revision Needed (Does Not Meet Specs)**.
2. **Tokens / Revision Economy**: Every learner begins the term with 3 "Revision Tokens". A token allows a learner to resubmit an assignment within 7 days after addressing all feedback comments.
3. **Grade Bundles (Tiers)**: Course letter grades are earned by completing predefined bundles of work:
   - **Grade C Bundle**: Meet specs on 80% of Core Labs + Pass 2 Midterm Conceptual Checks.
   - **Grade B Bundle**: Meet specs on 90% of Core Labs + Complete 2 Advanced Problem Sets + Pass 2 Midterm Checks.
   - **Grade A Bundle**: Meet specs on 100% of Core Labs + Complete 4 Advanced Problem Sets + Capstone Research Paper & Presentation meeting all publication specs.

---

## 3. Rubric Design: Analytic vs. Holistic

### Sample Analytic Rubric for a Climate/Code Laboratory Report

| Dimension | Exemplary / Meets Specs (Full Credit) | Satisfactory / Minor Revision | Needs Revision / Resubmit |
|---|---|---|---|
| **Physical Conceptualization (30%)** | Correctly derives governing equations; clearly explains physical mechanisms and boundary conditions. | Minor error in parameter definition, but physical reasoning is sound. | Fundamental physical misconception present; equations incorrect or unjustified. |
| **Code Implementation & Reproducibility (30%)** | Clean, modular Python functions; vectorized array operations; fully documented docstrings and unit tests. | Code runs correctly, but lacks comments or contains inefficient nested loops. | Code throws runtime errors, lacks documentation, or hardcodes magic numbers. |
| **Data Visualization & Legends (25%)** | Standalone figures with bold title, panel identifiers ($a, b$), axis labels with SI units, and defined colorbars. | Graph readable, but missing units on one axis or legend lacks panel context. | Illegible font size, missing labels, inappropriate colormap (e.g. rainbow colormap used for perceptual data). |
| **Scientific Writing & Citations (15%)** | Structured Nature-style abstract; concise subheadings; properly formatted academic citations with DOIs. | Abstract missing one element; minor citation format errors. | Lacks abstract; no subheadings; unreferenced claims. |
