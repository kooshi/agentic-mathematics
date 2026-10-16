# Why `.claude/settings.json` says what it says

*JSON carries no comments, so each setting's reason is here. Keryx writes both files; a change to one is a change to the other in
the same commit.*

| setting | what it does | why |
|---|---|---|
| `"outputStyle": "keryx"` | makes the top-level session Keryx: `.claude/output-styles/keryx.md` (the `keryx` identity, then the coordinator's workflow) becomes its output style | an output style survives every compaction, where a file read at the start of a session does not; the coordinator is the one mind whose identity must hold for the whole run. An output style applies to whatever runs as the main session, so `claude --agent poros` run directly would hold two identities: pass `--settings '{"outputStyle":"default"}'` with it. A lane launched by Keryx as a subagent never receives the style. |
| `"skillOverrides"`: the four cores `user-invocable-only` | hides `keryx`, `poros`, `ephodos` and `debruijn` from the model's skill list | each lane already carries its identity in its agent file; a mind that saw the other cores in its skill list could load a second identity and run two standards at once. The cores stay invocable by the person at the keyboard. The companions stay visible, because the lanes invoke them fresh by design. |
| `"CLAUDE_CODE_MAX_SUBAGENT_SPAWN_DEPTH": "1"` | the harness refuses an agent launched by an agent | delegation is one level deep: the coordinator reviews by artifact and can review only work it knows exists, and a delegate that delegates spends the principal's budget silently. The agent files also withhold the Agent and Workflow tools; this setting is the backstop if one forgets. |
| `"TZ": "UTC"` | every process the harness starts reads time in UTC | dates and times in records, commit messages, briefs and file names are compared across machines and sessions; one zone makes "before" and "after" mean the same thing everywhere, and blindness is dated by commit order. |
