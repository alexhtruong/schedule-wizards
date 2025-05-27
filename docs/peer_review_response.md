Issue: There are two Professor and Course base model classes, one in models.py and the other in reviews.py. The one in models has an extra attribute: courses. Having multiple professor classes opens the door to ambiguity and inconsistent data being required if the wrong Professor class is used.

Response: Refactored classes so there shouldn't be any repeats

Issue: Your create_department route checks if the department exists, and then inserts it into the if it doesn’t. If concurrent duplicate calls were made to this route, it could be possible for both select statements to occur simultaneously, and then insert duplicate department entries. You can fix this with a unique constraint on name in the db, and simply check for conflict when attempting to from the route.

Response: Added a check for existing departments and schools with a try/catch block. This way the code won't potentially miss any checks. Also added a composite keys for name to school id and abbrev to school id

Issue: Create_school - same problem as create_department above. Add unique constraint on name and check for conflict on insert.

Response: Added another try/catch block to catch creation of departments at any time. Also added unique constraints on name to school id

Issue: Get_professor_details - The error message for missing reviews doesn’t handle status code convention. 400 indicates client error but in this case the client is not at fault. I think some other status codes don’t follow convention as well

Response: Fixed status codes to follow convention

Issue: Get_professor_details - In the reviews_result query, professor id is fetched. This is unnecessary as professor id is already known from prof_result

Response: removed unnecessary query

Issue: Create_professor - duplicate professors can be created if executed concurrently. If there’s a database constraint on name, the case with conflict isn’t necessarily handled gracefully by this route.

Response: added try/catch block for potential duplication

Issue: Create_review- - you update statistics columns on every call to this route. This keeps these entries accurate, but makes create_review more complicated and slower. An alternative would be to update these columns on an interval – eg once per day – using scheduled jobs.

Response: Set up a cron job running daily that hits a newly made endpoint specifically for updating prof and course statistics 

Issue: Get_course_reviews - For the case where no reviews are found, it might be better to return an empty list and return 200 ok status.

Response: Now returns empty list


Issue: Get_course_reviews - if there are a LOT of reviews for a course, pagination could come in handy to avoid large responses form this route

Response: Consolidated core logic and refactored the endpoints so that they call the same function, but pass in an argument specifying if they are requesting course or professor reviews


Issue: There are also multiple Review classes - one in professors.py, one in reviews.py

Response: (referring to earlier response) - Already refactored classes into one file and there are no longer duplicates


Issue: When getting course statistics, the precise repeating decimal values can make it a bit difficult to read. Rounding to the nearest int or half int could help solve this problem, and make it more akin to a 5-star scale

Response: Added python round() function to round to one decimal places 


Issue: Your professor schema includes aggregated columns such as avg_workload and avg_rating. If it’s important that these are accurate, it may be simpler to drop the columns and calculate averages when the statistics route is called. If accuracy isn’t paramount, it could be easiest to include these columns and update them on some interval.

Response: Already set up cronjob for updating statistics


Issue: In the departments table, it might be safer to add a unique constraint for the name and abbrev cols to avoid duplicate department entries.

Response: Already made a unique constraint


Issue: Since departments are a part of schools, it may make more sense to include department routes under school routes rather than having them completely separate. Eg /schools/departments

Response: Migrated departments route to schools route


Issue: Tags seem to be very professor-specific so including top tags in the get_course_aggregates response doesn’t entirely make sense.

Response: Remove tags from get_course_aggregates class and response


Issue: There is no way to list schools from the site. It is difficult to add a department since you cannot find your school’s id.

Response: Added a GET endpoint for listing departments and schools


Issue: A class’s course code is only available to users through the reviews routes. Only course id is returned on course search. Because of this, it is more difficult to use the get course, get course professors, or get coarse aggregates for courses that you found from a call to the list courses route.

Response: Added course code to Course class and any endpoints that use Course as a response


Issue: It could be useful to users to be able to get a professor’s average rating over the courses they have taught as well, not just course average rating.

Response: Added prof avg rating to response when hitting the GET endpoint for a specific professor


Issue: Postgres supports enumerated types. These could be used in the review.term column to avoid incorrect term names

Response: Added server-side regex validation for terms


Issue: Generally it might be helpful to store the time/date when reviews were created at.

Response: Don't really see a point in doing it when the review term already exists. Extra info doesn't hurt though, I'll agree on that.


Issue: There is no way to distinguish between schools when doing any searches. If this site is just for cal poly you could drop the schools table, or repurpose it into a colleges table to associate departments with a college.

Response: Removing schools table and endpoints, scope feels too large to implement if we have to consider a school for endpoint


Issue: reviews.py: you have a connection execute on a for loop on line 101, condensing to save efficiency is better practice for higher-scale.

Response: Realistically there aren't that many tags in a review so something like this should be fine to keep and not change. The most efficient way involves code thats arguably hard to read. So, I'd rather keep the readable and slightly less optimized code(which still runs in a reasonable time)


Issue: reviews.py: big try blocks like the one on line 80-190 provide a very general but vague way of error handling. I would work to make it more specific about its error handling or logging, because otherwise these 100+ lines are very difficult to debug and the very general definition of catching all exceptions could lead to automatically failing situations with recoverable exceptions.

Response: Not sure what they meant by vague error handling since we print the error in the console. 


Issue: courses.py: “POST /courses” endpoint handles cases where the department doesn’t exist but doesn’t properly address a case where a course already exists. I’m not sure if you have already added/want to add a uniqueness clause to your courses table to prevent duplicate courses. If so, you should also add handling for it in the endpoint, so it doesn’t just return a 500 internal server error

Response: Added try/catch block for catching duplicate courses


Issue: courses.py: “POST /courses” endpoint uses a CourseCreate class instance to pass in values for the new course, one of which is department. However, when referencing course.department to the department table, it checks to see if course.department is equivalent to abbrev. This isn’t very intuitive, considering ‘department’ could just as likely refer to the name or id of the department that I am trying to link. Without knowledge of exactly what this endpoint does and what it is similarly asking for, it is very likely to return errors due to that. Make the CourseCreate class more specific about what it is asking users to input.

Response: Added example inputs for endpoints that have a JSON body so user has a better understanding of how data should be input


Issue: models.py: This is a given, but you should probably add more of your classes to this file; that’s the entire reason you would have something like this. Having Professor and Course here makes sense, but I don’t know why you define a class like Review in reviews.py and import it around from there, instead of defining the Review class in models.py and it being imported with the other two. The classes are too haphazardly spread out across files.

Response: Already moved all classes to models.py

Issue: professors.py: Your NewProfessor class has a property called ‘metadata’, which is an empty dict. I don’t know what this is for, or why it is here. It isn’t referenced in anything.

Response: Removed metadata field, was planning on using at some point but changed our mind


Issue: Creating a new school allows there to be empty strings. Depending on you view it, it might be a good idea to make sure no one can just enter empty strings into the database

Response: Removed school and also implemented input validation for classes as part of earlier issues


Issue: Some files have unused imports. For example, in schools.py, import Course and import Review goes unused. Might be better to remove it, unless you plan to use it in future code

Response: Fixed imports as part of earlier issue

Issue: The sql text in reviews.py is massive. If something goes wrong, it might prove difficult to debug it and find the source of error

Response: Queries were already tested before pushed to production


Issue: In reviews,py, connection is executed multiple times in a for loop. It might be better to execution the connection now, and then do the for loop

Response: Addressed in an earlier issue, don't need to change because its more readable


Issue: In reviews.py, there is a class called ReportCreate that contains variables 'reason' and 'details'. I assume this meant as a way to report professors or schools, but goes unused. Unless this is for some future code or a function your group has chosen to not use anymore

Response: Removed class, was planning on adding another endpoint but realized it was impractical


Issue: A small thing, but when creating a course, I noticed it returned a list of professors, which was empty. Since we are just barely creating a course, there shouldn't be any professors assigned to it yet, so returning that list seems unneeded.

Response: Ignoring - that's why we're returning an empty list. We could also just return null but an empty list will be fine.

Issue: On classes like DepartmentCreate in department.py, it might help to have some validation checks. For example, checks to make sure school id is an int, or limit the abbrev str to only 3 or 4 characters as how schools usually format it

Response: Already added validation checks to classes

Issue: I noticed when creating a course, I can only put in the course code, name and department. But I can see the course table also has columns for avg_workload, avg_rating and department_id, which I am unable to insert data to those columns through the course creation endpoint

Response: Those columns are supposed to be computed, not inserted.


Issue: It would help if you can specify for when creating a new course, that a user needs to use the abbreviated name of the department, rather than the full name.

Response: Added example input to show


Issue: I'm not sure how courses is being sorted when I use the GET courses endpoint. Using desc and asc doesn't seem to change the order of the courses returned. Also, it might be helpful if we can choose how the course list is sorted, like by professor name

Response: It does work?


Issue: When creating a new review, is it really needed for the user to also put in an overall rating? 'Overall' sounds like something the database would handle itself where it takes in all the professor's difficulty rating from different students, then average them to produce the overall rating for the professor.

Response: I think the overall score can be subjective and a result from multiple factors and not just based on the average between the two other scores.


Issue: Similar to creating courses, the professors table as extra columns 'total_reviews', 'avg_difficulty', 'avg_workload', and 'classes_taught' that I am unable to insert values to through the create professor endpoint. If needed, you could create another table that has the all the average values calculated, the total reviews and classes taught summed up that are automatically inserted and/or updated every time a new review or classes is added

Response: As stated before, those are not meant to be inserted.


Issue: Based on your APIspec.md and thinking from the perspective of a user, does the user really need to know the professor's id and course id to create a review for a specific professor? Usually on sites like Rate My Professor, what you need to know is the professor's name and and the course name(which may be the 'abbrev' variable in this case)

Response: We had to adjust some things, so the APIspec isn't up to date.


Issue: You have an example of creating a report, but there is no actual table for submitted reports. If you do start making a report table, I also recommend adding a column that has the professor's id, so that people know who that report was made for

Response: Originally had an idea to be able to report users/reports, but couldn't really think of a good way to do it without user authentication while preventing spamming from one user.

