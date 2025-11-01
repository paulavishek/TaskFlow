# Simple Gantt Chart Implementation Guide

## 📋 Data Model Changes

### Step 1: Update Task Model (5 minutes)

Add these fields to your existing Task model:

```python
# models.py
class Task(models.Model):
    # ... existing fields ...
    
    # NEW FIELDS FOR GANTT
    start_date = models.DateField(null=True, blank=True)
    due_date = models.DateField(null=True, blank=True)  # You may already have this
    progress = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # OPTIONAL: For task dependencies
    dependencies = models.ManyToManyField(
        'self', 
        blank=True, 
        symmetrical=False,
        related_name='dependent_tasks'
    )
    
    def duration_days(self):
        """Calculate task duration"""
        if self.start_date and self.due_date:
            return (self.due_date - self.start_date).days
        return 0
```

### Step 2: Database Migration

```bash
python manage.py makemigrations
python manage.py migrate
```

---

## 🎨 Frontend Implementation

### Installation

```bash
# Install Frappe Gantt
npm install frappe-gantt
# or
yarn add frappe-gantt
```

### Basic Gantt Component (React)

```jsx
// components/gantt/GanttChart.jsx
import React, { useEffect, useRef } from 'react';
import Gantt from 'frappe-gantt';
import 'frappe-gantt/dist/frappe-gantt.css';

function GanttChart({ tasks }) {
  const ganttRef = useRef(null);
  const ganttInstance = useRef(null);

  useEffect(() => {
    if (!tasks || tasks.length === 0) return;

    // Convert tasks to Frappe Gantt format
    const ganttTasks = tasks
      .filter(task => task.start_date && task.due_date)
      .map(task => ({
        id: task.id,
        name: task.title,
        start: task.start_date,
        end: task.due_date,
        progress: task.progress || 0,
        dependencies: task.dependencies?.join(',') || '',
        custom_class: getTaskClass(task)
      }));

    if (ganttTasks.length === 0) {
      return; // No tasks with dates
    }

    // Initialize Gantt
    if (ganttInstance.current) {
      ganttInstance.current.refresh(ganttTasks);
    } else {
      ganttInstance.current = new Gantt(ganttRef.current, ganttTasks, {
        view_mode: 'Week',
        bar_height: 30,
        bar_corner_radius: 3,
        arrow_curve: 5,
        padding: 18,
        date_format: 'YYYY-MM-DD',
        language: 'en',
        on_click: (task) => {
          console.log('Task clicked:', task);
          // You can open task detail modal here
        },
        on_date_change: (task, start, end) => {
          // Update task dates when user drags the bar
          updateTaskDates(task.id, start, end);
        },
        on_progress_change: (task, progress) => {
          // Update task progress when user drags progress handle
          updateTaskProgress(task.id, progress);
        }
      });
    }

    return () => {
      if (ganttInstance.current) {
        ganttInstance.current = null;
      }
    };
  }, [tasks]);

  const getTaskClass = (task) => {
    // Color-code based on status
    if (task.status === 'done') return 'bar-milestone';
    if (task.status === 'in_progress') return 'bar-success';
    return 'bar-default';
  };

  const updateTaskDates = async (taskId, start, end) => {
    await fetch(`/api/tasks/${taskId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        start_date: start.toISOString().split('T')[0],
        due_date: end.toISOString().split('T')[0]
      })
    });
  };

  const updateTaskProgress = async (taskId, progress) => {
    await fetch(`/api/tasks/${taskId}/`, {
      method: 'PATCH',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({ progress })
    });
  };

  return (
    <div className="gantt-container">
      <div className="gantt-header">
        <h2>📊 Project Timeline</h2>
        <div className="view-buttons">
          <button onClick={() => ganttInstance.current?.change_view_mode('Day')}>Day</button>
          <button onClick={() => ganttInstance.current?.change_view_mode('Week')}>Week</button>
          <button onClick={() => ganttInstance.current?.change_view_mode('Month')}>Month</button>
        </div>
      </div>
      <svg ref={ganttRef}></svg>
    </div>
  );
}

export default GanttChart;
```

### Add Custom Styling

```css
/* gantt.css */
.gantt-container {
  padding: 20px;
  background: white;
  border-radius: 8px;
  box-shadow: 0 2px 8px rgba(0,0,0,0.1);
}

.gantt-header {
  display: flex;
  justify-content: space-between;
  align-items: center;
  margin-bottom: 20px;
}

.view-buttons button {
  margin-left: 8px;
  padding: 8px 16px;
  border: 1px solid #ddd;
  background: white;
  border-radius: 4px;
  cursor: pointer;
}

.view-buttons button:hover {
  background: #f5f5f5;
}

/* Custom task colors */
.bar-milestone {
  fill: #FFD700 !important;
}

.bar-success {
  fill: #4CAF50 !important;
}

.bar-default {
  fill: #2196F3 !important;
}
```

---

## 🔌 Backend API Update

### Serializer Enhancement

```python
# serializers.py
class TaskSerializer(serializers.ModelSerializer):
    dependencies = serializers.PrimaryKeyRelatedField(
        many=True, 
        queryset=Task.objects.all(),
        required=False
    )
    duration_days = serializers.ReadOnlyField()
    
    class Meta:
        model = Task
        fields = [
            'id', 'title', 'description', 'status',
            'start_date', 'due_date', 'progress',
            'dependencies', 'duration_days',
            'assigned_to', 'created_at'
        ]
```

### API Endpoint for Gantt Data

```python
# views.py
from rest_framework.decorators import action

class TaskViewSet(viewsets.ModelViewSet):
    # ... existing methods ...
    
    @action(detail=False, methods=['get'])
    def gantt_data(self, request):
        """Get tasks formatted for Gantt chart"""
        board_id = request.query_params.get('board_id')
        
        tasks = Task.objects.filter(
            column__board_id=board_id,
            start_date__isnull=False,
            due_date__isnull=False
        ).select_related('assigned_to').prefetch_related('dependencies')
        
        serializer = self.get_serializer(tasks, many=True)
        return Response(serializer.data)
```

**Usage**: `GET /api/tasks/gantt_data/?board_id=123`

---

## 🎯 Minimal Feature Set

### Must-Have Features (Week 1):
- ✅ Display tasks as horizontal bars
- ✅ Bar length = duration (start_date to due_date)
- ✅ Progress bar fill (colored based on %)
- ✅ Week/Month view toggle
- ✅ Click bar → open task details

### Nice-to-Have (Week 2):
- ✅ Drag bars to reschedule tasks
- ✅ Drag progress handle to update completion
- ✅ Dependency arrows between tasks
- ✅ Color-coding by status

### Skip These (Not Essential):
- ❌ Critical path calculation
- ❌ Resource allocation view
- ❌ Baseline/planned vs actual
- ❌ Export to PDF/Excel
- ❌ Real-time collaboration on Gantt
- ❌ Automatic scheduling (AI-powered)
- ❌ Multiple projects on one chart
- ❌ Cost tracking

---

## 📊 Data Flow Diagram

```
User Action                  Frontend                Backend
─────────────────────────────────────────────────────────────
                                                    
View Gantt    ──────────>  Fetch tasks    ───────> GET /api/tasks/gantt_data/
                           │                         │
                           │                         │ Query tasks with dates
                           │                         │
                           │  <────────────────────  Return JSON
                           │
                           Convert to Gantt format
                           │
                           Render with Frappe Gantt
                           │
User drags bar ─────────>  Calculate new dates
                           │
                           Update backend ─────────> PATCH /api/tasks/{id}/
                           │                         │
                           │  <────────────────────  Success
                           │
                           Refresh chart
```

---

## 🎨 UI Integration Options

### Option 1: Separate Gantt Page
```
/boards/{id}/gantt
```
Add tab in board header: `Kanban | Calendar | Gantt`

### Option 2: Modal View
Add "Gantt View" button on board → opens full-screen modal

### Option 3: Split View (Advanced)
Left: Kanban board | Right: Gantt chart (synchronized)

**Recommendation**: Start with **Option 1** (simplest)

---

## 🚀 Quick Implementation Steps

### Day 1: Backend (2 hours)
1. ✅ Add `start_date`, `progress` fields to Task model
2. ✅ Run migrations
3. ✅ Update TaskSerializer
4. ✅ Create `/api/tasks/gantt_data/` endpoint
5. ✅ Test API with Postman

### Day 2: Frontend Setup (2 hours)
1. ✅ Install `frappe-gantt` package
2. ✅ Create `GanttChart.jsx` component
3. ✅ Add route `/boards/{id}/gantt`
4. ✅ Fetch data and display basic Gantt

### Day 3: Interactivity (3 hours)
1. ✅ Enable drag-to-reschedule
2. ✅ Enable progress updates
3. ✅ Add view mode toggles (Day/Week/Month)
4. ✅ Style with custom CSS

### Day 4: Dependencies (2 hours)
1. ✅ Add `dependencies` field to Task model
2. ✅ Create UI to set dependencies (dropdown on task form)
3. ✅ Display dependency arrows on Gantt

### Day 5: Polish (2 hours)
1. ✅ Add loading states
2. ✅ Handle edge cases (no dates, empty board)
3. ✅ Add "Add Task" button from Gantt view
4. ✅ Color-code by status/priority
5. ✅ Test drag-and-drop updates

**Total: ~11 hours = 1 week part-time**

---

## 💡 Smart Defaults

### Auto-set Start Date
When user creates a task with due_date but no start_date:

```python
def save(self, *args, **kwargs):
    if self.due_date and not self.start_date:
        # Default: task takes 3 days
        self.start_date = self.due_date - timedelta(days=3)
    super().save(*args, **kwargs)
```

### Auto-calculate Progress
If you track task completion with subtasks:

```python
@property
def progress(self):
    if self.subtasks.count() == 0:
        return 0 if self.status != 'done' else 100
    
    completed = self.subtasks.filter(status='done').count()
    return int((completed / self.subtasks.count()) * 100)
```

---

## 🎁 Bonus: One AI Feature

### Smart Duration Estimation

When user creates a task, AI suggests duration:

```python
def estimate_task_duration(title, description):
    prompt = f"""
    Estimate how many days this task should take:
    Title: {title}
    Description: {description}
    
    Consider typical software development timelines.
    Respond with just a number (e.g., "5" for 5 days).
    """
    
    response = gemini_api.generate(prompt)
    days = int(response.strip())
    
    return {
        'suggested_start': date.today(),
        'suggested_end': date.today() + timedelta(days=days),
        'estimated_days': days
    }
```

---

## 📸 What It Looks Like (Example)

```
Project: Website Redesign
─────────────────────────────────────────────────────────────
                Oct 1      Oct 8      Oct 15     Oct 22
Design Phase    ████████░░░░░░                              80%
  ├─> Development         ███████████░░░░░░                 70%
       └─> Testing                      ██████████           45%
Deployment                                      ████████████ 0%
─────────────────────────────────────────────────────────────
Today: Oct 12 (↓)
```

**Visual cues:**
- Solid color = completed work
- Light color = remaining work
- Arrows = dependencies (Testing can't start until Development finishes)
- Diamond = milestone

---

---

## 🔧 Complete Code Example

Here's a minimal working example you can copy-paste:

### HTML/JavaScript Version (Simplest)

```html
<!DOCTYPE html>
<html>
<head>
    <link rel="stylesheet" href="https://unpkg.com/frappe-gantt/dist/frappe-gantt.css">
    <script src="https://unpkg.com/frappe-gantt"></script>
</head>
<body>
    <h1>Project Timeline</h1>
    <div id="gantt"></div>
    
    <script>
        const tasks = [
            {
                id: '1',
                name: 'Design Homepage',
                start: '2024-10-01',
                end: '2024-10-05',
                progress: 80
            },
            {
                id: '2',
                name: 'Build Backend API',
                start: '2024-10-05',
                end: '2024-10-15',
                progress: 60,
                dependencies: '1'
            },
            {
                id: '3',
                name: 'QA Testing',
                start: '2024-10-15',
                end: '2024-10-20',
                progress: 30,
                dependencies: '2'
            }
        ];
        
        const gantt = new Gantt("#gantt", tasks, {
            view_mode: 'Week',
            on_click: task => alert(`Task: ${task.name}`),
            on_date_change: (task, start, end) => {
                console.log('Rescheduled:', task.name, start, end);
            }
        });
    </script>
</body>
</html>
```

**That's 40 lines!** Fully functional Gantt chart.

---

## 🎯 Final Recommendation

**Implement:**
1. Add `start_date` and `progress` fields (5 min)
2. Install Frappe Gantt (2 min)
3. Create basic GanttChart component (1 hour)
4. Add Gantt page to your app (30 min)
5. Enable drag-to-reschedule (1 hour)
6. Add dependencies (optional, 2 hours)

**Total: 4-6 hours** for working Gantt chart!
---

## 🚀 Start Here (30-Minute MVP)

If you want the absolute fastest path:

1. Add this to your existing Task API response:
   ```python
   {
       "id": "1",
       "title": "Task name",
       "start_date": "2024-10-01",
       "due_date": "2024-10-05",
       "progress": 60
   }
   ```

2. Copy the HTML example above into a new page

3. Fetch your tasks and pass them to Frappe Gantt

