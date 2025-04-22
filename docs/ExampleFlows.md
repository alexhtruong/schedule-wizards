# Example User Flows

## 1. Submitting a Course Review Flow

Sarah just finished her CSC101 course with Professor Andrew Smith and wants to share her experience with other students. She decides to submit a review on Reveel to help future students make informed decisions.

First, Sarah searches for her class by calling GET `/search/class/CSC101` to see if it exists in the system. The search shows that while CSC101 exists, Professor Smith hasn't been added to the system yet.

Since Professor Smith isn't in the system, Sarah helps out by:

1. Calling POST `/professors` with Professor Smith's information
2. This creates a new professor entry with ID "xyz456"

Now that both the course and professor exist, Sarah submits her review by calling POST `/reviews` with:

- A difficulty rating of 3/5
- An overall rating of 4/5
- Estimated workload of 5 hours per week
- Tags: ["Engaging", "Tough exams"]
- A detailed comment about the great teaching but tough grading

Sarah's review is now available to help future students make informed decisions about taking CSC101 with Professor Smith.

## 2. Finding the Best Professor for Engineering Dynamics Flow

Mike needs to take ME212 (Engineering Dynamics) next quarter and wants to choose the best professor for his learning style. He uses Reveel to research his options.

First, Mike calls GET `/search/class/ME212` to see all professors who have taught the course. The search returns two professors:

- Sally Cartman
- Ashton Hall

To learn more about Professor Hall, Mike calls GET `/professors/ahall68` and discovers:

- Professor Hall has taught both ME211 and ME212
- Their average difficulty rating is 7/10
- Students typically spend about 9 hours per week on coursework
- Common tags include "Engaging", "Helpful", and "Tough exams"
- Recent reviews mention interesting lectures but challenging exams

Mike reads through the detailed reviews and notices that Professor Hall has a good balance of hands-on projects and theoretical content, which matches his learning style. Based on this research, Mike decides to register for ME212 with Professor Hall next quarter.

## 3. Discovering Hidden Gem GE Courses Flow

Jessica needs to fulfill her C1 GE requirement and wants to find an interesting course that won't overload her schedule. She uses Reveel to explore her options strategically.

First, Jessica calls GET `/search/class/?area=C1&sort_col=rating&sort_order=desc` to see all C1 courses ranked by student ratings. This gives her a sorted list of courses including CSC101, ME212, and CE212 with their overall ratings.

Interested in CSC101's high rating, Jessica:

1. Calls GET `/courses/CSC101/aggregates` to get deeper insights:

   - Average rating: 4.6/5
   - Average difficulty: 2.3/5
   - Average workload: 5.2 hours/week
   - Popular tags suggest interesting readings and approachable professors

2. Calls GET `/search/class/CSC101` to see who teaches it

3. Looking at Professor Alan Turing's stellar reviews (GET `/professor/aturing123`), she finds:
   - Consistently positive feedback
   - Engaging teaching style
   - Reasonable workload of 8-10 hours/week
   - Clear explanations of complex topics

However, Jessica notices a concerning review with inappropriate language. Being a responsible user, she reports it by calling POST `/reviews/rev001/report` with details about the inappropriate content.

Based on her research, Jessica decides to take CSC101 with Professor Turing, confident that she's found a high-quality GE course that won't overwhelm her schedule.
