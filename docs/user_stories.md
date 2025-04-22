## 12 User Stories: 
- As a student at Cal Poly, I want to see what professor I should take for a specific class so that I can get a better grade and have a better experience. 
- As a student at Cal Poly, I want to see the year and major of the student leaving a review for a class, as well as what grade they received and other reviews they’ve left, so that I know if the review is from a straight A student or from someone who just likes to complain. 
- As a student at Cal Poly, I want to be able to leave a review for the class so others can see my thoughts on the class, that way I can help other students who have to take the class in the future. 
- As a student at Cal Poly, I want to be able to rate my professors so others can see which professors to take and which not to take. 
- As a Cal Poly student I want to balance out my quarters based on the relative difficulty of the classes, so that I don’t get too many quarters where I feel overwhelmed. 
- As a cal poly student i want to see what GE classes and professors people recommend the most, that way I can pick the best “hidden gems” among a long list of GE classes I have to take. 
- As a cal poly student I want to be able to see what classes are best grouped/ taken in the same quarter depending on my major. 
- As a student, I want to bookmark or save classes and professors I'm interested in so I can quickly return to them when planning my schedule.
- As a student I want to write why I recommend taking certain classes in the order I took them. 
- As a student I want to report which classes I wish I took before taking a class I recently took, so that way others can plan which classes to take in advance. 
- As a Cal Poly student, I want to filter class reviews by major so I can see how students with similar academic paths experienced the class.
- As a student, I want to be notified when a highly-rated professor is teaching a course I need, so I can plan my schedule accordingly.


## 12 Exceptions: 
- If a user tries to rate a class/professor without including a review, then the API should request extra input
- If the user tries to leave multiple reviews for the same professor and class combo, the API should stop them to prevent one user making too many reviews
- If a student tries to submit a review for a course code or professor that isn’t in the system yet (for example a typo or a newly added course that hasn't been entered into the database), the API shouldn’t just fail silently.
- If a user enters a professor's name that doesn’t match any existing faculty, the API should suggest possible matches or alert 'professor not found'.
- If a review includes offensive or inappropriate language, the system should flag it for moderation before posting. 
- If a student tries to rate a class they haven’t marked as taken in their profile, the system should prompt for verification. 
- If a user leaves a review with fewer than a minimum number of characters, the API should prompt for more detailed feedback.
- If a student submits a review but leaves out required fields like difficulty rating or weekly workload, the form will throw an error message stating to fill in the required fields.
- If the user fills out a review, submits, but the database is down or the server errors out, the user should see a friendly error.
- If a student tries to access features without being logged in, the system should redirect them to the login page. 
- If the user selects incompatible filters like searching for a professor who teaches a course outside their department,  the API should return an empty result with a helpful message. 
- If a user updates a review after a set deadline , for example 30 days after the original review was made, the API should require justification for the edit or block changes.

