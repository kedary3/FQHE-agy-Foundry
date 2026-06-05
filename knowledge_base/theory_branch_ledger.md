# Theory Branch Ledger

This ledger is concise durable memory for theoretical avenues. It prevents the
Director and Theory Agent from repeatedly spending loop budget on stalled
branches unless explicit revival criteria are met.

## Bootstrap

{
  "branches": [
    {
      "branch_id": "generic-candidate-consensus",
      "title": "Assume a candidate state is correct before evidence review",
      "status": "pruned",
      "rationale": "Project rules require Pfaffian, anti-Pfaffian, PH-Pfaffian, CFL, stripe/nematic, and other candidates to remain hypotheses until evidence-labeled support is validated.",
      "revival_criteria": "Revive only if a future Director-approved task asks to audit a specific candidate under a specified Hamiltonian and evidence label."
    },
    {
      "branch_id": "finite-size-as-thermodynamic-proof",
      "title": "Treat finite-size numerical trends as thermodynamic proof",
      "status": "pruned",
      "rationale": "Finite-size ED or fixture results must be numerical evidence for specified systems, not exact thermodynamic conclusions.",
      "revival_criteria": "Revive only as a falsification target or if paired with a controlled finite-size scaling argument and explicit limitations."
    },
    {
      "branch_id": "finite-width-ll-mixing-checks",
      "title": "Finite-width and Landau-level-mixing analytical checks",
      "status": "active",
      "rationale": "These perturbations are experimentally relevant and can generate concrete Hamiltonian terms or observables for gated numerics.",
      "revival_criteria": ""
    },
    {
      "branch_id": "laughlin-fixture-orchestration-only",
      "title": "Use Laughlin N=3 fixture for orchestration validation only",
      "status": "validated",
      "rationale": "The small fixture verifies reporting and numerical plumbing but is not evidence for the ν=5/2 half-filled second Landau level.",
      "revival_criteria": ""
    }
  ]
}
