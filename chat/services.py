from __future__ import annotations
from dataclasses import dataclass
from datetime import datetime, timedelta
import re
import random
from typing import Optional
from django.utils.timezone import get_current_timezone, make_aware, now, is_naive

from tasks.models import Task
from notes.models import Note
from reminders.models import Reminder
from events.models import Event
from .ml import IntentRouter

# --- lightweight natural date parser (similar to your CLI) ---
_TIME24 = r"(?P<h>\d{1,2}):(?P<m>\d{2})(?::(?P<s>\d{2}))?"
_TIME12 = r"(?P<h>\d{1,2})(?::(?P<m>\d{2}))?\s?(?P<ampm>am|pm)"
_DATE = r"(?P<y>\d{4})-(?P<mo>\d{2})-(?P<d>\d{2})"
_TIME24_SIMPLE = r"\d{1,2}:\d{2}(?::\d{2})?"
_TIME12_SIMPLE = r"\d{1,2}(?::\d{2})?\s?(?:am|pm)"

def _parse_time_into(base: datetime, token: str) -> datetime:
    token = token.strip().lower()
    m = re.match(_TIME24 + r"$", token)
    if m:
        hh = int(m.group("h")); mm = int(m.group("m")); ss = int(m.group("s")) if m.group("s") else 0
        return base.replace(hour=hh, minute=mm, second=ss, microsecond=0)
    m = re.match(_TIME12 + r"$", token)
    if m:
        hh = int(m.group("h")); mm = int(m.group("m")) if m.group("m") else 0
        if hh == 12: hh = 0
        if m.group("ampm") == "pm": hh += 12
        return base.replace(hour=hh, minute=mm, second=0, microsecond=0)
    return base

def parse_datetime(text: str, base: Optional[datetime] = None) -> tuple[Optional[datetime], str]:
    tz = get_current_timezone()
    base = base or now()
    s = text.strip().lower()
    def _aware(dt: datetime) -> datetime:
        return make_aware(dt, tz) if is_naive(dt) else dt

    m = re.search(r"\bin\s+(?P<n>\d+)\s+(?P<u>seconds?|minutes?|hours?|days?|weeks?)\b", s)
    if m:
        n = int(m.group("n")); u = m.group("u")
        delta = dict(second=timedelta(seconds=n), seconds=timedelta(seconds=n),
                     minute=timedelta(minutes=n), minutes=timedelta(minutes=n),
                     hour=timedelta(hours=n), hours=timedelta(hours=n),
                     day=timedelta(days=n), days=timedelta(days=n),
                     week=timedelta(weeks=n), weeks=timedelta(weeks=n))[u]
        when = base + delta
        remainder = (s[: m.start()] + s[m.end():]).strip()
        return _aware(when), remainder

    m = re.search(r"\btomorrow(?:\s+at\s+(?P<t>" + _TIME24_SIMPLE + r"|" + _TIME12_SIMPLE + r"))?\b", s)
    if m:
        base2 = base + timedelta(days=1)
        base2 = base2.replace(hour=9, minute=0, second=0, microsecond=0)
        t = m.group("t")
        when = _parse_time_into(base2, t) if t else base2
        remainder = (s[: m.start()] + s[m.end():]).strip()
        return _aware(when), remainder

    m = re.search(r"\btoday\s+at\s+(?P<t>" + _TIME24_SIMPLE + r"|" + _TIME12_SIMPLE + r")\b", s)
    if m:
        when = _parse_time_into(base, m.group("t"))
        if when <= base:
            when += timedelta(days=1)
        remainder = (s[: m.start()] + s[m.end():]).strip()
        return _aware(when), remainder

    m = re.search(r"\bon\s+" + _DATE + r"(?:\s+at\s+(?P<t>" + _TIME24_SIMPLE + r"|" + _TIME12_SIMPLE + r"))?\b", s)
    if m:
        y, mo, d = int(m.group("y")), int(m.group("mo")), int(m.group("d"))
        base2 = base.replace(year=y, month=mo, day=d, hour=9, minute=0, second=0, microsecond=0)
        t = m.group("t")
        when = _parse_time_into(base2, t) if t else base2
        remainder = (s[: m.start()] + s[m.end():]).strip()
        return _aware(when), remainder

    m = re.search(_DATE + r"(?:\s+" + _TIME24_SIMPLE + r")?", s)
    if m:
        y, mo, d = int(m.group("y")), int(m.group("mo")), int(m.group("d"))
        base2 = base.replace(year=y, month=mo, day=d, hour=9, minute=0, second=0, microsecond=0)
        when = base2
        mm = re.match(r"^\s+(" + _TIME24_SIMPLE + r"|" + _TIME12_SIMPLE + r")\b", s[m.end():])
        if mm:
            when = _parse_time_into(when, mm.group(1))
        remainder = (s[: m.start()] + s[m.end():]).strip()
        return _aware(when), remainder

    return None, s

# --- main assistant orchestration ---
@dataclass
class AssistResult:
    reply: str

class Assistant:
    def __init__(self) -> None:
        self.router = IntentRouter()
        self.router.train()  # train once at import; could add admin button to retrain

    def handle(self, user_text: str) -> AssistResult:
        label, conf = self.router.predict(user_text)
        if not label or conf < self.router.threshold:
            # simple rule fallback
            s = user_text.lower()
            if s.startswith("help") or s.strip() in ("help", "/help", "commands", "examples", "how to use"):
                return self._handle_help()
            if re.search(r"\b(hi|hello|hey|yo|good\s+(morning|afternoon|evening))\b", s) or "how are you" in s or "thank" in s:
                return self._handle_smalltalk(user_text)
            if s.startswith("add task") or "task" in s:
                return self._handle_tasks(user_text)
            if s.startswith("remind me") or "reminder" in s:
                return self._handle_reminders2(user_text)
            if s.startswith("note ") or s.startswith("search notes") or "note" in s:
                return self._handle_notes(user_text)
            if s.startswith("add event") or "event" in s:
                return self._handle_events(user_text)
            if "about me" in s or "who am i" in s or "profile" in s:
                return self._handle_profile(user_text)
            if "projects" in s or "project" in s:
                return self._handle_projects(user_text)
            if "time" in s or "date" in s:
                return AssistResult(reply=now().strftime("It is %Y-%m-%d %H:%M:%S %Z"))
            return AssistResult(reply="I didn't catch that. Try 'help'.")
        # dispatch by label
        if label == "help":
            return self._handle_help()
        if label == "tasks":
            return self._handle_tasks(user_text)
        if label == "reminders":
            return self._handle_reminders2(user_text)
        if label == "notes":
            return self._handle_notes(user_text)
        if label == "events":
            return self._handle_events(user_text)
        if label == "profile":
            return self._handle_profile(user_text)
        if label == "projects":
            return self._handle_projects(user_text)
        if label == "smalltalk":
            return self._handle_smalltalk(user_text)
        if label == "time":
            return AssistResult(reply=now().strftime("It is %Y-%m-%d %H:%M:%S %Z"))
        return AssistResult(reply="Okay.")

    # --- handlers ---
    def _handle_tasks(self, text: str) -> AssistResult:
        when, remainder = parse_datetime(text)
        title = remainder.replace("add task", "").strip() or remainder.strip() or "(untitled)"
        if title.startswith("task"):
            title = title.replace("task", "", 1).strip()
        t = Task.objects.create(title=title, due_at=when)
        extra = f" (due {when:%Y-%m-%d %H:%M})" if when else ""
        return AssistResult(reply=f"Added task #{t.id}: {t.title}{extra}")

    def _handle_notes(self, text: str) -> AssistResult:
        s = text.strip()
        if s.lower().startswith("search notes"):
            q = s[len("search notes"):].strip()
            qs = Note.objects.filter(title__icontains=q) | Note.objects.filter(content__icontains=q)
            if not qs.exists():
                return AssistResult(reply="No matches.")
            preview = "\n".join([f"[{n.id}] {n.title}" for n in qs[:10]])
            return AssistResult(reply=f"Matches:\n{preview}")
        if s.lower().startswith("note "):
            body = s[len("note "):].strip()
            if ":" in body:
                title, content = [p.strip() for p in body.split(":", 1)]
            else:
                title, content = body[:40], body
            Note.objects.create(title=title, content=content)
            return AssistResult(reply=f"Saved note: {title}")
        return AssistResult(reply="Try: 'note Title: content' or 'search notes milk'")

    def _handle_reminders(self, text: str) -> AssistResult:
        when, remainder = parse_datetime(text)
        msg = remainder.replace("remind me", "").replace("to ", "", 1).strip() or "(no message)"
        if not when:
            return AssistResult(reply="I couldn't find a time in that. Try 'in 10 minutes' or 'tomorrow at 09:00'.")
        r = Reminder.objects.create(message=msg, due_at=when)
        return AssistResult(reply=f"Reminder #{r.id} set for {when:%Y-%m-%d %H:%M:%S} - {msg}")

    # Safe replacement used by routing to avoid any encoding issues in old method
    def _handle_reminders2(self, text: str) -> AssistResult:
        when, remainder = parse_datetime(text)
        msg = remainder.replace("remind me", "").replace("to ", "", 1).strip() or "(no message)"
        if not when:
            return AssistResult(reply="I couldn't find a time in that. Try 'in 10 minutes' or 'tomorrow at 09:00'.")
        r = Reminder.objects.create(message=msg, due_at=when)
        return AssistResult(reply=f"Reminder #{r.id} set for {when:%Y-%m-%d %H:%M:%S} - {msg}")

    def _handle_events(self, text: str) -> AssistResult:
        # Expect: add event 2025-08-25 14:00 - Title [@Location]
        m = re.search(r"(?P<date>\d{4}-\d{2}-\d{2})\s+(?P<time>\d{1,2}:\d{2})\s*-\s*(?P<title>.+)", text)
        if not m:
            return AssistResult(reply="Usage: add event 2025-08-25 14:00 - Title [@Location]")
        starts_at = make_aware(datetime.fromisoformat(f"{m.group('date')} {m.group('time')}"))
        rest = m.group("title")
        if "@" in rest:
            title, location = [p.strip() for p in rest.split("@", 1)]
        else:
            title, location = rest.strip(), None
        e = Event.objects.create(title=title, starts_at=starts_at, location=location)
        loc = f" @ {location}" if location else ""
        return AssistResult(reply=f"Event #{e.id} added: {title} at {starts_at:%Y-%m-%d %H:%M}{loc}")

    # --- profile & projects ---
    def _apply_persona(self, text: str) -> str:
        try:
            from profileapp.models import Persona, Profile
            persona = Persona.objects.first()
            profile = Profile.objects.first()
        except Exception:
            persona = None
            profile = None
        if not persona:
            return text
        name = profile.display_name if (profile and getattr(profile, "display_name", None)) else (getattr(persona, "refer_to_user_as", "") or "")
        out = text
        if getattr(persona, "greeting_template", "") and name:
            try:
                out = f"{persona.greeting_template.format(name=name)}\n\n{out}"
            except Exception:
                out = f"{persona.greeting_template}\n\n{out}"
        if getattr(persona, "closing_template", ""):
            out = f"{out}\n\n{persona.closing_template}"
        return out

    def _handle_profile(self, text: str) -> AssistResult:
        try:
            from profileapp.models import Profile, QAPair
        except Exception:
            return AssistResult(reply="Profile module not installed.")
        prof = Profile.objects.first()
        if not prof:
            return AssistResult(reply="I don't have profile info yet. Add one in the admin under Profile.")
        parts = []
        parts.append((f"About {prof.display_name}: {prof.short_bio}" if prof.short_bio else f"About {prof.display_name}").strip())
        if prof.full_bio:
            parts.append(prof.full_bio)
        links = []
        if prof.website:
            links.append(f"Website: {prof.website}")
        if prof.email:
            links.append(f"Email: {prof.email}")
        if prof.location:
            links.append(f"Location: {prof.location}")
        if links:
            parts.append("\n".join(links))
        faq = QAPair.objects.first()
        if faq:
            parts.append(f"FAQ - {faq.question}: {faq.answer}")
        reply = "\n\n".join([p for p in parts if p])
        reply = self._apply_persona(reply)
        return AssistResult(reply=reply)

    def _handle_projects(self, text: str) -> AssistResult:
        try:
            from profileapp.models import Project
        except Exception:
            return AssistResult(reply="Projects module not installed.")
        qs = Project.objects.filter(is_active=True)
        if not qs.exists():
            return AssistResult(reply="No projects found yet. Add projects in the admin.")
        lines = []
        for p in qs[:10]:
            line = f"- {p.title}"
            if p.summary:
                line += f" - {p.summary}"
            if p.url:
                line += f" - {p.url}"
            lines.append(line)
        reply = "Projects:\n" + "\n".join(lines)
        reply = self._apply_persona(reply)
        return AssistResult(reply=reply)

    def _handle_help(self) -> AssistResult:
        lines = [
            "Here are examples you can ask:",
            "",
            "Tasks:",
            "- add task Buy milk tomorrow at 09:00",
            "- add task Call Alice in 2 hours",
            "",
            "Notes:",
            "- note Trip: Pack passport and charger",
            "- search notes passport",
            "",
            "Reminders:",
            "- remind me in 10 minutes to stretch",
            "- remind me tomorrow at 9 to call mom",
            "",
            "Events:",
            "- add event 2025-08-25 14:00 - Demo @HQ",
            "",
            "Time:",
            "- what time is it",
            "",
            "About you:",
            "- about me",
            "- my projects",
            "",
            "Tips:",
            "- Natural dates like 'in 15 minutes', 'today at 18:00', 'tomorrow at 9' work.",
            "- Staff can add Training Phrases in admin and POST /retrain/ to improve intent routing.",
        ]
        return AssistResult(reply="\n".join(lines))

    def _handle_smalltalk(self, text: str) -> AssistResult:
        s = text.strip()
        sl = s.lower()
        replies: list[str] = []
        try:
            from .models import SmalltalkPair
            for p in SmalltalkPair.objects.filter(is_active=True):
                matched = False
                if p.is_regex:
                    try:
                        if re.search(p.pattern, sl, re.IGNORECASE):
                            matched = True
                    except re.error:
                        matched = False
                else:
                    if p.pattern.lower() in sl:
                        matched = True
                if matched:
                    raw = p.answers.replace("\r", "\n")
                    parts = []
                    for chunk in raw.split("\n"):
                        parts.extend([c.strip() for c in chunk.split("|")])
                    parts = [a for a in parts if a]
                    replies.extend(parts)
        except Exception:
            # ignore DB errors
            pass

        if not replies:
            if re.search(r"\b(hi|hello|hey|yo)\b", sl):
                replies = [
                    "Hello!",
                    "Hi there!",
                    "Hey — how can I help?",
                    "Hello! What can I do for you today?",
                ]
            elif "how are you" in sl:
                replies = [
                    "I’m doing great — ready to help!",
                    "All good here. How can I assist?",
                    "Feeling efficient today. What’s up?",
                ]
            elif "thank" in sl:
                replies = [
                    "You’re welcome!",
                    "Anytime!",
                    "Happy to help!",
                ]
            else:
                replies = [
                    "Sounds good. How can I help further?",
                    "Got it. Want me to add a task or note?",
                    "Let me know what you’d like to do next.",
                ]

        reply = random.choice(replies)
        reply = self._apply_persona(reply)
        return AssistResult(reply=reply)
