# Assignment 3: The Workplace Becomes the App

HR needs daily attendance for 1,000 people at 100 locations. Employees do not have smartphones. There is no attendance app to install.

**The workplace becomes the app.** We do not put a new device in every employee’s pocket. We put a small attendance terminal at each workplace. The employee taps a company RFID/NFC badge. If the badge is missing, they use a PIN. Where the company has approved it, they can use a biometric check.

The LLM is not the source of truth. The attendance system is the source of truth. The LLM does not decide whether someone is present. It helps people talk to the system and understand the data.

This document is a design. It describes how the system would work. It is not a claim that it has been built or rolled out.

---

## The big idea

```
   Employee
      │  no smartphone needed
      ▼
┌──────────────────────┐
│ Attendance Terminal   │  ← lives at the workplace
└──────────┬────────────┘
           │ verifies identity
           ▼
┌──────────────────────┐
│ Attendance System     │  ← source of truth
└──────────┬────────────┘
           │
     ┌─────┴──────┐
     ▼             ▼
 HR Dashboard   LLM Assistant
```

The terminal takes the place of the phone. The employee never opens an app. Identity is checked at the terminal. Attendance is stored only in the attendance system. The HR dashboard and the LLM assistant look at those records. They do not invent who showed up.

---

## What happens when an employee arrives

```
Employee arrives
      │
      ▼
Taps company badge
      │
      ▼
System identifies employee
      │
      ▼
Checks:
 • Is the badge valid?
 • Is this location allowed for them?
 • Already checked in today?
      │
      ▼
Record attendance → "Check-in successful"
```

Rahul works at Location 27. He arrives at 9:05 AM and taps his badge. The system sees an active employee, allowed at that site, who has not already checked in. It stores a check-in and the screen says it worked. If he were 5 minutes past the start of his shift, the record can also mark him late. That is a normal check-in. Checkout later in the day is the same idea, stored as a check-out.

If Rahul taps again at 9:06 without checking out, that is a duplicate check-in. The system does not write a second “present.” It tells him he is already checked in. HR can still fix a genuine mistake later by adding a correction, not by erasing the first event.

---

## Where the LLM helps

```
                ┌────────────────┐
                │  LLM Assistant  │
                └────────┬────────┘
        ┌────────────────┼────────────────┐
        ▼                 ▼                ▼
  Employee help      HR questions      Exceptions
        │                 │                │
        └────────────────┼────────────────┘
                          ▼
                ┌──────────────────┐
                │ Attendance System │
                └──────────────────┘
```

The assistant sits on top of the attendance system. Badge check-in still works if the assistant is down. Voice is only a way to talk. It is not proof of who someone is. A copied voice should not mark Rahul present.

**Forgot badge.** Employee: “I forgot my badge.” The assistant starts the backup path. The person enters employee ID and PIN (or a biometric, if that site uses it). If that check passes, attendance is stored as PIN or biometric, not as a badge tap.

**Visiting another office.** Employee: “I work in Mumbai, but I am at this site today.” The assistant treats this as a visit request. The attendance system checks whether that visit is allowed. If yes, check-in is stored at the visit location. If not, it goes to HR as an exception the same day.

**Who is absent.** HR: “Who has not checked in yet?” The assistant turns that into a lookup for today. The attendance system returns the list from real records. The assistant only reads those names. It never guesses.

---

## One hundred locations

```
                ┌─────────────────┐
                │  Central System │
                └────────┬─────────┘
       ┌───────────────────┼───────────────────┐
       ▼                    ▼                    ▼
  Location 1            Location 2          Location 100
       │                    │                    │
   Terminal              Terminal             Terminal
       │                    │                    │
  ~10 employees        ~10 employees        ~10 employees
```

1,000 employees and 100 sites is about 10 people per location. One terminal is enough at a small site. A busy entrance can have a second reader. Both still belong to the same location. We do not need a large computer room at every office. One HQ might have 200 people and a shop might have 3. The design still works if sites are uneven.

---

## When the internet is down (a network problem)

This is about the wire, not about who the person is. The badge check already succeeded. The terminal just cannot reach HQ for a while.

```
Normal day:
  Check-in ──────────────► Central System

Internet drops:
  Check-in ──► Saved on terminal ──► Employee still confirmed
                                              │
                                    (connection returns)
                                              ▼
                                   Synced to Central System
```

At Location 27 the internet fails from 9:00 to 9:20. Rahul still taps his badge at 9:05. The terminal saves a signed event on the device, gives him confirmation, and later sends that event when the link is back. Each event has its own ID, so the same punch is stored once, not twice. The screen can say “saved here” until HQ has it, so a short delay on the HR screen is expected.

---

## When identity cannot be proven (an exception)

Diagram 5 was a broken connection. This is a broken identity check: we do not yet know it is the right person, or they have no badge in hand.

```
"I forgot my badge"
         │
         ▼
Ask for PIN or biometric backup
         │
    ┌────┴─────┐
    ▼           ▼
Verified     Not verified
    │           │
    ▼           ▼
Record       Flag sent to HR
attendance   for same-day review
                 │
                 ▼
         HR confirms or corrects
         the entry manually
```

The system does not fire or mark someone absent forever because an automatic check failed. A failed check becomes a same-day flag for a person. HR confirms or corrects the entry. That closes the loop. HR has the last word.

**Attendance dispute.** Rahul: “I was here yesterday. The system shows absent.” HR opens his event history, not only a Present/Absent cell. If the terminal was broken, or a punch was missed, HR adds a correction event that points at the original record. The old line stays. The new line explains the fix. Pay and warnings stay a human decision.

If the **terminal hardware** itself dies, that is not an internet outage. People use a nearby working terminal, or PIN at a backup reader, or the same HR exception path for that morning. IT replaces the box and enrolls it again as that location’s device.

---

## How the pieces fit

```
                           HR
                           │
                     HR Dashboard
                           │
                     LLM Assistant
                           │
                    Central Backend
                           │
                  Attendance Database
                           │
        ┌──────────────────┼──────────────────┐
        ▼                   ▼                   ▼
   Location 1           Location 2          Location 100
        │                   │                   │
    Terminal             Terminal            Terminal
        │                   │                   │
   Employees            Employees           Employees
```

HR is the user. The dashboard and the LLM are how HR (and, at the terminal, employees) see and ask about data. The backend and database are where truth lives. Terminals are where truth is created, when a badge, PIN, or approved biometric succeeds.

HR can filter by person, site, date, team, and status: present, late, absent, still syncing, or open exception. “Give me today’s summary” must come from those counts. If the lookup fails, the assistant says it cannot answer.

---

## Design details

**Attendance records.** Each check-in stores an event ID, employee, location, terminal, time, type (check-in or check-out), how identity was proven, and whether it started offline. Example: Rahul, Location 27, terminal A, 9:05, check-in, badge.

**Event history.** Instead of only storing “Rahul is Present”, the system logs events like check-in, check-out, visit, exception, and correction. That gives HR a history to investigate, not just a snapshot. Today’s Present / Late / Absent list is built from those events.

**Security.** Badges map to an employee ID. PINs are stored as hashes, not plain numbers, and retries are limited. Each terminal has its own device key so a random laptop cannot post check-ins for Location 27. Only HR and auditors see other people’s records. An employee can see their own.

**Privacy.** We store who, where, when, and the method. We do not keep the room’s microphone on all day. If a site uses biometrics, keep only what policy allows (often a template, not a raw photo), for a set time, then delete. Presence tracking should not become watching people all day.

**Fraud detection.** The system cannot stop every shared badge. It can flag patterns for review, not auto-punish. Example: the same badge checks in at Location 12 at 9:01 and Location 87 at 9:20, far apart. That is impossible travel. HR looks at it. It might be a clone, a clock error, or a data bug.

**Offline operation.** See the internet-down flow above. Signed events wait on the terminal and sync by event ID when the network returns.

**Scaling.** About 2,000 events a day if everyone checks in and out. A normal database handles that. If the company grows to 1,000 locations, we add terminals and keep one central attendance system. We do not need a new product shape for each site.

**Failure handling.** Network loss is covered above. If a terminal breaks, use another reader at that site or a neighbour site, plus the HR path for that morning. If the database is down, online punches wait on the terminal queue. They must not be thrown away.

**Data retention.** Keep daily event history for the period HR and law need (for example 12–24 months), then delete or archive under policy. Biometric templates, if used, are deleted sooner and when someone leaves. The employee or HR can request a correction. The fix is a new event, not a silent edit.

**Trade-offs.** One hundred terminals cost money and they break. A new joiner on day one may not have a badge yet and will use PIN or HR. Field staff who never enter a site still need a separate rule, because this design is for a workplace door, not a phone in a bag.

A first prototype can fake 100 locations on a laptop, with the same records and the same rules. That is how we would learn, not a claim that 100 boxes already exist.

---

## Close

If employees do not have smartphones, do not try to rebuild a smartphone app in another shape. Move the system to the workplace itself.

The workplace provides the terminal. The attendance system keeps the actual records. The LLM helps employees and HR interact with those records.

This gives HR a simple way to manage attendance across 1,000 employees and 100 locations without needing employees to own smartphones.
