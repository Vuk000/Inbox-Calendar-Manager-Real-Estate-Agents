/**
 * MSW (Mock Service Worker) server setup
 * Mocks API calls during testing
 */
import { setupServer } from 'msw/node'
import { handlers } from './handlers'

// Create MSW server with our request handlers
export const server = setupServer(...handlers)

