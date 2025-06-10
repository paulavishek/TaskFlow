# Digital Kanban Board

A powerful, feature-rich web application for digital Kanban project management designed to improve team collaboration and workflow visibility.

![Digital Kanban Board Logo](static/img/favicon.ico)

## Table of Contents

- [Overview](#overview)
- [Key Features](#key-features)
- [Getting Started](#getting-started)
- [User Guide](#user-guide)
- [Productivity Tracking](#productivity-tracking)
- [Technical Information](#technical-information)
- [Security & Privacy](#security--privacy)
- [Contributing](#contributing)
- [License](#license)

## Overview

Digital Kanban Board is a modern project management tool built on the principles of Kanban methodology. It helps teams organize work, manage tasks, and improve workflow efficiency through visual management. The application is designed to be intuitive for non-technical users while offering powerful features for complex project requirements.

## Key Features

### Organization & Team Management
- **Multi-Organization Support**: Separate workspaces for different organizations
- **Team Collaboration**: Add team members to boards for collaborative work
- **Role-Based Permissions**: Control who can view, edit, and manage boards

### Board Management
- **Customizable Boards**: Create and configure boards for different projects or workflows
- **Flexible Columns**: Add, rename, and reorder columns to match your workflow stages
- **Drag and Drop Interface**: Intuitive movement of tasks between workflow stages

### Task Management
- **Rich Task Details**: Title, description, due dates, assignees, and more
- **Task Labels**: Color-coded labels for easy categorization and filtering
- **Task Progress**: Percentage-based progress tracking
- **Priority Levels**: Mark tasks as low, medium, high, or urgent
- **Commenting System**: Discussion threads on individual tasks

### Analytics & Reporting
- **Board Analytics**: Visual graphs showing task distribution and completion rates
- **Productivity Metrics**: Track team and individual productivity
- **Completion Trends**: Monitor how task completion evolves over time
- **User Performance**: See who completes the most tasks and at what rate
- **AI-Powered Insights**: Get natural language insights and risk identification from your board data

### AI-Powered Features
- **Smart Task Assistant**: Generate detailed task descriptions and checklists from simple task titles
- **Comment Summarization**: Quickly understand long comment threads through AI-generated summaries
- **Lean Six Sigma Classification**: Get AI suggestions for proper LSS classification of tasks
- **Analytics Insights**: Receive human-readable analysis of your board metrics and potential risks

### Import/Export
- **Data Portability**: Export boards as JSON or CSV
- **Easy Migration**: Import boards from JSON files
- **Backup & Restore**: Save board configurations and task data

## Getting Started

### System Requirements
- Web browser (Chrome, Firefox, Safari, Edge recommended)
- Internet connection
- Gemini API key for AI features (obtain from https://makersuite.google.com/app/apikey)

### Setting Up AI Features
1. Create a `.env` file in the project root (use `.env-example` as a template)
2. Add your Gemini API key to the `.env` file: `GEMINI_API_KEY=your_api_key_here`
3. Test your API key by running `python test_gemini_api.py`

### User Registration
1. Navigate to the application login page
2. Click "Register" to create a new account
3. Enter your details and choose a secure password
4. Follow the email verification process (if applicable)

### Creating Your First Board
1. After logging in, click "New Board"
2. Name your board and add an optional description
3. Your board will be created with default columns (To Do, In Progress, Done)
4. Start adding tasks by clicking "Add Task" in the To Do column

## User Guide

### Board Navigation
The application organizes work into boards, columns, and tasks:
- **Boards**: Represent projects or work areas
- **Columns**: Represent stages in your workflow (e.g., To Do, In Progress, Done)
- **Tasks**: Individual work items that move through the workflow

### Managing Tasks
- **Create tasks** with the "Add Task" button
- **Move tasks** by dragging and dropping between columns
- **Update progress** using the progress bar on each task
- **Add details** by clicking on a task to open its detailed view

### Using Filters and Search
- Use the search panel to filter tasks by:
  - Text content (title or description)
  - Column
  - Priority level
  - Label
  - Assignee

### Exporting and Importing Boards
- **Export**: Click the "Export" button on a board and choose JSON or CSV format
- **Import**: On the boards list page, click "Import Board" and select a previously exported JSON file

### Using AI Features

#### Task Assistant
1. Start creating a new task by entering a title
   - **Pro Tip:** Use specific, detailed titles for better AI-generated content
   - Example: Instead of "Add a feature", use "Add user profile picture upload"
2. Click "Generate with AI" next to the description field
3. Review and edit the AI-generated description and checklist as needed

#### Comment Summarization
1. On a task with several comments, locate the "Summarize with AI" button
2. Click the button to generate a concise summary of the comment thread
3. The summary will appear at the top of the comments section

#### Lean Six Sigma Classification
1. When creating or editing a task, click "Suggest LSS Classification"
2. The AI will analyze your task's title and description
3. It will suggest the most appropriate classification (Value-Added, Necessary Non-Value-Added, or Waste)
4. Use this suggestion to help select the appropriate LSS label

#### Analytics Insights
1. Navigate to a board's Analytics page
2. Click "Generate Insights" in the AI-Powered Insights section
3. The AI will analyze your board's metrics and provide human-readable insights
4. Pay special attention to any risks or improvement opportunities identified

## Productivity Tracking

Digital Kanban Board helps you understand and improve team productivity through several metrics:

### How Productivity is Measured

The application uses a comprehensive approach to measure productivity:

1. **Task Progress Percentage**: Each task has a progress percentage (0-100%)
   - Tasks can be manually updated with progress percentages
   - Tasks in the "Done" column automatically reach 100%

2. **Overall Productivity Score**: Calculated as the average progress across all tasks
   - Formula: (Sum of all task progress) / (Total number of tasks × 100) × 100
   - Example: If you have 10 tasks with average 60% completion, productivity is 60%

3. **Completion Rate**: Percentage of tasks that are fully completed
   - Formula: (Number of completed tasks) / (Total number of tasks) × 100
   - Tasks in the "Done" column are counted as completed

4. **User Performance**: Individual productivity metrics
   - Tasks assigned and completed per user
   - Average completion time per user
   - Completion percentage per user

### Interpreting Productivity Metrics

- **Productivity Score (0-100%)**: Higher percentages indicate more work completion
  - 0-30%: Early project stages or blocked progress
  - 31-70%: Active work in progress
  - 71-100%: Nearing completion or high productivity

- **Completion Trends**: Graph showing tasks completed over time
  - Upward trend: Increasing team velocity
  - Flat or downward trend: Potential issues to address

- **User Performance**: Helps identify:
  - Team members who may need assistance
  - High performers who can mentor others
  - Workload imbalances requiring redistribution

## Technical Information

Digital Kanban Board is built with modern web technologies:

- **Framework**: Django (Python web framework)
- **Frontend**: HTML5, CSS3, JavaScript with Bootstrap
- **Database**: SQLite (default), compatible with PostgreSQL
- **Hosting**: Can be self-hosted or deployed to cloud platforms

## Security & Privacy

- **Authentication**: Secure user authentication system
- **Data Protection**: Information is accessible only to authorized users
- **Organization Isolation**: Data is separated by organization

## Contributing

We welcome contributions to the Digital Kanban Board project! Please see [CONTRIBUTING.md](CONTRIBUTING.md) for details on how to contribute.

## License

This project is licensed under the MIT License - see the LICENSE file for details.

---

© 2025 Digital Kanban Board. All rights reserved.