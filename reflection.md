# PawPal+ Project Reflection

## 1. System Design

**a. Initial design**

- Briefly describe your initial UML design.
- What classes did you include, and what responsibilities did you assign to each?

My initial UML design has four classes that separate the data (who and what needs care) from the planning logic (deciding what gets done today). An Owner has one or more Pets, each Pet has zero or more Tasks, and a Scheduler reads the Owner's tasks and builds a daily plan from them.

- **Task**: Represents a single care activity, such as a walk, feeding, or medication. It stores the title, duration in minutes, priority (low/medium/high), category, and whether it has been completed. Its only behavior is marking itself complete.
- **Pet**: Represents one animal (name, species, age) and owns the list of care tasks that pet needs. It is responsible for adding and removing its own tasks.
- **Owner**: Represents the person using the app. It holds the owner's name, how many minutes they have available in the day, their preferences, and their list of pets. It can add pets and gather all tasks across every pet, so the scheduler has one place to get everything that needs doing.
- **Scheduler**: Holds the planning logic. Given an Owner, it sorts tasks by priority, checks whether each task fits in the remaining time, builds the daily plan, and explains why the plan was chosen.

I made Task, Pet, and Owner Python dataclasses because they mostly hold data, which keeps them short and readable. Scheduler is a regular class because its job is behavior rather than storage. Keeping the scheduling rules in one class means I can change how plans are built without touching the data classes.

**b. Design changes**

- Did your design change during implementation?
- If yes, describe at least one change and why you made it.

Yes, in several ways. The first change happened before any logic was written: my UML gave `Task` a `title` and a `category`, but the assignment asked for a description, time, frequency, and completion status, so I renamed and replaced those fields and updated the UML to match.

The biggest change came with recurring tasks. My original `mark_complete()` just set a flag and returned nothing. To support daily and weekly tasks, I added a `due_date` to `Task`, a `next_occurrence()` method that copies the task one day or one week later, and made `mark_complete()` return that copy. I then added `Pet.complete_task()` to add the copy to the pet, and `Scheduler.complete_task()` to find which pet owns a task. That last one created a new relationship (Scheduler → Pet) that wasn't in my first diagram. I also added a `conflicts` list and methods for sorting by time, filtering, and detecting conflicts, and I changed Owner → Pet from `1..*` to `0..*` because an owner starts with no pets in the app. I made these changes because the features needed them, and I updated the UML at the end so it shows the system I actually built.

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

My scheduler considers four things:
- **Available time:** the owner's minutes for the day are a hard limit; the plan never goes over.
- **Priority:** high, medium, or low, which decides the order tasks are considered in.
- **Due date and completion:** completed tasks and tasks not due until a later day are left out, so tomorrow's copy of a daily task doesn't show up today.
- **Preferred time:** used to put the plan in clock order and to detect conflicts, but not to decide which tasks get chosen.

I decided time and priority mattered most because those are what a busy owner actually struggles with: there isn't enough time for everything, so the important things (feeding, medication) have to come first. Duration only breaks ties, because when two tasks are equally important, fitting the shorter one first leaves more room for others. I didn't use the owner's `preferences` yet. It's in the `Owner` class, but I couldn't define a clear rule for it, and I'd rather leave it unused than add a rule I couldn't explain or test.

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

My scheduler picks tasks greedily: it sorts them by priority (shorter tasks first on ties) and adds each one if it still fits in the owner's remaining time. It never goes back to try a different combination. This means it doesn't always use the available time as fully as possible. In my `main.py` demo with a 60-minute budget, it chose Feeding (10 min), Morning walk (30 min), and Brushing (15 min) for 55 minutes, then skipped the Evening walk, Playtime, and Fetch because only 5 minutes were left. A search over every combination (like a knapsack algorithm) could sometimes fill the time more completely, for example by swapping one longer medium task for two shorter low-priority ones.

I think this tradeoff is reasonable for a pet owner. A higher-priority task should never get bumped just so the minutes add up more neatly. Feeding and medication matter more than playtime, even if that leaves a few minutes unused. The greedy approach is also easy to explain: every skipped task gets a clear reason like "needs 20 min but only 5 min left", which an owner can understand and act on. An optimal search would be harder to explain and slower as the task list grows, and a typical owner only has a handful of tasks a day, so the extra efficiency wouldn't be worth the added complexity.

---

## 3. AI Collaboration

**a. How you used AI**

- How did you use AI tools during this project (for example: design brainstorming, debugging, refactoring)?
- What kinds of prompts or questions were most helpful?

I used Claude Code as a coding assistant throughout the project. I used it to check that my UML had the four classes I needed, to turn the UML into Python class stubs, to review that skeleton before writing logic, to implement the methods, to write a `main.py` demo and a pytest suite, and to commit and push my work to GitHub.

The most helpful prompts were specific and gave the AI a clear job. Asking it to review the skeleton for "missing relationships or potential logic bottlenecks" got much more useful feedback than asking whether the code looked fine. Pasting the assignment's exact requirements (for example, "Task: description, time, frequency, completion status" and "the Scheduler must read from the Owner method") kept the code aligned with what the project asks for.

**b. Judgment and verification**

- Describe one moment where you did not accept an AI suggestion as-is.
- How did you evaluate or verify what the AI suggested?

When the AI reviewed my skeleton, it listed nine possible problems. I didn't take all of them. I accepted the three that mattered most right away:
- **Priority sorting:** sorting priority strings would be alphabetical, putting "high" before "low" before "medium", so I added a numeric `PRIORITY_RANK`.
- **Pet link:** tasks didn't know which pet they belonged to, so I added `pet_name`.
- **Skipped tasks:** the scheduler couldn't explain skipped tasks, so I added a `skipped` list with reasons.

I held off on others, like adding start times to the plan and using the owner's `preferences`. Those depend on design decisions I hadn't made yet, and adding them early would have made the code more complicated than the project needed at that point.

I also changed things the AI first produced when they didn't match the assignment. The first `Task` class followed my UML, with `title` and `category` fields. The assignment asked for description, time, frequency, and completion status, so I had it changed to match, and I updated the UML too. The first version of `main.py` only gave two tasks a time, and the assignment required at least three tasks with different times, so I had that fixed as well.

To verify the results, I:
- ran `python main.py` and checked that the schedule made sense: high-priority tasks first, the total within 60 minutes, and the completed task and the task that didn't fit both listed as skipped
- ran `pytest` after each change; all 16 tests pass, including tests for the priority-order bug and for the scheduler pulling tasks from both pets
- checked GitHub after each push to confirm the commit was actually there

**c. AI strategy**

*Which AI coding assistant features were most effective for building your scheduler?*

The most effective feature was that the assistant could read my actual code and run it, instead of answering in general terms. When I asked what edge cases to test, it read `pawpal_system.py` first and found specific problems in my code, like `"8:00"` sorting after `"10:00"` because times were compared as text. It then wrote the tests and ran `pytest` to show the results (56 passed, 5 expected failures) instead of just telling me they would work. Running things was useful in other places too: it ran `python main.py` to get real output for my README, used Streamlit's test runner to check that the app's buttons and warnings worked, and checked that my local files matched GitHub before and after pushing. Being able to edit several files in one step (tests, README, `app.py`, and the UML) also saved time, as long as I reviewed each change.

*Give one example of an AI suggestion you rejected or modified to keep your system design clean.*

When the assistant found five bugs in edge cases (times without a leading zero, minutes like `"08:75"`, overdue recurring tasks, tasks running past midnight, and removing duplicate tasks), the quick option would have been to patch all five in `pawpal_system.py` right away. I didn't do that. Instead, I had each one written as a test marked `xfail(strict=True)`, so the suite documents the gap and will tell me when it's fixed, and I kept the scheduler code unchanged. Some of these aren't simple bugs but design decisions. For example, when an overdue daily task is completed, should the next one be due the day after it was completed, or one day after the date it was originally due? Patching it quickly would have meant the AI made that choice for me. Keeping the decision with me kept the design deliberate, and the README now lists these as known limitations instead of hiding them.

*How did using separate chat sessions for different phases help you stay organized?*

I used separate sessions for different phases of the project: one for designing the UML and building the core classes, and another for testing, connecting the Streamlit UI, and writing documentation. Starting a new session for a new phase meant the assistant was focused on that phase's job without a long history of earlier decisions to sort through. Each phase also ended with something concrete that the next one could start from: committed code on GitHub, a passing test suite, an updated UML. That made it easy to check that each phase was really finished. One thing I had to manage was that the sessions didn't share everything automatically. For example, my working folder isn't the git repo, so changes had to be copied into my GitHub clone before pushing, and that had to be carried over between sessions.

*Summarize what you learned about being the "lead architect" when collaborating with powerful AI tools.*

Being the lead architect meant I owned the decisions, and the AI did the work quickly once a decision was made. The AI was good at generating code, finding edge cases, and writing documentation, but it would also happily build in whatever direction I pointed it, so the direction had to come from me. In practice, that meant three things: giving it specific jobs with clear requirements (like pasting the assignment's exact wording), checking its output against my design and the assignment instead of assuming it was right, and deciding what *not* to build yet, like the owner `preferences` or the fixes for design-level edge cases. My UML became the reference point. When the code and diagram disagreed, I had to decide which one was right, and at the end I updated the diagram to match what I had deliberately built.

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

My test suite has 61 tests in `tests/test_pawpal.py`. They cover:
- **Sorting:** tasks come back in chronological order, untimed tasks go last, earlier dates come first, and priority sorts high → medium → low instead of alphabetically.
- **Recurrence:** completing a daily task creates a new task for the next day, weekly tasks recur 7 days later, "once" tasks don't recur, completing a task twice creates only one copy, and due dates roll over months, years, and leap days.
- **Conflict detection:** exact same-time tasks and overlapping tasks are flagged, for the same pet or different pets, while back-to-back tasks are not, and a malformed time gives a warning instead of crashing.
- **Planning:** the plan stays within the time budget, including a task that exactly fills it; overdue tasks are included; the planner keeps going after a task that doesn't fit; and every skipped task has a reason.
- **Validation and filtering:** invalid durations, priorities, and frequencies are rejected, and filters work by pet, by status, or both.

These tests matter because the scheduler's mistakes would be quiet ones. A wrong sort order or a duplicated recurring task doesn't crash anything, it just gives the owner a plan that looks fine but isn't. Some tests cover problems found during the project, like priority sorting alphabetically and completing a task twice creating two copies of its next occurrence, so they make sure those bugs can't come back.

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

I'd rate my confidence 4 out of 5. All 56 tests of current behavior pass, including edge cases like exact-fit time budgets and double completion. I held back one point because five tests are marked as expected failures: they describe real gaps I found but haven't fixed yet.

Next, I would:
- Fix and test the five known gaps: times without a leading zero (`"8:00"`), out-of-range minutes (`"08:75"`), completing an overdue recurring task, tasks running past midnight, and removing one of two identical tasks.
- Add automated tests for the Streamlit app, like adding a pet, completing a task, and generating a schedule, since the UI is currently only checked by running it.
- Test two pets with the same name, since tasks are linked to pets by name and the filter would merge them.

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

I'm most satisfied with how explainable the scheduler is. Every task that's left out of the plan has a plain reason, like "needs 20 min but only 5 min left" or "not due until 2026-10-19", and conflicts show up as warnings instead of errors, so the owner always gets a plan and knows what to fix. I'm also happy with keeping the logic separate from the UI: all the scheduling rules live in `pawpal_system.py`, and `app.py` only collects input and displays what the `Scheduler` returns. That made the logic easy to test without a browser, and it let me improve the display at the end without touching the scheduler.

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

- **Validate times when a task is created.** Right now, `Task` checks duration, priority, and frequency, but not the time format, which is the root cause of two of my known gaps. Checking it in one place would be cleaner than handling bad times later.
- **Link tasks to pets by object, not by name.** Two pets with the same name are currently treated as one.
- **Decide how overdue recurring tasks should behave** and make the code match.
- **Use the owner's preferences**, for example preferred walk times or tasks to always include.
- **Save data between sessions.** The app forgets everything when the page is refreshed.

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?

Designing first made working with AI much better. Because I had a UML diagram and clear class responsibilities before writing logic, I could give the AI specific jobs and check its output against something concrete. When it suggested a change, I could ask whether it fit the design instead of just whether it worked. The AI made building fast, but the design decided whether the result stayed clean.
