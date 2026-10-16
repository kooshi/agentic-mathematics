# Standing rules — part of every brief

*A working template. Copy it into the project's briefs directory, fill every `<…>`, and delete a rule only when its reason no
longer holds. Every brief names this file in its `standing rules:` field and says "it is part of this brief; read it in full."*

1. **No agents of your own.** Do not use the Agent tool, a fork, a workflow, or anything else that starts another agent: delegation
   here is one level deep. The reason is in two parts. Staffing is the principal's budget decision, and an agent you start overrides it
   silently. And the coordinator reviews by artifact, so it cannot review work by an agent it does not know exists. If the work
   outgrows your context, stop at a saved stage and say what is left — that is a good report, never a failure.

2. **Work in stages, and save after each one.** Add the stage's section to your record, headed "Stage n — SAVED", and commit it before
   the next stage starts, because a response lost to an output limit or a usage halt cannot be recovered, and a saved stage makes a
   halt cost one stage instead of the job. If your record already exists when you start, you are resuming: read it and your brief,
   check the last SAVED stage against `git log -- <record>`, and continue at the first stage that is not saved.

3. **Quote statements verbatim; never paraphrase.** Every statement you hand on goes in a quotation with its source address, because a
   paraphrase can widen a statement, narrow it, or empty it, and the reader cannot tell which. Your first stage checks every quotation
   in your brief against its source and logs the result — a mismatch is a finding about the brief, and the coordinator wants it.

4. **Every outcome counts.** TRUE, FALSE with a counterexample, and a gap at a named step are all results. Do not lean toward yes: audit
   a result you like as hard as one you dislike, since the defects that flatter the work are the ones that survive. State each result at
   its grade, with its count of independent minds; never raise a grade, a scope, or a verdict you are copying.

5. **Commits by explicit path.** Other agents share the tree. `git add <path>` then `git commit <paths> -m …`; never `git add -A`, never
   amend, never force-push. Subjects are neutral — "<job id>: stage n" — because a newly launched agent is shown recent commit subjects,
   and a blind job must not read a verdict there. <The project's push rule.>

6. **Your record.** It lives at the path your brief names. Give it a heading "Results this job produced": one line per result, with its
   grade and its address. Put working files a successor would need under the data path your brief names, committed with the stage;
   scratch space dies with the session.

7. **Fences.** If your brief fences a path and a search prints fenced text, stop reading it, and log the touch — the time, the file,
   what it carried — in your record and your report at once. A disclosed touch costs little; an undisclosed one voids the grade. Never
   copy an agent id into a file, and never read credential files.

8. **Reading.** An abstract is not a reading. Record, per source, what you read and at what depth; say "recalled, not read" where that
   is true.

9. **The report.** When you finish, and at any halt you can foresee, write it to the report path your brief names and send the same text
   to the coordinator by message:
     JOB <id> — <DONE | STAGE n SAVED | BLOCKED: reason>
     RESULT: <one line per claim: TRUE, FALSE with the counterexample, or GAP at the step; or the result's name and grade>
     RECORD: <path>   COMMITS: <hashes>
     INVENTORY: <one line per item — kind — one line — source address; kinds: result, correction owed, prediction scored, slip,
                tool defect, prior-art debt, stub to mint, fence touch>
     HELD FOR THE COORDINATOR: <a decision or a slip, one line each; or "none">
   Your last words are exactly "<id> idle; report sent to the coordinator", with no content: a hand-back is delivered to whichever
   agent last woke you, which may not be the coordinator.

10. **Budget.** Your brief names a size, as guidance, and a hand-back line. Leave margin: your own count of your context runs below the
    harness's.
