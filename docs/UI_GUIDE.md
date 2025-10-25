---
title: "Ui Guide"
type: guide
component: general
status: draft
tags: []
---

# User Preferences Dashboard - UI Visual Guide

**Quick visual reference for the completed interface**

---

## Page Layout

```
┌─────────────────────────────────────────────────────────────────┐
│ Navigation Bar (shared_navigation.html)                         │
├─────────────────────────────────────────────────────────────────┤
│                                                                  │
│  User Preferences - ML Training                                 │
│  Define 1-5 job scenarios to train a machine learning model     │
│                                                                  │
├──────────────────────────────────┬──────────────────────────────┤
│                                  │                              │
│  LEFT PANEL (60%)                │  RIGHT PANEL (40%)           │
│  ┌────────────────────────────┐  │  ┌────────────────────────┐ │
│  │  Job Scenarios             │  │  │  Model Status          │ │
│  │  [Add Scenario] [Save All] │  │  │  ❌ Not Trained        │ │
│  └────────────────────────────┘  │  │  [Train Model]         │ │
│                                  │  └────────────────────────┘ │
│  ┌────────────────────────────┐  │                              │
│  │  Scenario 1: Local Job     │  │  ┌────────────────────────┐ │
│  │                            │  │  │  Feature Importance    │ │
│  │  Essential Variables       │  │  │  [Bar Chart]           │ │
│  │  • Salary: [75000    ]     │  │  └────────────────────────┘ │
│  │  • Commute: [20     ]      │  │                              │
│  │  • Hours: [40       ]      │  │  ┌────────────────────────┐ │
│  │  • Arrangement: [Hybrid▼]  │  │  │  Trade-off Explorer    │ │
│  │  • Career: [7──────▮─]     │  │  │  X: [Salary ▼]         │ │
│  │                            │  │  │  Y: [Commute ▼]        │ │
│  │  ▼ Job Characteristics     │  │  │  [Scatter Plot]        │ │
│  │  ▼ Benefits & Work-Life    │  │  └────────────────────────┘ │
│  │                            │  │                              │
│  │  ⭐ How acceptable?        │  │  ┌────────────────────────┐ │
│  │  [0────────▮──────100]     │  │  │  Test Your Model       │ │
│  │         80/100             │  │  │  Salary: [80000   ]    │ │
│  │  [Gradient: Red→Green]     │  │  │  Commute: [15     ]    │ │
│  │                            │  │  │  [Evaluate Job]        │ │
│  │  [Remove]                  │  │  │                        │ │
│  └────────────────────────────┘  │  │  ✅ APPLY             │ │
│                                  │  │  78/100                │ │
│  [+ Add Another Scenario]        │  │  Confidence: 85%       │ │
│                                  │  └────────────────────────┘ │
│                                  │                              │
└──────────────────────────────────┴──────────────────────────────┘
```

---

## Component Details

### 1. Scenario Card (Expanded View)

```
┌──────────────────────────────────────────────────┐
│  Scenario 1: Local Edmonton Job      [Remove]   │
├──────────────────────────────────────────────────┤
│                                                  │
│  Essential Variables                             │
│  ┌────────────────────────────────────────────┐  │
│  │ Salary ($)                                 │  │
│  │ [75000                             ]       │  │
│  │                                            │  │
│  │ Commute (minutes)                          │  │
│  │ [20                                ]       │  │
│  │                                            │  │
│  │ Work Hours/Week                            │  │
│  │ [40                                ]       │  │
│  │                                            │  │
│  │ Work Arrangement                           │  │
│  │ [Hybrid                            ▼]      │  │
│  │                                            │  │
│  │ Career Growth                              │  │
│  │ [1──────────▮───────────────────10]  7     │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ▶ Job Characteristics (5 variables)            │
│  ▼ Benefits & Work-Life (3 variables)           │
│  ┌────────────────────────────────────────────┐  │
│  │ Work Hour Flexibility                      │  │
│  │ [1──────▮─────────────────────10]  5       │  │
│  │                                            │  │
│  │ Vacation Days                              │  │
│  │ [15                                ]       │  │
│  │                                            │  │
│  │ Benefits Quality                           │  │
│  │ [1──────▮─────────────────────10]  5       │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
│  ⭐ How acceptable is this job?                 │
│  ┌────────────────────────────────────────────┐  │
│  │ [0─────────────────▮────────────────100]   │  │
│  │                                            │  │
│  │              75/100                        │  │
│  │                                            │  │
│  │  [Red────Yellow────Green]  ← Gradient     │  │
│  └────────────────────────────────────────────┘  │
│                                                  │
└──────────────────────────────────────────────────┘
```

### 2. Model Status Panel (Untrained)

```
┌──────────────────────────────────┐
│  Model Status                    │
├──────────────────────────────────┤
│                                  │
│  ┌────────────────────────────┐  │
│  │  ❌ Not Trained            │  │
│  └────────────────────────────┘  │
│                                  │
│  ┌────────────────────────────┐  │
│  │    [Train Model]           │  │
│  │      (disabled)            │  │
│  └────────────────────────────┘  │
│                                  │
│  ℹ️  Add scenarios and save     │
│     before training             │
│                                  │
└──────────────────────────────────┘
```

### 3. Model Status Panel (Trained)

```
┌──────────────────────────────────┐
│  Model Status                    │
├──────────────────────────────────┤
│                                  │
│  ┌────────────────────────────┐  │
│  │  ✅ Model Trained          │  │
│  │                            │  │
│  │  RandomForestRegressor     │  │
│  │  R² Score: 0.872           │  │
│  │  Scenarios: 3              │  │
│  └────────────────────────────┘  │
│                                  │
│  ┌────────────────────────────┐  │
│  │    [Retrain Model]         │  │
│  └────────────────────────────┘  │
│                                  │
│  Learned Formula                 │
│  ┌────────────────────────────┐  │
│  │ Acceptance =               │  │
│  │   0.35×Salary +            │  │
│  │   0.28×Career_Growth +     │  │
│  │  -0.22×Commute +           │  │
│  │   0.15×Work_Arrangement    │  │
│  └────────────────────────────┘  │
│                                  │
└──────────────────────────────────┘
```

### 4. Feature Importance Chart

```
┌──────────────────────────────────┐
│  What Matters Most               │
├──────────────────────────────────┤
│                                  │
│  Salary          ████████ 35%    │
│  Career Growth   ██████ 28%      │
│  Commute         ████ 22%        │
│  Work Arr.       ██ 15%          │
│                                  │
│  [Horizontal Bar Chart]          │
│                                  │
└──────────────────────────────────┘
```

### 5. Trade-off Explorer

```
┌──────────────────────────────────┐
│  Trade-off Explorer              │
├──────────────────────────────────┤
│                                  │
│  X-Axis: [Salary         ▼]     │
│  Y-Axis: [Commute Time   ▼]     │
│                                  │
│  Commute (min)                   │
│    60│                           │
│      │                           │
│    40│     🔴 Low acceptance     │
│      │                           │
│    20│  🟢 High    🟡 Medium     │
│      │                           │
│     0└──────────────────────     │
│       60k   75k   90k  Salary    │
│                                  │
│  Legend:                         │
│  🟢 80-100  Excellent            │
│  🟡 60-80   Good                 │
│  🟠 40-60   Borderline           │
│  🔴 0-40    Poor                 │
│                                  │
└──────────────────────────────────┘
```

### 6. Job Preview Panel (Before Evaluation)

```
┌──────────────────────────────────┐
│  Test Your Model                 │
├──────────────────────────────────┤
│                                  │
│  Enter hypothetical job details  │
│  to see if your model would      │
│  recommend applying              │
│                                  │
│  Salary                          │
│  [80000              ]           │
│                                  │
│  Commute (minutes)               │
│  [15                 ]           │
│                                  │
│  Work Hours/Week                 │
│  [40                 ]           │
│                                  │
│  Career Growth (1-10)            │
│  [1──────────▮─────10]  8        │
│                                  │
│  ┌────────────────────────────┐  │
│  │    [Evaluate Job]          │  │
│  └────────────────────────────┘  │
│                                  │
└──────────────────────────────────┘
```

### 7. Job Preview Panel (After Evaluation - APPLY)

```
┌──────────────────────────────────┐
│  Test Your Model                 │
├──────────────────────────────────┤
│                                  │
│  [Same input fields as above]    │
│                                  │
│  ┌────────────────────────────┐  │
│  │        ✅ APPLY            │  │
│  └────────────────────────────┘  │
│                                  │
│           78/100                 │
│                                  │
│  Confidence: 85%                 │
│                                  │
│  Explanation:                    │
│  This job scores well because:   │
│  • Salary above minimum          │
│    ($80k vs $65k)                │
│  • Short commute (15 min)        │
│  • Strong career growth (8/10)   │
│  ⚠ Work hours acceptable         │
│    but at upper limit            │
│                                  │
└──────────────────────────────────┘
```

### 8. Job Preview Panel (After Evaluation - SKIP)

```
┌──────────────────────────────────┐
│  Test Your Model                 │
├──────────────────────────────────┤
│                                  │
│  Salary: [50000      ]           │
│  Commute: [60        ]           │
│  Hours: [55          ]           │
│  Career: [3──▮──] 3              │
│                                  │
│  ┌────────────────────────────┐  │
│  │        ❌ SKIP             │  │
│  └────────────────────────────┘  │
│                                  │
│           32/100                 │
│                                  │
│  Confidence: 92%                 │
│                                  │
│  Explanation:                    │
│  This job does not meet your     │
│  acceptance criteria:            │
│  • Salary too low                │
│    ($50k vs $65k min)            │
│  • Commute too long (60 min)     │
│  • Poor career growth (3/10)     │
│  • Work hours excessive (55h)    │
│                                  │
└──────────────────────────────────┘
```

---

## Color Scheme

### Acceptance Score Gradient
```
  0%                50%               100%
  ├─────────────────┼─────────────────┤
  🔴Red → 🟠Orange → 🟡Yellow → 🟢Green
  #dc3545   #fd7e14   #ffc107   #28a745
```

### Background Colors (Dark Theme)
- Main background: `#1a1a1a`
- Card background: `#2a2a2a`
- Input background: `#3a3a3a`
- Border color: `#3a3a3a`
- Text color: `#e0e0e0`

### Accent Colors
- Primary (buttons): `#4a90e2`
- Success (apply): `#28a745`
- Danger (skip): `#dc3545`
- Warning (borderline): `#ffc107`
- Info (tooltips): `#17a2b8`

---

## Interaction States

### Buttons

**Enabled:**
```
┌──────────────┐
│ [Train Model]│  ← Blue, cursor pointer
└──────────────┘
```

**Disabled:**
```
┌──────────────┐
│ [Train Model]│  ← Gray, cursor not-allowed
└──────────────┘
```

**Loading:**
```
┌──────────────┐
│ ⟳ Training...│  ← Spinner, disabled
└──────────────┘
```

**Hover:**
```
┌──────────────┐
│ [Train Model]│  ← Darker blue, slight scale
└──────────────┘
```

### Range Sliders

**Default:**
```
[1──────▮─────10]  5
 └─Track─Thumb─┘
```

**Dragging:**
```
[1──────▮─────10]  7  ← Value updates in real-time
```

**Color-coded (Acceptance Score):**
```
0                50               100
[🔴────────🟡────────▮──────🟢]  75
```

### Collapsible Sections

**Collapsed:**
```
▶ Job Characteristics (5 variables)
```

**Expanded:**
```
▼ Job Characteristics (5 variables)
┌────────────────────────────────┐
│  [Variable inputs here]        │
└────────────────────────────────┘
```

---

## Toast Notifications

### Success
```
┌─────────────────────────────────┐
│ ✓ Scenarios saved successfully!│  ← Green background
└─────────────────────────────────┘
   (Auto-dismiss after 3 seconds)
```

### Error
```
┌─────────────────────────────────┐
│ ✗ Error: Connection failed      │  ← Red background
└─────────────────────────────────┘
   (Auto-dismiss after 3 seconds)
```

### Info
```
┌─────────────────────────────────┐
│ ℹ Model training in progress... │  ← Blue background
└─────────────────────────────────┘
   (Auto-dismiss after 3 seconds)
```

---

## Responsive Behavior

### Desktop (≥992px)
```
┌─────────────────────────────────────┐
│  [Scenarios 60%] [Visualization 40%]│
└─────────────────────────────────────┘
```

### Tablet (768-991px)
```
┌─────────────────────────────────────┐
│  [Scenarios 50%] [Visualization 50%]│
└─────────────────────────────────────┘
```

### Mobile (<768px)
```
┌────────────────┐
│  [Scenarios]   │
│   (100% width) │
├────────────────┤
│ [Visualization]│
│   (100% width) │
└────────────────┘
```

---

## Animation & Transitions

### Smooth Transitions
- Button hover: `0.2s ease`
- Chart updates: `0.3s ease-in-out`
- Toast slide-in: `0.3s ease-out`
- Accordion expand: `0.2s ease`

### Loading States
- Spinner rotation: `1s linear infinite`
- Pulse effect: `1.5s ease-in-out infinite`

---

## Accessibility Features

### Keyboard Navigation
- Tab through form inputs
- Enter to submit forms
- Space to toggle checkboxes
- Arrow keys for range sliders

### Screen Reader Labels
```html
<label for="salary" aria-label="Annual salary in dollars">
  Salary ($)
</label>
<input id="salary" type="number"
       aria-describedby="salary-help">
```

### Focus Indicators
```
[Input field with blue outline when focused]
```

---

## Real-World Example

**User Story: Steve defines his preferences**

1. **Initial State:**
   - Empty page with "Add Scenario" button
   - Model status: ❌ Not Trained
   - Train button: Disabled

2. **After adding 3 scenarios:**
   - Scenario 1: Local ($70k, 20min, 40h, hybrid) → 75/100
   - Scenario 2: Remote ($95k, 0min, 45h, remote) → 85/100
   - Scenario 3: Min acceptable ($60k, 30min, 40h, onsite) → 50/100
   - Train button: Enabled

3. **After training model:**
   - Status: ✅ Model Trained (RandomForest, R²=0.87)
   - Formula: Acceptance = 0.35×Salary + 0.28×Career - 0.22×Commute + ...
   - Feature chart shows: Salary (35%), Career (28%), Commute (22%)
   - Trade-off chart shows 3 colored points

4. **Testing a job:**
   - Input: $80k, 15min, 40h, 8/10 career
   - Result: ✅ APPLY (78/100, 85% confidence)
   - Explanation highlights salary above min, short commute

---

## Quick Reference

| Element | Location | Purpose |
|---------|----------|---------|
| Scenario Cards | Left panel | Define job examples |
| Train Button | Top right | Start ML training |
| Formula Display | Top right | Show learned equation |
| Feature Chart | Middle right | Importance percentages |
| Trade-off Chart | Middle right | Visualize factor pairs |
| Job Preview | Bottom right | Test hypothetical jobs |
| Toast Notifications | Top right corner | User feedback |

---

**Visual design philosophy:**
- **Clean:** Minimal clutter, focused on task
- **Intuitive:** Clear labels, obvious actions
- **Responsive:** Works on all screen sizes
- **Accessible:** Keyboard navigation, screen readers
- **Modern:** Dark theme, smooth animations
- **Data-driven:** Charts make ML transparent

For implementation details, see `frontend_templates/preferences.html`
