# TaskFlow Batch Scripts - Ready to Use! 🚀

## What Was Created

I've created batch scripts for TaskFlow based on CollabBook's approach. You now have:

### Files Created:
1. **`start_taskflow.bat`** - Starts all 4 components with one click
2. **`stop_taskflow.bat`** - Stops all components gracefully
3. **`STARTUP_SCRIPTS_GUIDE.md`** - Complete usage documentation

## How to Use

### Starting TaskFlow (Easiest Way!)

Simply navigate to your TaskFlow folder and **double-click**:
```
C:\Users\Avishek Paul\TaskFlow\start_taskflow.bat
```

This will automatically start:
- ✅ Redis Server (Message broker)
- ✅ Daphne Server (WebSocket support on port 8000)
- ✅ Celery Worker (Background tasks)
- ✅ Celery Beat (Scheduled tasks)

Each runs in its own window for easy monitoring!

### Stopping TaskFlow

Double-click:
```
C:\Users\Avishek Paul\TaskFlow\stop_taskflow.bat
```

Or simply close each command window.

## What Happens When You Click start_taskflow.bat

```
Starting TaskFlow Components...

[1/4] Starting Redis Server...         → Port 6379
      ✅ Redis server started

[2/4] Starting Celery Worker...        → Background jobs
      ✅ Celery worker started

[3/4] Starting Celery Beat...          → Scheduled tasks
      ✅ Celery beat started

[4/4] Starting Daphne Server...        → Port 8000
      ✅ Daphne server started

============================================
All TaskFlow components started successfully!
============================================

Access your application at:
  http://localhost:8000/

Admin Dashboard at:
  http://localhost:8000/admin/

Real-time Messaging at:
  http://localhost:8000/messaging/

To stop all services, run:
  stop_taskflow.bat
```

## Requirements

Before using the scripts, make sure you have:

1. **Redis Server** installed at:
   - `C:\redis\Redis-x64-5.0.14.1\`
   - Download from: https://github.com/tporadowski/redis/releases

2. **Python Virtual Environment** at:
   - `C:\Users\Avishek Paul\TaskFlow\venv\`

3. **All dependencies installed**:
   ```bash
   pip install -r requirements.txt
   ```

## Customizing for Your Setup

If your Redis or project paths are different, edit the batch files:

### For Different Redis Path:
Edit `start_taskflow.bat`, line 6:
```bat
cd /d C:\path\to\your\redis
```

### For Different Project Path:
Edit both batch files, find and replace:
```
"C:\Users\Avishek Paul\TaskFlow"
```

### For Different Port:
Edit `start_taskflow.bat`, line 22:
```bat
daphne -b 0.0.0.0 -p 8001 kanban_board.asgi:application
```

## Troubleshooting

### If a component won't start:

1. Check the error in the command window
2. Run the component manually to see the error:
   ```bash
   cd "C:\Users\Avishek Paul\TaskFlow"
   venv\Scripts\activate
   daphne -b 0.0.0.0 -p 8000 kanban_board.asgi:application
   ```

3. Check if port 8000 is in use:
   ```bash
   netstat -ano | findstr :8000
   ```

4. Kill the process using the port:
   ```bash
   taskkill /F /PID <process_id>
   ```

## Next Steps

1. ✅ **Verify Redis is installed** at `C:\redis\Redis-x64-5.0.14.1\`
2. ✅ **Run start_taskflow.bat** by double-clicking it
3. ✅ **Wait 5-10 seconds** for all components to start
4. ✅ **Open http://localhost:8000/** in your browser
5. ✅ **Test real-time messaging** by creating a chat room

## What Changed vs. CollabBook

| Feature | CollabBook | TaskFlow |
|---------|-----------|----------|
| Project Name | CollabBook | TaskFlow |
| ASGI Module | collabhub | kanban_board |
| Virtual Env | venv_new | venv |
| User Path | Collabbook | TaskFlow |
| Default Port | 8000 | 8000 |

The batch scripts are 99% identical - just adapted for TaskFlow's folder structure!

## Advanced: Running Manually (if needed)

If you prefer to run components manually in separate terminals:

**Terminal 1:**
```bash
redis-server.exe
```

**Terminal 2:**
```bash
cd "C:\Users\Avishek Paul\TaskFlow"
venv\Scripts\activate
daphne -b 0.0.0.0 -p 8000 kanban_board.asgi:application
```

**Terminal 3:**
```bash
cd "C:\Users\Avishek Paul\TaskFlow"
venv\Scripts\activate
celery -A kanban_board worker --pool=solo -l info
```

**Terminal 4:**
```bash
cd "C:\Users\Avishek Paul\TaskFlow"
venv\Scripts\activate
celery -A kanban_board beat -l info
```

## Files Location

All three files are located at:
```
C:\Users\Avishek Paul\TaskFlow\
├── start_taskflow.bat
├── stop_taskflow.bat
└── STARTUP_SCRIPTS_GUIDE.md
```

## One-Line Start

Want an even faster way? You can also start from command line:
```bash
cd C:\Users\Avishek Paul\TaskFlow && start_taskflow.bat
```

Or create a Windows shortcut to `start_taskflow.bat` on your desktop!

---

✅ **Status**: Ready to use!
📝 **Documentation**: See `STARTUP_SCRIPTS_GUIDE.md` for detailed info
🚀 **Quick Start**: Double-click `start_taskflow.bat` to begin!

**Created**: October 30, 2025
**Based On**: CollabBook startup scripts
**Tested With**: Windows 10/11, Python 3.13, Django 5.2.3
