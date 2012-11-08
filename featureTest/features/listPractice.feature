Feature: As a user I want to see the practice list
    
    Scenario: No practice
        Given Teacher "teacher" exists with password "teacher"
          And there are no practices
    	  And course "2012-1" exists
          And I log in as "teacher" "teacher"
         When I click in the "2012-1" link
         Then I should see "There are yet no Practices"
         
    Scenario: Practices in course 2012-1 order by Dead Line
        Given Teacher "teacher" exists with password "teacher"
    	  And course "2012-1" exists
          And I log in as "teacher" "teacher"
          And practice "TP 1" exists in course "2012-1" with deadline "2012-12-02"
          And practice "TP Intro" exists in course "2012-1" with deadline "2012-12-01"
         when I am in the modifier page of course "2012-1"
         Then I should see "TP Intro" before "TP 1"
         
    Scenario: List Delivery of Practices from home student
        Given Student "martin" exists with password "martin"
    	  And course "2012-1" exists
    	  And practice "TP Intro" exists in course "2012-1" with deadline "2012-12-01"
          And I log in as "martin" "martin"
    	  And student "Martin" exists in course "2012-1"
    	 when I am in the delivery page of practice "TP INTRO"
    	 Then I should see "There are yet no Delivery from this practice"
