# Feature: EP-100 病患註冊與認證
# 目的: 為病患與治療師提供安全可靠的身份驗證機制。
# 對應 PRD: [Link to ../product_requirements_document.md#史詩-ep-100-病患註冊與認證]

@patient @auth
Feature: Patient Registration and Authentication

  Background:
    Given the system is running
    And the LINE LIFF application is properly configured

  @happy-path @sprint-1
  Scenario: US-101 A new patient registers successfully through LINE
    Given I am a new patient accessing the registration LIFF page
    And the system can retrieve my LINE User ID "U1234567890"
    When I fill in "name" with "王大明"
    And I select "gender" as "male"
    And I fill in "birth_date" with "1955-10-20"
    And I submit the registration form
    Then a new patient record for "王大明" should be created in the database
    And the patient record should be linked to LINE User ID "U1234567890"
    And I should be shown a "Registration Successful" message
    And the system should set the patient's default Rich Menu

  @sad-path
  Scenario: US-101 A patient tries to register with an already existing LINE ID
    Given a patient with LINE User ID "U1234567890" already exists
    When I, as a user with LINE User ID "U1234567890", access the registration page
    And I submit the registration form
    Then I should be shown an error message "This LINE account is already registered."
    And no new patient record should be created

  @sad-path
  Scenario Outline: US-101 A new patient tries to register with invalid or incomplete data
    Given I am a new patient accessing the registration LIFF page
    When I fill in "<field>" with "<value>"
    And I submit the registration form
    Then I should be shown an error message "<error_message>"
    And no new patient record should be created

    Examples:
      | field        | value        | error_message                          |
      | name         | ""           | "Name cannot be empty."                |
      | name         | "John123"    | "Name contains invalid characters."    |
      | birth_date   | "2077-01-01" | "Birth date cannot be in the future."  |
      | gender       | "other"      | "Please select a valid gender."        |

@therapist @auth
Feature: Therapist Authentication

  Background:
    Given I am on the therapist dashboard login page "/dashboard/login"
    And a therapist account with email "therapist@respira.ally" and password "ValidPassword123" exists

  @happy-path @sprint-1
  Scenario: US-102 A therapist logs in successfully with correct credentials
    When I fill in "email" with "therapist@respira.ally"
    And I fill in "password" with "ValidPassword123"
    And I click the "Login" button
    Then I should be redirected to the "/dashboard" page
    And the system should issue a valid JWT token with an 8-hour expiration
    And I should see a welcome message "Welcome, therapist!"

  @sad-path
  Scenario: US-102 A therapist fails to log in with an incorrect password
    When I fill in "email" with "therapist@respira.ally"
    And I fill in "password" with "WrongPassword"
    And I click the "Login" button
    Then I should remain on the "/dashboard/login" page
    And I should see an error message "Invalid email or password."

  @sad-path
  Scenario: US-102 A user tries to log in with a non-existent email
    When I fill in "email" with "nonexistent@respira.ally"
    And I fill in "password" with "any_password"
    And I click the "Login" button
    Then I should remain on the "/dashboard/login" page
    And I should see an error message "Invalid email or password."

  @edge-case
  Scenario Outline: US-102 A therapist fails to log in multiple times and gets locked out
    Given the therapist "therapist@respira.ally" has had <login_attempts> failed login attempts
    When I fill in "email" with "therapist@respira.ally"
    And I fill in "password" with "WrongPassword"
    And I click the "Login" button
    Then I should see an error message "<error_message>"

    Examples:
      | login_attempts | error_message                                        |
      | 2              | "Invalid email or password. 1 attempt remaining."    |
      | 3              | "Account locked due to too many failed login attempts. Please try again in 15 minutes." |

  @edge-case
  Scenario: US-102 A locked-out therapist tries to log in again
    Given a therapist account "therapist@respira.ally" is currently locked out
    When I fill in "email" with "therapist@respira.ally"
    And I fill in "password" with "ValidPassword123"
    And I click the "Login" button
    Then I should see an error message "Account locked. Please try again in 10 minutes."
