# Example User Flows

## 1. The Transfer Student's Course Planning Journey

Maya is a transfer student who needs to efficiently plan her upcoming quarters. She wants to maximize her chances of success while managing her workload carefully across multiple engineering courses.

First, Maya calls GET `/search/class/?area=B2&sort_col=workload&sort_order=asc` to find all engineering foundation courses, sorted by workload. She identifies three crucial courses: ME211, ME212, and CE201.

For each course, Maya:

1. Calls GET `/courses/{id}/aggregates` to understand the overall picture:

   - ME211: 3.8/5 rating, 15hrs/week average workload
   - ME212: 4.1/5 rating, 12hrs/week average workload
   - CE201: 3.2/5 rating, 18hrs/week average workload

2. Uses GET `/search/class/{course_id}` for each course to find professors teaching next quarter:

   - ME211: Prof. Hall and Prof. Johnson
   - ME212: Prof. Williams
   - CE201: Prof. Chen and Prof. Rodriguez

3. Calls GET `/professors/{id}` for each professor to deep dive into their teaching styles and student experiences

After thorough research, Maya discovers that Prof. Hall (ME211) and Prof. Williams (ME212) have complementary teaching styles that would work well together. She also notices some concerning reviews about Prof. Chen's CE201 class.

Being a diligent student, Maya:

1. Submits a new review for a previous professor via POST `/reviews` with detailed feedback about their teaching style
2. Reports an inappropriate review using POST `/reviews/:id/report` that contained personal attacks against Prof. Chen
3. Helps improve the system by adding a missing professor using POST `/professors` for a new Engineering faculty member

## 2. The Department Chair's Curriculum Review

Dr. Thompson, the Engineering department chair, needs to evaluate course effectiveness and teaching quality across the department. She uses Reveel to gather comprehensive data for the annual department review.

Her investigation flow:

1. First, she calls GET `/search/class/?department=ME` to list all Mechanical Engineering courses.

2. For each core course, she calls GET `/courses/{id}/aggregates` to analyze:

   - Overall course performance
   - Difficulty trends
   - Workload distribution
   - Common student feedback themes

3. She notices unusually high difficulty ratings in ME304 and investigates deeper:

   - Calls GET `/search/class/ME304` to see all professors who taught it
   - Uses GET `/professors/{id}` for each professor to analyze individual teaching effectiveness
   - Discovers a significant disparity in student success rates between professors

4. Dr. Thompson identifies areas for improvement:
   - Adds new professors to the system via POST `/professors` for recent hires
   - Submits detailed course context via POST `/courses` for a new experimental course
   - Reviews and reports outdated information using POST `/reviews/:id/report`

## 3. Student Course Guide Project

Some anonymous person decides to create a guide for new students. They uses Reveel's API to gather and verify information across multiple courses and professors.

The research process:

1. They start broad with GET `/search/class/?sort_col=rating&sort_order=desc` to identify the most highly-rated courses.

2. For each department's core courses:

   - Call GET `/courses/{id}/aggregates` to gather statistical data
   - Use GET `/search/class/{course_id}` to find all professors
   - Analyze GET `/professors/{id}` for each professor's teaching history

3. They enhance the database quality by:

   - Adding missing course information via POST `/courses`
   - Creating entries for new professors via POST `/professors`
   - Contributing detailed reviews through POST `/reviews`
   - Reporting outdated or incorrect information using POST `/reviews/:id/report`

4. For the popular "ME212 - Engineering Dynamics" course, they conduct a deep dive:
   - Analyze professor ratings across multiple quarters
   - Compare workload estimates between different teaching styles
   - Identify the most successful student preparation strategies based on review comments
   - Document which professor combinations for ME211/ME212 sequence lead to better student outcomes

This approach helps them create a valuable resource that combines quantitative data with insights, helping future students make informed decisions about their academics.
