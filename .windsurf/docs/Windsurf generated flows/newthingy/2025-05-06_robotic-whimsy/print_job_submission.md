# 3D Print Job Submission

## Purposenable users (or agentic flows) to submit requests for 3D printing placards, robot parts, or protest art for use in whimsical, meta interventions.

## API Design (Draft)
- POST /api/3d_print
    - object_type: string (e.g. "placard", "robot_part", "protest_art")
    - design_file: string (URL or file upload)
    - material: string
    - color: string
    - quantity: int
    - consent_required: bool

## Safety and Consent
- All print jobs must be reviewed for safety and appropriateness
- No weaponizable or illegal designs
- Human-in-the-loop for approval

## To Do
- Simulation/test harness for print jobs
- Consent workflow integration
- Logging and audit
