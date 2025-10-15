import { useState, useEffect } from 'react'
import { MicrophoneIcon, StopIcon } from '@heroicons/react/24/solid'
import toast from 'react-hot-toast'

interface VoiceInterfaceProps {
  onCommand?: (command: string) => void
  onDictation?: (text: string) => void
  mode?: 'command' | 'dictation'
}

export default function VoiceInterface({ 
  onCommand, 
  onDictation, 
  mode = 'command' 
}: VoiceInterfaceProps) {
  const [isListening, setIsListening] = useState(false)
  const [transcript, setTranscript] = useState('')
  const [recognition, setRecognition] = useState<any>(null)

  useEffect(() => {
    // Check if browser supports Speech Recognition
    const SpeechRecognition = (window as any).SpeechRecognition || (window as any).webkitSpeechRecognition
    
    if (!SpeechRecognition) {
      console.warn('Speech Recognition not supported in this browser')
      return
    }

    // Initialize speech recognition
    const recognitionInstance = new SpeechRecognition()
    recognitionInstance.continuous = mode === 'dictation'
    recognitionInstance.interimResults = true
    recognitionInstance.lang = 'en-US'

    recognitionInstance.onresult = (event: any) => {
      let finalTranscript = ''
      let interimTranscript = ''

      for (let i = event.resultIndex; i < event.results.length; i++) {
        const transcript = event.results[i][0].transcript
        if (event.results[i].isFinal) {
          finalTranscript += transcript + ' '
        } else {
          interimTranscript += transcript
        }
      }

      if (finalTranscript) {
        setTranscript(prev => prev + finalTranscript)
        
        if (mode === 'command') {
          // Process as command
          processVoiceCommand(finalTranscript.trim())
        } else {
          // Process as dictation
          onDictation?.(finalTranscript.trim())
        }
      } else {
        setTranscript(interimTranscript)
      }
    }

    recognitionInstance.onerror = (event: any) => {
      console.error('Speech recognition error:', event.error)
      setIsListening(false)
      
      if (event.error === 'not-allowed') {
        toast.error('Microphone permission denied')
      } else {
        toast.error('Voice recognition error')
      }
    }

    recognitionInstance.onend = () => {
      setIsListening(false)
    }

    setRecognition(recognitionInstance)

    return () => {
      if (recognitionInstance) {
        recognitionInstance.stop()
      }
    }
  }, [mode])

  const processVoiceCommand = (command: string) => {
    const commandLower = command.toLowerCase()
    
    // Parse voice commands
    if (commandLower.includes('show urgent') || commandLower.includes('urgent email')) {
      onCommand?.('show_urgent')
      toast.success('Showing urgent emails')
    } else if (commandLower.includes('show lead')) {
      onCommand?.('show_leads')
      toast.success('Showing leads')
    } else if (commandLower.includes('show offer')) {
      onCommand?.('show_offers')
      toast.success('Showing offers')
    } else if (commandLower.includes('draft reply')) {
      onCommand?.('generate_draft')
      toast.success('Generating draft')
    } else if (commandLower.includes('schedule')) {
      onCommand?.('schedule')
      toast.success('Opening scheduler')
    } else {
      onCommand?.(command)
    }
  }

  const toggleListening = () => {
    if (!recognition) {
      toast.error('Voice recognition not available in this browser')
      return
    }

    if (isListening) {
      recognition.stop()
      setIsListening(false)
    } else {
      setTranscript('')
      recognition.start()
      setIsListening(true)
      toast.success(mode === 'command' ? 'Listening for command...' : 'Dictation started')
    }
  }

  return (
    <div className="fixed bottom-8 right-8 z-50">
      <button
        onClick={toggleListening}
        className={`
          p-4 rounded-full shadow-lg transition-all transform hover:scale-110
          ${isListening 
            ? 'bg-danger-500 hover:bg-danger-600 animate-pulse' 
            : 'bg-primary-600 hover:bg-primary-700'
          }
        `}
        title={mode === 'command' ? 'Voice Commands' : 'Voice Dictation'}
      >
        {isListening ? (
          <StopIcon className="h-6 w-6 text-white" />
        ) : (
          <MicrophoneIcon className="h-6 w-6 text-white" />
        )}
      </button>

      {/* Transcript display */}
      {isListening && transcript && (
        <div className="absolute bottom-20 right-0 bg-white rounded-lg shadow-xl border border-gray-200 p-4 max-w-md">
          <p className="text-sm text-gray-600 mb-1">
            {mode === 'command' ? 'Listening...' : 'Dictating...'}
          </p>
          <p className="text-gray-900">{transcript}</p>
        </div>
      )}
    </div>
  )
}

