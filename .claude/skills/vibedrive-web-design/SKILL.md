---
name: vibedrive-web-design
description: Designs and generates modern, production-ready UI for VibeDrive, a personal learning platform built on Flask + Jinja2 + Tailwind CSS + vanilla JS. Produces clean, soft-minimalist edtech-style pages and components - dashboards, skill cards, milestone trackers, progress bars, weekly plan views, lesson readers, modals, forms - with consistent spacing, rounded corners, subtle shadows, Inter typography, and Lucide icons. Use this skill whenever the user asks to design, build, create, redesign, improve, or style any VibeDrive page, screen, section, or component - including phrasings like "design the X page", "create UI for X", "build a component for X", "make the X look better", "redesign X", or any request about VibeDrive's frontend, layout, Tailwind classes, or visual polish - even when VibeDrive isn't named explicitly if the conversation context is clearly about it.
disable-model-invocation: false
---

# VibeDrive Web Designer

You are designing frontend UI for **VibeDrive**, a personal learning platform that helps users define skills, break them into milestones, track progress, and receive AI-generated weekly study plans. VibeDrive is a Flask app with server-rendered Jinja2 templates, Tailwind CSS for styling, and vanilla JS for interactions.

The aesthetic target is **soft-minimalist** — calm, airy, focused. Think Notion meets a modern edtech product. Light backgrounds, generous whitespace, one confident accent color, purposeful motion. Not sterile, not over-gamified.

---

## VibeDrive's stack

- **Backend:** Flask, SQLite/PostgreSQL, served via `app.py`
- **Templates:** Jinja2 in `templates/` — e.g. `base.html`, `dashboard.html`, `skill_detail.html`
- **Styles:** Tailwind CSS — utility classes inline on elements. No separate CSS files unless a genuinely custom utility is needed (e.g. progress ring stroke math).
- **Font:** Inter — load via Google Fonts in `base.html`: `<link href="https://fonts.googleapis.com/css2?family=Inter:wght@400;500;600;700&display=swap" rel="stylesheet">`. Apply globally: `font-family: 'Inter', system-ui, Helvetica, Arial, sans-serif`.
- **Scripts:** Vanilla JS in `static/js/` — no frameworks. Used for modals, toggles, chart init, dynamic DOM.
- **Icons:** Lucide via CDN. Used as `<i data-lucide="icon-name"></i>`, initialized with `lucide.createIcons()`. Thin line style, 1.5–2px stroke — matches the soft-minimalist tone perfectly.
- **Charts:** Chart.js via CDN for progress dashboards and analytics.
Do not introduce React, Vue, Alpine, or any CSS-in-JS. Stick to the stack above.

---

## Before you design: check what already exists

If the user's project files are available (repo shared, files uploaded, or you're inside the codebase), open `base.html` and one or two existing templates before generating anything. Consistency matters — VibeDrive should feel like one coherent product.

Look for and reuse:

- **Tailwind config** — custom color tokens, font extensions in `tailwind.config.js`
- **Base layout** — sidebar? topnav? container width? Follow it exactly.
- **Recurring component patterns** — how are cards structured? What does a button look like? What's the nav active state?
- **Jinja2 macros or includes** — if `_card.html` or `_modal.html` exists, extend it rather than reinventing it.
If you can't see existing files and the request is non-trivial, ask the user to paste `base.html` or share a screenshot before proceeding. One screenshot prevents three revision rounds.

---

## Design language

### Color system

A calm, low-contrast palette. The accent color (`blue-500`) appears in under 10% of the UI — CTAs, active states, progress fills, links. Everything else stays neutral.

| Role | Tailwind token | Hex |
|---|---|---|
| Background | `bg-white` | #FFFFFF |
| Secondary background | `bg-gray-50` | #F7F7F8 |
| Border / divider | `border-gray-200` | #E5E7EB |
| Primary text | `text-gray-700` | #374151 |
| Heading text | `text-gray-900` | #111827 |
| Secondary text | `text-gray-400` | #9CA3AF |
| **Primary accent** | `bg-blue-500` / `text-blue-500` | #3B82F6 |
| Accent soft (hover / selection bg) | `bg-blue-50` | #E0EDFF |
| Accent hover (button) | `bg-blue-600` | #2563EB |
| Success / completed | `text-emerald-500` / `bg-emerald-50` | #10B981 |
| Warning / in-progress | `text-amber-500` / `bg-amber-50` | #F59E0B |
| Error / blocked | `text-red-500` / `bg-red-50` | #EF4444 |
| Streak / XP | `text-orange-500` / `bg-orange-50` | #F97316 |

**Usage rules:**
- Backgrounds stay light and airy — use `bg-white` for surfaces, `bg-gray-50` for page background
- Text uses dark neutrals (`gray-700`, `gray-900`), never pure black
- Blue accent is reserved for interactive elements and progress — do not use it decoratively
- Semantic colors (emerald, amber, red) are for status only
### Typography

**Font:** Inter throughout — load it in `base.html`.

| Style | Tailwind classes |
|---|---|
| H1 — Page title | `text-3xl font-semibold text-gray-900 leading-tight` |
| H2 — Section heading | `text-2xl font-semibold text-gray-900 leading-snug` |
| H3 — Card / subsection | `text-xl font-semibold text-gray-800 leading-snug` |
| Body L | `text-lg text-gray-700 leading-relaxed` |
| Body M (default) | `text-base text-gray-700 leading-relaxed` |
| Body S | `text-sm text-gray-600 leading-relaxed` |
| Label / caption | `text-xs font-medium text-gray-400 uppercase tracking-wide` |
| Numbers / percentages | Add `tabular-nums` class or inline style `font-variant-numeric: tabular-nums` |

**Rules:**
- Use font weight (500–700) for hierarchy, not color shifts
- Keep `leading-relaxed` (1.6) on body text for readability
- Avoid decorative or display fonts entirely
### Spacing

4-point base scale. Stick to it — no arbitrary values like `p-[13px]`.

```
4px / 8px / 12px / 16px / 24px / 32px / 48px / 64px
→ p-1 / p-2 / p-3 / p-4 / p-6 / p-8 / p-12 / p-16
```

- Card padding: `p-6` (24px) or `p-8` (32px)
- Between major page sections: `py-12` or `py-16`
- Between cards in a grid: `gap-4` or `gap-6`
- Keep layouts airy — generous whitespace is not wasted space
### Radius and shadows

- Inputs, badges, small elements: `rounded-lg` (8px)
- Cards: `rounded-xl` (12px)
- Modals: `rounded-2xl` (16px)
Shadow: **subtle only**. The standard card shadow is:
```
shadow-sm   →   0 1px 2px rgba(0,0,0,0.05)
```
For modals and dropdowns: `shadow-md` maximum. Never `shadow-lg` or higher for static cards.

On card hover, step up one level: `hover:shadow-md` with `transition-shadow duration-150`.

### Interactions and motion

Soft, purposeful, never bouncy.

- Hover state (buttons, cards): 120–160ms ease transition
- Button: `transition-colors duration-150 ease-in-out`
- Card hover lift: `hover:shadow-md transition-shadow duration-150`
- Active/pressed: 2–4% brightness shift via `active:brightness-95`
- Page transitions: fade or slide-up, 150–200ms
- Avoid: bouncy keyframes, high-contrast flashes, excessive movement
### Progress and completion states

VibeDrive is a progress-tracking product. Use these patterns consistently:

- **Progress bar:** `bg-gray-200` track, `bg-blue-500` fill, `rounded-full h-2`
- **Progress ring:** SVG `<circle>` with `stroke-dasharray` / `stroke-dashoffset`. Use `stroke="currentColor"` with `text-blue-500`. Provide a JS snippet to compute offset from a `data-percent` attribute.
- **Completion badge:** `bg-emerald-50 text-emerald-600 rounded-full px-2.5 py-0.5 text-xs font-medium`
- **In-progress badge:** `bg-amber-50 text-amber-600 ...`
- **Locked / not started:** `bg-gray-100 text-gray-400 ...`
- **Streak indicator:** `<i data-lucide="flame"></i>` + `text-orange-500 font-semibold`
- **XP indicator:** `<i data-lucide="zap"></i>` + `text-orange-500 font-semibold tabular-nums`
---

## Icons: Lucide

Load once in `base.html`:

```html
<script src="https://unpkg.com/lucide@latest"></script>
```

Call `lucide.createIcons()` after DOM ready and after any dynamic DOM insert. In templates:

```html
<i data-lucide="book-open"></i>
```

Lucide's thin line style (1.5–2px stroke, rounded caps) fits the soft-minimalist aesthetic exactly. Size via CSS on the rendered `<svg>`: 16px inline with text, 20px in buttons, 24px for section headers, 48px for empty states.

**VibeDrive icon reference:**

| Context | Icon |
|---|---|
| Skill / learning | `book-open`, `graduation-cap`, `layers` |
| Milestone | `flag`, `check-circle`, `list-checks` |
| Progress | `trending-up`, `bar-chart-2`, `activity` |
| Weekly plan | `calendar`, `clock`, `calendar-check` |
| AI / study plan | `sparkles`, `brain`, `wand-2` |
| Lesson / content | `file-text`, `play-circle`, `youtube` |
| Streak | `flame` |
| XP / points | `zap` |
| Resource | `link`, `video`, `file-text`, `github` |
| Add / new | `plus`, `plus-circle` |
| Settings | `settings`, `sliders-horizontal` |
| User / profile | `user`, `circle-user` |
| Search | `search` |
| Filter | `filter` |
| Notification | `bell` |

One icon per button. One per section heading. One per list row action. Don't over-decorate — icons add clarity only when text alone is insufficient.

---

## Component patterns

Apply these consistently across all VibeDrive pages.

### Cards
```
bg-white border border-gray-200 rounded-xl shadow-sm p-6
hover:shadow-md transition-shadow duration-150
```
Cards are the primary content container. Use for skills, milestones, progress summaries, weekly plans, and quizzes. Do not use raw divs without a card treatment for primary content.

### Buttons

**Primary:**
```
bg-blue-500 hover:bg-blue-600 text-white font-medium
rounded-lg px-4 py-2 text-sm
transition-colors duration-150 ease-in-out
```

**Secondary:**
```
border border-gray-200 bg-white hover:bg-gray-50 text-gray-700 font-medium
rounded-lg px-4 py-2 text-sm
transition-colors duration-150
```

**Tertiary (text-only):**
```
text-blue-500 hover:underline text-sm font-medium
```

### Navigation

- Sticky top bar: logo left, primary actions right, max 5 nav items
- Active nav item: `text-blue-500 font-medium` or a left-border accent `border-l-2 border-blue-500`
- Mobile: bottom nav with 3–5 items, clear labels
### Lesson / content pages

- Centered content column, `max-w-2xl mx-auto` (720px)
- Wide left margin on desktop for breathing room
- Progress indicator at top of page
- Sticky "Next lesson" CTA anchored at the bottom
### Skill card
- Title + category tag + progress bar + percentage + status badge
- Hover: `shadow-md` lift + border shifts to `border-blue-200`
- CTA: "Continue" (in-progress) or "Start" (not started)
### Milestone row
- Status icon left, title + description center, effort estimate right
- Completed: title `line-through text-gray-400`
- Locked: full row `opacity-50 cursor-not-allowed`
### Weekly plan block
- Day label as pill header (`Mon`, `Tue`, etc.) in `bg-gray-100 text-gray-600`
- Each task as checklist item with estimated time
- AI-generated badge: `<i data-lucide="sparkles"></i> AI Generated` with `bg-blue-50 text-blue-500`
### AI content indicators
Any AI-generated content (weekly plan, suggested milestones, resource recs) gets:
```
bg-blue-50 border border-blue-100 rounded-xl p-4
```
With a `<i data-lucide="sparkles"></i>` prefix in `text-blue-500`.

### Empty states
- Centered layout (`text-center max-w-sm mx-auto py-16`)
- Lucide icon at 48px in `text-gray-300`
- Heading in `text-gray-900 font-semibold`, subtext in `text-gray-500 text-sm mt-1`
- Primary CTA button below
---

## Output structure

Structure every design response like this:

### 1. UI plan (2–5 bullets)
Name the key sections and any notable UX decisions. State assumptions explicitly and concisely — one line each. Example: "Assuming the skill detail page shows: skill header with progress ring, milestone list with status badges, and a sidebar with the weekly plan preview. Let me know if you want a different layout."

### 2. The code

- **Template file(s):** Full Jinja2 with `{% extends "base.html" %}` and `{% block content %}`. Use Jinja control flow (`{% for %}`, `{% if %}`) with sensible placeholder variable names the Flask route would pass.
- **Tailwind classes inline:** All styling as utility classes on elements. No separate CSS file unless a custom utility is genuinely necessary (e.g. SVG progress ring math).
- **JS (only if needed):** Vanilla, no frameworks. Small, readable, scoped to the feature.
Each file in its own fenced code block with a path annotation at the top.

### 3. Integration note (1–3 lines)
Which Flask route renders this, what variables the template expects, any new dependency. Keep it brief.

---

## What to avoid

- **Corporate or fintech aesthetics** — VibeDrive is calm and motivating, not a dashboard SaaS
- **Over-gamification** — XP and streaks exist but are subtle, not the whole personality
- **Flat, featureless layouts** — use cards and whitespace to guide attention
- **Tight layouts** — generous spacing is intentional; resist the urge to fill space
- **Multiple accent colors** — blue is the only accent; don't add teal, violet, or purple for decoration
- **Arbitrary spacing** — no `p-[13px]`, `mt-[27px]`. Stay on the 4-point scale.
- **Heavy shadows** — `shadow-sm` for cards, `shadow-md` for modals, nothing heavier
- **Bouncy animations** — 150ms ease transitions only, no spring or bounce keyframes
- **Mobile afterthought** — use `md:` and `lg:` prefixes from the start; cards stack vertically, tables scroll horizontally on narrow viewports
---

## Handling ambiguity

If the request is under-specified, make reasonable assumptions and state them in the UI plan. Example: "Assuming the dashboard shows: streak counter, active skills, weekly plan preview, and recent completions. Let me know if you want different widgets."

Ask only when the answer genuinely changes the architecture: "Is this a full page or a modal?" or "Should milestones be editable inline or via a separate form?"

---

## A worked example

**Request:** "Design the skill detail page"

**UI plan:**
- Hero: skill title, category badge, progress bar + percentage, "Continue Learning" CTA
- Milestone list: status icon, title, effort estimate, expand-for-resources toggle per row
- Sidebar (desktop, `lg:grid-cols-3`): AI learning path summary card + weekly plan preview
- Mobile: sidebar stacks below the milestone list
**Template:** `templates/skill_detail.html` — extends `base.html`. Expects `skill` object (with `.milestones`, `.progress_pct`, `.category`, `.weekly_plan`) from the Flask route.

**JS:** Small script to toggle milestone detail rows and re-run `lucide.createIcons()` after DOM update.

**Integration:** Route `GET /skills/<skill_id>` renders the template. Pass `skill=skill_obj` from the ORM query.
