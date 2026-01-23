# V2 Summarizer - Revised Prompts for BJJ System Documentation

## TASK: Document a BJJ system/class for teaching purposes

Each prompt has a specific teaching goal. Output should be concise (1 sentence per line), 
properly formatted for Logseq, and organized as a clear progression from entry to primary 
to reactions.

---

## PROMPT 1: Extract Techniques Demonstrated

**YOUR TASK:** Generate a list of techniques demonstrated in this class to provide a 
quick reference for what students will learn.

**PURPOSE:** Help instructors and students understand the scope of techniques covered in 
this session. This is a teaching overview, not exhaustive documentation.

**FORMAT:** Bullet list, one technique per line, with 1-sentence description max

**POSITIVE EXAMPLE:**
```
- Half Butterfly Guard
  - A guard position using inside leg positioning for control and leg lock setups
- Single Leg X-Guard
  - A leg entanglement position for sweeps and leg lock attacks
- Choi Bar
  - An upper body attack targeting the arm when opponent cross-faces
```

**NEGATIVE EXAMPLE:**
```
❌ Half Butterfly Guard: This is a guard position that uses inside leg positioning 
and is very effective for setting up leg locks. It works in both gi and nogi, and 
has become increasingly popular in recent years because of how many leg lock options 
it provides. The position involves...
```

---

## PROMPT 2: Extract Key Positions

**YOUR TASK:** Extract the major positional waypoints students will reach during this 
lesson, so they can recognize when they've achieved each milestone.

**PURPOSE:** Create a positional roadmap for students. Each position should be 
recognizable and specific to this system.

**FORMAT:** Bullet list, position name with one-sentence description of how to 
recognize it

**POSITIVE EXAMPLE:**
```
- Knee Shield
  - Your knee is across opponent's body, blocking their advance
- Half Butterfly Guard
  - One hook deep near opponent's hip, other leg creating space
- Single Leg X-Guard
  - Your shin is diagonal across opponent's leg, knee deep
- Saddle Position
  - Both legs entangled around one opponent's leg, hips underneath
```

**NEGATIVE EXAMPLE:**
```
❌ In the knee shield, your knee extends across your opponent's torso in a 
particular way. This position is defensive but can also lead to offensive 
opportunities. The knee shield is used as an intermediary position...
```

---

## PROMPT 3: Extract Entry to Position (Knee Shield → Half Butterfly)

**YOUR TASK:** Generate step-by-step instructions for entering the half butterfly guard 
from knee shield position, so a student can follow the progression clearly.

**PURPOSE:** This is the entry drill. Students start in knee shield and learn to 
transition into half butterfly. Make it teachable.

**FORMAT:** 
- Numbered steps (3-4 max)
- One sentence per step
- Each step should be a single action/concept

**POSITIVE EXAMPLE:**
```
1. Establish knee shield with bottom hook on opponent's shin
2. Control opponent's shoulder with arm drag grip, pulling tight
3. Transition butterfly hook close to opponent's hip as they posture up
```

**NEGATIVE EXAMPLE:**
```
❌ 1. Get your knee shield going and maintain control of the opponent's upper body
   2. As the opponent starts to move, you're going to want to shift your leg position
   3. Work your hook in as they respond to your pressure
```

---

## PROMPT 4: Extract Primary Sequence (Single Leg X Entry)

**YOUR TASK:** Generate the step-by-step primary attack sequence from half butterfly 
to single leg X-guard, so instructors can teach the main technique clearly.

**PURPOSE:** The primary sequence is the main technique students should practice first. 
It's the "bread and butter" of this system.

**FORMAT:**
- Numbered steps (4-5 max)
- One sentence per step
- Include what happens at each stage
- Include what to feel/look for (verification point)

**POSITIVE EXAMPLE:**
```
1. From half butterfly, secure arm drag grip on wrist and shoulder
2. Shoot your knee deep behind opponent's hips to bump their weight forward
3. Fall flat on your back while maintaining shoulder control
4. Step on opponent's hip and knock them off balance to one side
5. Achieve single leg X with your shin across their leg
```

**NEGATIVE EXAMPLE:**
```
❌ 1. Make sure you have good upper body control in place
   2. Your leg is going to move in a particular way that creates pressure
   3. The opponent's weight will shift based on how you execute this
   4. You should end up in a good position from here
```

---

## PROMPT 5: Extract Reactions (Follow-up Techniques)

**YOUR TASK:** Extract the 2 main opponent reactions and the counter-technique for each, 
so students know how to adapt when the primary doesn't work.

**PURPOSE:** Teach the decision tree: "If they do this, do that." This mirrors how 
real rolling works.

**FORMAT:**
For each reaction (numbered, max 2):
- **When to use:** One sentence describing the opponent's action that triggers this
- **Steps:** 3-4 numbered steps, one sentence each

**POSITIVE EXAMPLE:**
```
### Reaction 1: Choi Bar (Cross Face Defense)
**When to use:** Opponent attempts to cross face your head
- Sit up and reach for their head to create space
- Isolate their arm by controlling shoulder and wrist
- Pull their shoulder tight to your chest and fall back
- Flatten hips to secure the arm bar finish

### Reaction 2: Saddle Entry (Heavy Weight)
**When to use:** Opponent puts weight heavily on their opposite leg
- Control upper body to force their weight away from that leg
- Pull your bottom leg out, hips up behind their thigh
- Lock your feet together and push their hips to mat
```

**NEGATIVE EXAMPLE:**
```
❌ ### Follow-up Option 1
**Trigger:** When the opponent reacts defensively
- You might want to consider attacking their arm
- There's an arm bar type technique available here
- Execute it based on how they're positioned

### Follow-up Option 2
**Trigger:** If they resist the primary attack
- Try to get to their legs instead
- This position offers several submission options
```

---

## PROMPT 6: Extract Core Concepts

**YOUR TASK:** Extract teaching principles, key insights, and common mistakes so 
instructors can emphasize what matters and prevent bad habits.

**PURPOSE:** Help students understand the "why" behind the techniques, not just the "how."

**FORMAT:**
Three subsections, bullet list, one sentence per item (max 5 per section)

**POSITIVE EXAMPLE:**
```
**Principles Taught**
- Control upper body to manage opponent's balance and reactions
- Use knee shield to create distance before committing to butterfly hook
- Keep foot deep near hip for leg entanglements, wide for sweeps
- Maintain opponent's head in line with your body for mobility

**Key Insights**
- Knee shield is the entry; don't rush to butterfly hook
- Primary sequence sets up all follow-up reactions
- Opponent's weight distribution determines which reaction to use
- Small adjustments in hip positioning create major control differences

**Common Mistakes to Avoid**
- Placing butterfly hook too wide or too loose early on
- Using butterfly hook before establishing upper body control
- Staying on your side instead of falling flat during primary sequence
- Trying to sweep instead of attacking the legs
```

**NEGATIVE EXAMPLE:**
```
❌ **Principles Taught**
- There are many important concepts in the half butterfly system
- You need to understand positioning and control
- Weight distribution and balance matter
- The techniques work well when executed properly

**Key Insights**
- Practice makes perfect
- Drill these techniques regularly
- Work with different partners
- Build your understanding over time
```

---

## PROMPT 7: Extract Drills (Progressive Teaching Sequence)

**YOUR TASK:** Generate 3-4 progressive drills that build on each other, so students 
can practice incrementally from basic entry to complex reactions.

**PURPOSE:** Create a class structure: drill entry, drill primary, then drill reactions. 
Each drill should stand alone but build toward the system.

**FORMAT:**
For each drill:
- **Starting position:** Where the drill begins
- **Goal:** What position/technique students are learning
- **Steps:** 3-4 numbered steps, one sentence each, including opponent reaction

**POSITIVE EXAMPLE:**
```
### Drill 1: Knee Shield to Half Butterfly Entry
**Starting position:** Knee shield guard
**Goal:** Transition into half butterfly guard
**Steps:**
1. Establish knee shield with bottom hook on opponent's shin
2. Control opponent's shoulder with arm drag grip
3. Transition butterfly hook close to hip as opponent postures up

### Drill 2: Half Butterfly to Single Leg X
**Starting position:** Half butterfly guard
**Goal:** Execute primary sequence to single leg X
**Steps:**
1. Secure arm drag grip with shoulder control
2. Shoot knee deep behind hips, bump weight forward
3. Fall flat on back, maintain control, step on hip
4. Achieve single leg X and feel opponent's weight shift

### Drill 3: Reacting to Cross Face with Choi Bar
**Starting position:** Half butterfly guard (opponent attempts cross face)
**Goal:** Counter with Choi Bar
**Steps:**
1. As opponent reaches to cross face, sit up and control head
2. Isolate their arm by pushing shoulder and wrist control
3. Fall back and flatten hips to secure arm bar
```

**NEGATIVE EXAMPLE:**
```
❌ ### Drill 1: Guard Transitions
**Goal:** Practice moving between positions
**Steps:**
1. Start from your current position
2. Work on transitioning to another position
3. Practice the technique

### Drill 2: Leg Attacks
**Goal:** Learn leg attack options
**Steps:**
1. Get to a good leg attack position
2. Attack the leg
3. Finish the submission
```

---

## PROMPT 8: Synthesize Overview (Written LAST)

**YOUR TASK:** Create a brief teaching overview that ties together entry → primary → 
reactions, so students understand the complete system flow.

**PURPOSE:** Opening remarks for class. Should answer: "What are we learning and why?"

**FORMAT:**
- **Primary Entry:** 1-2 sentences about entry point
- **Main Technique:** 1-2 sentences about primary sequence
- **Reaction Framework:** 1-2 sentences about how reactions work

**POSITIVE EXAMPLE:**
```
**Primary Entry**
Today we're learning the half butterfly system starting from knee shield position. 
The knee shield allows us to control distance while setting up for more aggressive attacks.

**Main Technique**
The primary attack is the single leg X-guard entry, which uses weight distribution 
and upper body control to put the opponent off-balance.

**Reaction Framework**
When the opponent reacts, you have two main options: Choi Bar for cross face attempts, 
or Saddle entry when they put heavy weight on their opposite leg.
```

**NEGATIVE EXAMPLE:**
```
❌ **Overview**
Today we're going to cover several different techniques and concepts related to 
the half butterfly position. These techniques are useful in many different situations 
and can be applied in various ways depending on your opponent's reactions.
```

---

