# Feature: EP-200 日常健康管理
# 目的: 讓病患可以方便地記錄每日健康狀況，並獲得回饋。
# 對應 PRD: [Link to ../product_requirements_document.md#史詩-ep-200-日常健康管理]

@patient @daily-log @sprint-2
Feature: Daily Health Management

  Background:
    Given I am a registered and logged-in patient with ID "patient-001"
    And I have accessed the Daily Log LIFF page

  @happy-path
  Scenario: US-201 Patient submits a complete daily log for the first time today
    Given I have not submitted a daily log for today
    When I toggle "medication_taken" to "Yes"
    And I enter "water_intake" as "1500"
    And I enter "exercise_duration" as "30"
    And I enter "cigarettes_smoked" as "0"
    And I submit the daily log
    Then a new daily log entry for "patient-001" for today should be saved to the database
    And the entry should contain medication_taken=true, water_intake=1500, exercise_duration=30, cigarettes_smoked=0
    And I should see a confirmation message "Great job! Keep it up. 💪"
    And the system should trigger a risk score recalculation for "patient-001"

  @happy-path
  Scenario: US-201 Patient updates their daily log within the same day
    Given I have already submitted a daily log for today with exercise_duration as "15"
    When I access the Daily Log LIFF page again
    And I update the "exercise_duration" to "35"
    And I submit the daily log
    Then the existing daily log entry for "patient-001" for today should be updated in the database
    And the entry's exercise_duration should now be "35"
    And I should see a confirmation message "Your log has been updated!"

  @sad-path
  Scenario Outline: US-201 Patient submits a daily log with invalid data
    Given I have not submitted a daily log for today
    When I enter "<field>" with "<invalid_value>"
    And I submit the daily log
    Then the submission should fail
    And I should see an error message "<error_message>"

    Examples:
      | field               | invalid_value | error_message                                |
      | water_intake        | -100          | "Water intake cannot be negative."           |
      | exercise_duration   | "abc"         | "Exercise duration must be a number."        |
      | cigarettes_smoked   | -1            | "Cigarette count cannot be negative."        |

  @sad-path
  Scenario: US-201 Patient submits an incomplete daily log
    Given I have not submitted a daily log for today
    When I enter "water_intake" as "1500"
    And I leave "medication_taken" unanswered
    And I submit the daily log
    Then the submission should fail
    And I should see an error message "Please answer all required questions."

@patient @trends @sprint-3
Feature: Health Trends Visualization

  Background:
    Given I am a registered and logged-in patient with ID "patient-001"
    And I have submitted daily logs for the past 14 days
    And I am on the "Health Trends" LIFF page

  @happy-path
  Scenario: US-202 Patient views their 7-day health trends
    When I view the "Last 7 Days" trend chart
    Then I should see a line chart displaying data for the last 7 days
    And the chart should include series for "Medication Adherence", "Water Intake", and "Exercise Duration"
    And I should see a summary stating "You've met your goals on 5 out of 7 days."
    And I should see a comparison metric "Water intake is up 15% from last week."

  @edge-case
  Scenario: US-202 Patient views health trends with no data
    Given I am a new registered patient with ID "patient-new"
    And I have submitted no daily logs
    When I view the "Last 7 Days" trend chart
    Then I should see a message "Not enough data to display trends. Start by submitting your daily log!"
    And the chart area should be empty

  @happy-path @sprint-4
  Scenario: US-202 Patient views their 30-day health trends
    Given I have submitted daily logs for the past 30 days
    When I select the "Last 30 Days" view
    Then I should see a line chart displaying data for the last 30 days
    And the chart should include series for "Medication Adherence", "Water Intake", and "Exercise Duration"
