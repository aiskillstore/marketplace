# Audit Reference

## Supported Scope

- Simulate standardized-patient interactions for teaching and rehearsal.
- Return educational feedback, missed-question hints, and debrief support.
- Keep outputs bounded to simulation and training support.

## Stable Audit Commands

```bash
python -m py_compile scripts/main.py
python -c "from scripts.main import PatientSimulator; sim=PatientSimulator('chest_pain'); print(sim.ask('Where does the pain go?')['patient_response'])"
```

## Fallback Boundaries

- If the request asks for real diagnosis, treatment, or emergency advice, stop and restate that the skill is educational only.
- If the requested scenario is unsupported, provide a manual scenario outline rather than claiming a simulated run succeeded.
- If execution fails, return a structured teaching scaffold with learner goals, patient cues, and debrief prompts.

## Output Guardrails

- Separate simulated patient speech from teaching commentary.
- Keep hidden-case facts distinct from revealed information.
- State clearly that final clinical judgment belongs to qualified supervision and real patient evaluation.
