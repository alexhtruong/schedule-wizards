# Example User Flows

## 1. The Transfer Student's Course Planning Journey

Maya is a transfer student who needs to efficiently plan her upcoming quarters. She wants to maximize her chances of success while managing her workload carefully across multiple engineering courses.

First, Maya calls GET `/courses?&sort=workload&order=asc` to find all engineering foundation courses, sorted by workload. She identifies three crucial courses: ME211, ME212, and CE201.

For each course, Maya:

1. Calls GET `/courses/{id}/statistics` to understand the overall picture:
   - ME211: 3.8/5 rating, 15hrs/week average workload
   - ME212: 4.1/5 rating, 12hrs/week average workload
   - CE201: 3.2/5 rating, 18hrs/week average workload

2. Uses GET `/courses/{id}/professors` for each course to find professors teaching next quarter:
   - ME211: Prof. Hall and Prof. Johnson
   - ME212: Prof. Williams
   - CE201: Prof. Chen and Prof. Rodriguez

3. Calls GET `/professors/{id}` for each professor to deep dive into their teaching styles and student experiences

After thorough research, Maya:
1. Creates a new review via POST `/reviews` with detailed feedback
2. Adds a new professor using POST `/professors`

## 2. The Department Chair's Curriculum Review

Dr. Thompson, the Engineering department chair, needs to evaluate course effectiveness and teaching quality across the department.

Her investigation flow:

1. First, she calls GET `/courses?department=ME` to list all Mechanical Engineering courses.

2. For each core course, she calls GET `/courses/{id}/statistics` to analyze:
   - Overall course performance
   - Difficulty trends
   - Workload distribution
   - Common student feedback themes

3. She notices unusually high difficulty ratings in ME304 and investigates deeper:
   - Calls GET `/courses/ME304/professors` to see all professors
   - Uses GET `/professors/{id}` for each professor
   - Discovers a significant disparity in student success rates between professors

4. Dr. Thompson identifies areas for improvement:
   - Creates new professors via POST `/professors`
   - Creates new courses via POST `/courses`

## 3. Student Course Guide Project

Some anonymous person decides to create a guide for new students. They use the API to gather and verify information across multiple courses and professors.

The research process:

1. They start broad with GET `/courses?sort=rating&order=desc` to identify the most highly-rated courses.

2. For each department's core courses:
   - Call GET `/courses/{id}/statistics` to gather statistical data
   - Use GET `/courses/{id}/professors` to find all professors
   - Analyze GET `/professors/{id}` for each professor's teaching history

3. They enhance the database quality by:
   - Creating new courses via POST `/courses`
   - Creating new professors via POST `/professors`
   - Creating detailed reviews via POST `/reviews`

4. For the popular "ME212 - Engineering Dynamics" course, they conduct a deep dive:
   - Analyze professor ratings across multiple quarters
   - Compare workload estimates between different teaching styles
   - Identify the most successful student preparation strategies based on review comments
   - Document which professor combinations for ME211/ME212 sequence lead to better student outcomes

This approach helps them create a valuable resource that combines quantitative data with insights, helping future students make informed decisions about their academics.