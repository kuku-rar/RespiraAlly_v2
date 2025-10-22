/**
 * QuestionCard Component - Survey Question Display with TTS Support
 *
 * Features:
 * - Elderly-friendly large font and high contrast
 * - Emoji + description option buttons
 * - TTS (Text-to-Speech) support
 * - Accessible design (ARIA labels, keyboard navigation)
 *
 * Sprint 3 Task 5.3.2 - Week 6 Day 2
 */

import { type SurveyQuestion, type SurveyOption } from '../../types/survey'

interface QuestionCardProps {
  question: SurveyQuestion
  selectedValue: number | null
  onSelect: (value: number) => void
  onSpeak?: (text: string) => void
  isSpeaking?: boolean
}

export function QuestionCard({
  question,
  selectedValue,
  onSelect,
  onSpeak,
  isSpeaking = false,
}: QuestionCardProps) {
  const handleSpeak = () => {
    if (onSpeak && question.ttsText) {
      onSpeak(question.ttsText)
    }
  }

  return (
    <div className="bg-white rounded-2xl shadow-xl p-6 sm:p-8 border border-gray-200">
      {/* Question Header */}
      <div className="mb-6">
        <div className="flex items-start justify-between gap-4 mb-4">
          <h2 className="text-2xl sm:text-3xl font-bold text-gray-900 leading-snug">
            {question.text}
          </h2>

          {/* TTS Button */}
          {onSpeak && (
            <button
              onClick={handleSpeak}
              disabled={isSpeaking}
              className={`flex-shrink-0 p-3 rounded-full transition-all ${
                isSpeaking
                  ? 'bg-blue-600 text-white scale-110'
                  : 'bg-gray-100 hover:bg-blue-50 text-gray-700'
              }`}
              aria-label="朗讀問題"
              title="朗讀問題"
            >
              <span className="text-2xl" role="img" aria-label="speaker">
                {isSpeaking ? '🔊' : '🔈'}
              </span>
            </button>
          )}
        </div>

        <p className="text-base sm:text-lg text-gray-600">
          請點選最符合您情況的選項
        </p>
      </div>

      {/* Options List */}
      <ul className="space-y-3" role="list">
        {question.options.map((option) => (
          <OptionButton
            key={option.value}
            option={option}
            isSelected={selectedValue === option.value}
            onSelect={() => onSelect(option.value)}
          />
        ))}
      </ul>
    </div>
  )
}

// ============================================================================
// OptionButton Component
// ============================================================================

interface OptionButtonProps {
  option: SurveyOption
  isSelected: boolean
  onSelect: () => void
}

function OptionButton({ option, isSelected, onSelect }: OptionButtonProps) {
  return (
    <li role="listitem">
      <button
        onClick={onSelect}
        className={`
          w-full p-4 sm:p-5 rounded-xl border-2 transition-all
          flex items-center gap-4 text-left
          ${
            isSelected
              ? 'bg-blue-50 border-blue-600 shadow-lg scale-[1.02]'
              : 'bg-gray-50 border-gray-200 hover:bg-blue-50 hover:border-blue-300 hover:shadow-md'
          }
        `}
        aria-label={`分數 ${option.value}：${option.label} ${option.description}`}
        aria-pressed={isSelected}
      >
        {/* Score Circle */}
        <div
          className={`
            flex-shrink-0 w-12 h-12 sm:w-14 sm:h-14 rounded-full
            flex items-center justify-center
            text-2xl sm:text-3xl font-bold
            ${
              isSelected
                ? 'bg-blue-600 text-white'
                : 'bg-blue-100 text-blue-700'
            }
          `}
        >
          {option.value}
        </div>

        {/* Label + Description */}
        <div className="flex-1 min-w-0">
          <div className="text-xl sm:text-2xl font-semibold text-gray-900 leading-tight mb-1">
            {option.label}
          </div>
          {option.description && (
            <div className="text-base sm:text-lg text-gray-600">
              {option.description}
            </div>
          )}
        </div>

        {/* Checkmark for selected option */}
        {isSelected && (
          <div className="flex-shrink-0 text-3xl" role="img" aria-label="已選">
            ✓
          </div>
        )}
      </button>
    </li>
  )
}
