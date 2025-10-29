import { Link } from 'react-router-dom'
import { 
  EnvelopeIcon, 
  ChatBubbleLeftIcon, 
  ChartBarIcon,
  SparklesIcon,
  ArrowRightIcon
} from '@heroicons/react/24/outline'

export default function LandingPage() {
  return (
    <div className="min-h-screen bg-gradient-to-br from-gray-900 via-gray-800 to-gray-900">
      {/* Navigation */}
      <nav className="bg-gray-900/50 backdrop-blur-sm border-b border-gray-700">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8">
          <div className="flex justify-between items-center h-16">
            <div className="flex items-center">
              <SparklesIcon className="h-8 w-8 text-blue-500" />
              <span className="ml-2 text-xl font-bold text-white">AgentFlow</span>
            </div>
            <div className="flex items-center space-x-4">
              <Link to="/login" className="text-gray-300 hover:text-white transition-colors">
                Login
              </Link>
              <Link 
                to="/register" 
                className="bg-blue-600 hover:bg-blue-700 text-white px-4 py-2 rounded-lg transition-colors"
              >
                Get Started Free
              </Link>
            </div>
          </div>
        </div>
      </nav>

      {/* Hero Section */}
      <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-20">
        <div className="text-center">
          <h1 className="text-5xl md:text-6xl font-bold text-white mb-6">
            Your Real Estate
            <br />
            <span className="text-blue-500">Command Center</span>
          </h1>
          <p className="text-xl text-gray-300 mb-8 max-w-3xl mx-auto">
            Intelligent inbox management, unified timeline, and AI-powered insights 
            for real estate agents who refuse to settle for chaos.
          </p>
          <div className="flex justify-center space-x-4">
            <Link 
              to="/register" 
              className="bg-blue-600 hover:bg-blue-700 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors flex items-center"
            >
              Start Free Trial
              <ArrowRightIcon className="ml-2 h-5 w-5" />
            </Link>
            <Link 
              to="/login" 
              className="bg-gray-700 hover:bg-gray-600 text-white px-8 py-4 rounded-lg text-lg font-semibold transition-colors"
            >
              Login
            </Link>
          </div>
        </div>

        {/* Features Grid */}
        <div className="mt-24 grid grid-cols-1 md:grid-cols-3 gap-8">
          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-blue-500 transition-colors">
            <div className="bg-blue-500/10 rounded-lg p-3 w-fit mb-4">
              <EnvelopeIcon className="h-8 w-8 text-blue-500" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">Unified Timeline</h3>
            <p className="text-gray-400">
              Every email, text, call, and note with a contact in one beautiful chronological view.
            </p>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-blue-500 transition-colors">
            <div className="bg-blue-500/10 rounded-lg p-3 w-fit mb-4">
              <SparklesIcon className="h-8 w-8 text-blue-500" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">AI-Powered Insights</h3>
            <p className="text-gray-400">
              Trustworthy AI that suggests actions but always keeps you in control.
            </p>
          </div>

          <div className="bg-gray-800/50 backdrop-blur-sm border border-gray-700 rounded-xl p-6 hover:border-blue-500 transition-colors">
            <div className="bg-blue-500/10 rounded-lg p-3 w-fit mb-4">
              <ChatBubbleLeftIcon className="h-8 w-8 text-blue-500" />
            </div>
            <h3 className="text-xl font-semibold text-white mb-2">All-in-One Platform</h3>
            <p className="text-gray-400">
              Email, contacts, tasks, and transactions all in one beautiful interface.
            </p>
          </div>
        </div>

        {/* CTA Section */}
        <div className="mt-24 bg-gradient-to-r from-blue-600 to-blue-700 rounded-2xl p-12 text-center">
          <h2 className="text-3xl font-bold text-white mb-4">
            Ready to take control of your inbox?
          </h2>
          <p className="text-blue-100 text-lg mb-8">
            Join AgentFlow and experience the command center agents actually love.
          </p>
          <Link 
            to="/register" 
            className="bg-white hover:bg-gray-100 text-blue-600 px-8 py-4 rounded-lg text-lg font-semibold transition-colors inline-flex items-center"
          >
            Get Started Free
            <ArrowRightIcon className="ml-2 h-5 w-5" />
          </Link>
        </div>
      </div>

      {/* Footer */}
      <footer className="border-t border-gray-800 mt-20">
        <div className="max-w-7xl mx-auto px-4 sm:px-6 lg:px-8 py-8">
          <p className="text-center text-gray-500">
            © 2025 AgentFlow. The CRM agents actually love.
          </p>
        </div>
      </footer>
    </div>
  )
}

