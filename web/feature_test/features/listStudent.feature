Feature: As a user I want to see the student list
    
    Scenario: No student in course 2012-1
        Given Teacher "teacher" exists with password "teacher"
          And course "2012-1" exists
          And a shift with name "tarde" and description "horario" in the course "2012-1"
          And there are no student in course "2012-1" shift "tarde" 
          And I log in as "teacher" "teacher"
         When I click the button "detail2012-1"
          And I click the button "studentlisttarde"
         Then I should see "There are yet no Students"
    
	Scenario: Student in course 2012-1 order by name
        Given Teacher "teacher" exists with password "teacher"
          And I log in as "teacher" "teacher"
          And course "2012-1" exists
          And a shift with name "tarde" and description "horario" in the course "2012-1"
          And Student "martin" exists with password "martin"
          And Student "anibal" exists with password "anibal"
          And student "martin" exists in course "2012-1" and in shift "tarde"
          And student "anibal" exists in course "2012-1" and in shift "tarde"
         when I am in the detail page of course "2012-1"
          And I click the button "studentlisttarde"
         Then I should see "anibal" before "martin" 