# TaskFlow Testing Guide

## Setup for Testing

Before you can test the AI features, you need to populate the database with test data:

1. Run the following command to populate the database with comprehensive test data:

   ```
   python populate_for_testing.py
   ```

2. This script will:
   - Create test users (admin, john_doe, jane_smith, robert_johnson)
   - Create organizations, boards, columns, and labels
   - Create tasks with Lean Six Sigma classifications
   - Add comments for testing the comment summarization feature
   - Create tasks for testing the task description generation
   - Create tasks for testing analytics insights

3. Once the script completes, you can log in with any of these credentials:
   - Username: admin, Password: admin123
   - Username: john_doe, Password: test1234
   - Username: jane_smith, Password: test1234
   - Username: robert_johnson, Password: test1234

## Testing the AI Features

### 1. Task Description Generation

1. Navigate to the Software Project board
2. Click "Create Task" or edit an existing task
3. Enter a title (e.g., "Optimize database queries")
4. Click "Generate with AI" next to the description field
5. The AI will generate a structured description with objectives and a checklist

### 2. Comment Summarization

1. Open the task "Implement AI-powered task recommendations"
2. This task has multiple comments discussing the implementation
3. Click the "Summarize Comments" or "Summarize with AI" button
4. The AI will generate a concise summary of the conversation

### 3. Lean Six Sigma Classification

1. Create a new task or edit an existing task
2. Enter a title and description
3. Click "Suggest LSS Classification"
4. The AI will analyze your task and suggest:
   - Value-Added (transforms the product in a way the customer values)
   - Necessary Non-Value-Added (required but doesn't directly add value)
   - Waste/Eliminate (consumes resources without adding value)

### 4. Analytics Insights

1. Navigate to the Software Project board
2. Click on "Analytics" or "Board Analytics"
3. View the analytics dashboard
4. Click on "Generate Insights" or look for the insights section
5. The AI will analyze the board data and provide strategic insights

## Notes for Testing

- If the AI features aren't working, check that your GEMINI_API_KEY is properly configured
- The test data is designed to showcase different aspects of each AI feature
- The Software Project board has tasks with various Lean Six Sigma classifications to demonstrate the analytics features

## Manual Testing Checklist

- [ ] Task Description Generation
- [ ] Comment Summarization
- [ ] Lean Six Sigma Classification
- [ ] Analytics Insights
- [ ] Task distribution by column
- [ ] Task distribution by priority
- [ ] Tasks by Lean Six Sigma category
- [ ] Value-added percentage calculation
