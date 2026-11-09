# Sensitivity vs Specificity

## The basics

Every test has **both** rates, and each is calculated from a **different group** of people.

| Rate            | Looks at…                  | Question it answers                       |
|-----------------|----------------------------|-------------------------------------------|
| **Sensitivity** | only people who are **sick**    | How many sick people does the test catch?   |
| **Specificity** | only people who are **healthy** | How many healthy people does the test clear? |

- High sensitivity → few sick people are **missed**
- High specificity → few healthy people are **wrongly flagged**

> **Smoke alarm example:** an alarm that goes off at the slightest smoke never misses a fire
> (high sensitivity), but it also goes off from toast (low specificity).

---

## How they are measured

1. Take a group of people.
2. Use a **gold standard** (the most reliable method, e.g. a biopsy or a lab PCR) to find out who is really sick.
3. Run the **new test** on everyone too.
4. Compare the two results.

**Example:** 100 people take the test. The gold standard says 20 are sick and 80 are healthy.

- Of the 20 sick, the test flags 18 → **sensitivity = 18 / 20 = 90%**
- Of the 80 healthy, the test clears 76 → **specificity = 76 / 80 = 95%**

The results are only as good as the gold standard. If it makes mistakes, these numbers will be off too.

---

## The threshold (cutoff)

Many tests give a **number** (blood sugar, a protein level, a score). The **threshold** turns that number into a result:

- at or above the cutoff → **positive**
- below the cutoff → **negative**

The sick and healthy groups usually **overlap**:

```
Healthy:   ████████████
Sick:              ████████████
                ↑ overlap ↑
```

| Cutoff    | Sensitivity | Specificity | Effect                              |
|-----------|-------------|-------------|-------------------------------------|
| **Lower** | ↑ goes up   | ↓ goes down | Catches more sick people, more false alarms |
| **Higher**| ↓ goes down | ↑ goes up   | Fewer false alarms, misses more sick people |

So sensitivity and specificity are always stated **at a given cutoff**. Moving the cutoff only changes which mistake happens more often.

---

## Which one matters more?

- **Screening** (e.g. cancer, HIV): you don't want to miss anyone → favour **high sensitivity**.
- **Confirming** (e.g. before surgery or chemotherapy): you don't want false alarms → favour **high specificity**.

Memory aids:

- **SnNout:** a highly **S**e**n**sitive test with a **N**egative result rules the condition **out**.
- **SpPin:** a highly **Sp**ecific test with a **P**ositive result rules the condition **in**.

---

## Quick summary

- **Sensitivity:** of the sick, how many the test catches.
- **Specificity:** of the healthy, how many the test clears.
- **Measured** by comparing the test against a gold standard.
- **Threshold:** the cutoff that turns a number into positive or negative. Moving it trades one mistake for the other.
