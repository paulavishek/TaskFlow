# 🚀 TaskFlow Demo - Quick Reference Card

## 👥 TEST USER CREDENTIALS

### ADMIN
```
Username: admin
Password: admin123
```

### DEV TEAM (5 Users)
```
john_doe          | JohnDoe@2024
jane_smith        | JaneSmith@2024
robert_johnson    | RobertJ@2024
alice_williams    | AliceW@2024
bob_martinez      | BobM@2024
```

### MARKETING TEAM (2 Users)
```
carol_anderson    | CarolA@2024
david_taylor      | DavidT@2024
```

---

## 📊 DEMO DATA STATS

| Item | Count |
|------|-------|
| Boards | 3 |
| Total Tasks | 27 |
| Risk Assessments | 12 |
| Stakeholders | 5 |
| Chat Rooms | 12 |
| Chat Messages | 60+ |
| Organizations | 2 |

---

## 🎯 KEY BOARDS

### Software Project (Dev Team)
- 11 tasks, 5 columns
- Risk data, resource forecasts, stakeholder tracking
- Members: 5 developers

### Bug Tracking (Dev Team)  
- 7 bug tasks
- Severity levels, risk assessments
- Members: 4 team members

### Marketing Campaign (Marketing Team)
- 9 tasks across 5 stages
- Campaign-specific labels
- Members: 2 marketers

---

## 💬 CHAT FEATURES

**4 Chat Rooms per Board**:
- General Discussion
- Technical Support
- Feature Planning
- Random Chat

**Total**: 12 rooms with 5-10 messages each

---

## ✨ FEATURES TO TEST

- [ ] Drag-drop tasks between columns
- [ ] View risk assessments (Critical/High)
- [ ] Check resource utilization (82-100%)
- [ ] Review stakeholder involvement
- [ ] Explore task dependencies
- [ ] Send messages in chat rooms
- [ ] Assign tasks to team members
- [ ] View Lean Six Sigma labels

---

## 🏃 QUICK START

```bash
python manage.py runserver
# Navigate to http://localhost:8000
# Log in with any user above
# Explore the boards!
```

---

## 🔄 RESET DEMO (if needed)

```bash
rm db.sqlite3
python manage.py migrate
python manage.py populate_test_data
```

---

## 🎓 SAMPLE SCENARIOS

**As Carol Anderson (Marketing)**:
1. Log in with carol_anderson | CarolA@2024
2. Go to Marketing Campaign board
3. Send a message in General Discussion
4. View stakeholder engagement

**As John Doe (Developer)**:
1. Log in with john_doe | JohnDoe@2024
2. Go to Software Project board
3. Check assigned tasks
4. Review risk assessments
5. Discuss in Technical Support chat

**As Admin**:
1. Log in with admin | admin123
2. Switch between organizations
3. View all boards and users
4. Check resource forecasts
5. Monitor stakeholder metrics

---

## 📝 FEATURE COVERAGE

| Feature | Demo Data | Users | Test |
|---------|-----------|-------|------|
| Kanban | ✅ 27 tasks | ✅ 8 users | ✅ Ready |
| Risk Mgmt | ✅ 12 items | ✅ Multiple | ✅ Ready |
| Resources | ✅ 4 forecasts | ✅ 2 users | ✅ Ready |
| Stakeholders | ✅ 5 people | ✅ Involved | ✅ Ready |
| Dependencies | ✅ 5 chains | ✅ All boards | ✅ Ready |
| Chat/Messaging | ✅ 60+ msgs | ✅ All users | ✅ Ready |
| Lean Six Sigma | ✅ Labeled | ✅ All tasks | ✅ Ready |

---

**Generated**: October 30, 2024  
**Version**: 2.0 - Full Feature Set
