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

---

## 2. Scheduling Logic and Tradeoffs

**a. Constraints and priorities**

- What constraints does your scheduler consider (for example: time, priority, preferences)?
- How did you decide which constraints mattered most?

**b. Tradeoffs**

- Describe one tradeoff your scheduler makes.
- Why is that tradeoff reasonable for this scenario?

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

---

## 4. Testing and Verification

**a. What you tested**

- What behaviors did you test?
- Why were these tests important?

**b. Confidence**

- How confident are you that your scheduler works correctly?
- What edge cases would you test next if you had more time?

---

## 5. Reflection

**a. What went well**

- What part of this project are you most satisfied with?

**b. What you would improve**

- If you had another iteration, what would you improve or redesign?

**c. Key takeaway**

- What is one important thing you learned about designing systems or working with AI on this project?
