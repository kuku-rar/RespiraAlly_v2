/**
 * Commitlint Configuration
 * Enforces Conventional Commits specification
 *
 * Format: <type>(<scope>): <subject>
 *
 * Examples:
 *   feat(api): add patient list endpoint
 *   fix(auth): resolve JWT expiry bug
 *   docs(readme): update installation guide
 */

module.exports = {
  extends: ['@commitlint/config-conventional'],

  // Custom rules
  rules: {
    // Type enum: allowed commit types
    'type-enum': [
      2,
      'always',
      [
        'feat',      // New feature
        'fix',       // Bug fix
        'docs',      // Documentation only changes
        'style',     // Code style changes (formatting, no logic change)
        'refactor',  // Code refactoring
        'perf',      // Performance improvements
        'test',      // Adding or updating tests
        'build',     // Changes to build system or dependencies
        'ci',        // CI/CD configuration changes
        'chore',     // Maintenance tasks
        'revert',    // Revert a previous commit
      ],
    ],

    // Type case: lowercase only
    'type-case': [2, 'always', 'lower-case'],

    // Type empty: type is required
    'type-empty': [2, 'never'],

    // Scope case: lowercase with dash allowed
    'scope-case': [2, 'always', 'lower-case'],

    // Scope enum: optional, but if provided must be from this list
    'scope-enum': [
      1,
      'always',
      [
        'api',        // Backend API changes
        'auth',       // Authentication/Authorization
        'db',         // Database changes
        'frontend',   // Frontend changes (general)
        'dashboard',  // Next.js Dashboard
        'liff',       // LINE LIFF app
        'ai',         // AI/ML components
        'rag',        // RAG system
        'worker',     // Background workers
        'ci',         // CI/CD
        'docker',     // Docker/Deployment
        'docs',       // Documentation
        'deps',       // Dependencies
        'config',     // Configuration
        'test',       // Testing
      ],
    ],

    // Subject case: sentence-case or lower-case
    'subject-case': [2, 'never', ['upper-case', 'pascal-case', 'start-case']],

    // Subject empty: subject is required
    'subject-empty': [2, 'never'],

    // Subject full stop: no period at the end
    'subject-full-stop': [2, 'never', '.'],

    // Subject max length: 72 characters
    'subject-max-length': [2, 'always', 72],

    // Body leading blank: blank line before body
    'body-leading-blank': [2, 'always'],

    // Body max line length: 100 characters per line
    'body-max-line-length': [2, 'always', 100],

    // Footer leading blank: blank line before footer
    'footer-leading-blank': [2, 'always'],

    // Header max length: 100 characters total
    'header-max-length': [2, 'always', 100],
  },

  // Custom prompt messages
  prompt: {
    messages: {
      skip: ':skip',
      max: 'upper %d chars',
      min: '%d chars at least',
      emptyWarning: 'can not be empty',
      upperLimitWarning: 'over limit',
      lowerLimitWarning: 'below limit',
    },
    questions: {
      type: {
        description: 'Select the type of change that you\'re committing:',
        enum: {
          feat: {
            description: 'A new feature',
            title: 'Features',
            emoji: '✨',
          },
          fix: {
            description: 'A bug fix',
            title: 'Bug Fixes',
            emoji: '🐛',
          },
          docs: {
            description: 'Documentation only changes',
            title: 'Documentation',
            emoji: '📝',
          },
          style: {
            description: 'Code style changes (formatting, no logic change)',
            title: 'Styles',
            emoji: '🎨',
          },
          refactor: {
            description: 'A code change that neither fixes a bug nor adds a feature',
            title: 'Code Refactoring',
            emoji: '♻️',
          },
          perf: {
            description: 'A code change that improves performance',
            title: 'Performance Improvements',
            emoji: '⚡',
          },
          test: {
            description: 'Adding missing tests or correcting existing tests',
            title: 'Tests',
            emoji: '✅',
          },
          build: {
            description: 'Changes that affect the build system or external dependencies',
            title: 'Builds',
            emoji: '🏗️',
          },
          ci: {
            description: 'Changes to our CI configuration files and scripts',
            title: 'Continuous Integrations',
            emoji: '🔧',
          },
          chore: {
            description: 'Other changes that don\'t modify src or test files',
            title: 'Chores',
            emoji: '🔨',
          },
          revert: {
            description: 'Reverts a previous commit',
            title: 'Reverts',
            emoji: '⏪',
          },
        },
      },
      scope: {
        description: 'What is the scope of this change (e.g., api, auth, frontend)',
      },
      subject: {
        description: 'Write a short, imperative tense description of the change',
      },
      body: {
        description: 'Provide a longer description of the change',
      },
      isBreaking: {
        description: 'Are there any breaking changes?',
      },
      breakingBody: {
        description: 'A BREAKING CHANGE commit requires a body. Please enter a longer description',
      },
      breaking: {
        description: 'Describe the breaking changes',
      },
      isIssueAffected: {
        description: 'Does this change affect any open issues?',
      },
      issuesBody: {
        description: 'If issues are closed, the commit requires a body. Please enter a longer description',
      },
      issues: {
        description: 'Add issue references (e.g., "fix #123", "re #123")',
      },
    },
  },
};
