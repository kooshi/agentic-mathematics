# Standing rules — part of every brief

*The rules every job in this project's pipeline shares, each with its reason. Every brief names this file in its `standing rules:`
field; it is part of the brief, read in full, so that a brief need only carry what is particular to its job. Keryx is this file's
writer.*

1. **No agents of your own.** Do not use the Agent tool, a fork, a workflow, or anything else that starts another agent: delegation is
   one level deep, and the agent files withhold those tools. *Why:* staffing is the principal's budget, and Keryx reviews by artifact,
   so it cannot review work by an agent it does not know exists. If the work outgrows your context, stop at a saved stage and say what
   is left — a good report, never a failure.

2. **Work in stages, saved.** Add each stage's section to your record, headed "Stage n — SAVED", and commit it before the next stage
   starts. *Why:* a usage halt then costs one stage instead of the job, and a response lost to the output limit cannot be recovered.
   - **Resuming.** If your record already exists, you are resuming: check its last SAVED stage against `git log -- <record>` and
     continue at the first stage not saved. Redo nothing saved.
   - **Working files** a successor would need go under the `data/…` path your brief names, committed with the stage — never in the
     session's scratch directory, and never only in `/tmp`, which may be RAM and dies with the session.
   - **Long runs.** A run expected to exceed about fifteen minutes checkpoints and resumes exactly; your record names the checkpoint's
     path and the resume command (`RUNNING.md` § Building).

3. **Quote statements verbatim, with their source address; never paraphrase.** *Why:* a paraphrase can widen, narrow or empty a
   statement, and the reader cannot tell which — a verifier handed a widened lemma refutes a statement nobody claimed. Your first
   stage checks every quotation in your brief against its source and logs the result; a mismatch is a finding about the brief, and
   Keryx wants it.

4. **Every outcome counts.** A proven theorem about why something is impossible is a result; TRUE, FALSE with a counterexample, and
   GAP at a named step are all results. *Why:* a mind that believes only "yes" is wanted leans toward it, and the defects that flatter
   the work are the ones that survive review (`CLAUDE.md` § Method, a negative measures its enumeration). State each result at its
   grade; say "not found in print", never "first", because a prior-art search shows only where it looked; never raise a grade, a
   scope or a verdict you are copying.

5. **No search, except by the Searcher.** No job runs SAT, MaxSAT or #SAT solvers, MILP/CP or local-search solvers, or exhaustive
   enumerations and sweeps hunting a witness (`CLAUDE.md` § Toolchain has the in-list: hand derivation, computer algebra and exact
   arithmetic, objects given by formula, the Lean kernel, existing checkers on existing certificates, an exact LP whose shape a
   derivation fixed). *Why:* a lane that may search stalls on compute and on nulls that explain nothing; one daily lane chooses the
   searches worth running. A step a search could decide goes in your report's INVENTORY as a `search request`: what it would decide,
   the object, its size. The Searcher (`.claude/agents/searcher.md`) runs searches once a day.

6. **Commits by explicit path.** *Why:* other agents share the tree, and a bare commit takes their half-finished files with yours.
   - `git add <new file>`, then `git commit <paths> -m …`. Never a bare `git commit`, never `git add -A`, never amend (an amend
     rewrites a commit another job may already have read).
   - If the repository has a remote, push after each commit (`git push origin <branch>`); on a ref-lock race, sleep 4 and retry.
     Never force-push: it destroys history another mind may be standing on.
   - Subjects name the job and the stage ("M03-E1: stage 2"), never the finding, because a newly launched agent is shown the most
     recent subjects and a blind mind would read the verdict there. End each message with your harness's attribution lines.

7. **Your record, your tools, and the files you do not write.**
   - Your record is the path your brief names, with a heading **"Theorems this phase proved"**: one line per theorem, with its grade
     and its address, or a line saying it proved none — so that the record job finds every theorem without reading the argument.
   - Your exact checks go in `tools/<job-prefix>_*.py`. Plant a fault in each and watch it fire (`RUNNING.md` § Make the gate fail,
     and watch it fail), because a check never seen failing may be checking nothing. Never edit another job's tools, or a tool a
     record cites as frozen: a result checked by a tool is only reproducible while the tool stays as it was.
   - **One writer per file.** `CLAUDE.md` § The pipeline names the files Keryx alone writes; unless your brief makes you its pen,
     draft edits to them in your record, each naming its slot (the file, the section, and the words it replaces or follows), so the
     edit can be filed verbatim without guessing where it goes.

8. **Never**: an agent id (a string like `a1b2c3…`) in any file, because a later reader could resume that agent by mistake and bill
   its context again; a credential file (`auth.json`, `.env`, keyrings) read; anything about an open milestone written into the
   auto-memory, which every agent is shown at launch. If your brief fences a path — de Bruijn's planner is fenced from the
   derivation's records until its plan is committed — do not read it until your brief allows, because what a mind has seen cannot be
   unseen and the second route it might have found is lost; if a search prints fenced text, stop reading and log the touch in your
   record and your report: the time, the file, and what it carried.

9. **The machine.**
   - Any job over about 2 GiB or 2 minutes runs under `scripts/slot.py --mem <GiB> --cpus <N> -- <cmd>`, with an honest `--mem`.
     *Why:* RAM is the resource whose exhaustion takes the machine down for every job at once. On exit 75, wait ten minutes and retry;
     never raise a cap; after three refusals, report BLOCKED.
   - Never run `lake build`, bare or named; Lean builds go through `./scripts/build.sh` under a slot, in de Bruijn's lane (`LEAN.md`
     § Building has why).
   - Read every exit status directly, never through a pipe, and never chain a commit after a gate with `;`: a pipe reports its last
     command's status, so a failed gate reads as a pass.
   - Stop a process by its PID or process group, never by matching a command line: a pattern also matches the shell that runs it and
     other agents' processes.
   - On any unexplained crash of any process, halt and report. Do not diagnose or retry: working past a crash can turn a fault in the
     machine into lost work.
   - `RUNNING.md` is this rule's long form; read it before any run over about fifteen minutes and before building any tool.

10. **Reading.** Grep `BIBLIOGRAPHY.md` by arXiv id and Zbl number, and look in the paper library its header names, before calling a
    paper unheld or fetching it. Record a reading status per section: an abstract is not a reading, and "recalled, not read" is said
    where it is true, because a paper remembered as read is cited for what it does not say. Never commit a paper's PDF (its licence is
    rarely ours); name it for the library. Propose `BIBLIOGRAPHY.md` rows in your report.

11. **The report.** When you finish, and at any halt you can foresee, write this to the report path your brief names, commit it, and
    end with the same text as your final message — your hand-back reaches Keryx, so send no separate message (a message after a
    hand-back resumes the sender and bills its context again):
    ```
    JOB <id> — <DONE | STAGE n SAVED | BLOCKED: reason>   harness≈<k> (own≈<k>)
    RESULT: <one line per claim: TRUE, FALSE with the counterexample, or GAP at the step; or the result's name and grade>
    RECORD: <path>   COMMITS: <hashes>
    INVENTORY: <one line per item — kind — one line — source address>
    HELD FOR THE COORDINATOR: <a decision or a slip, one line each; or "none">
    ```
    INVENTORY kinds: result, correction owed, prediction scored, slip, tool defect, prior-art debt, stub to mint or re-aim, statement
    defect, generalization, invention signal (`CLAUDE.md` § Method: two truths that contradict, or a whiff of them — both sides quoted
    with their addresses, no side picked), search request, question for another lane. The form is fixed so that Keryx can fold every
    report into the inventory line by line. Mid-job, message "main" only for a question you cannot work around, or a finding that
    cannot wait: a statement defect, a generalization, a refutation — because another job may be building on the statement it touches.

12. **Budget.** Your brief names a size as guidance and a hand-back line; an overrun is not a slip. Leave margin: the context loaded at
    launch is itself large, and agents' own counts of their context run well below the harness's. Hand back at a saved stage before
    your brief's line, because errors rise as a context fills and a successor briefed from your record starts clean.
