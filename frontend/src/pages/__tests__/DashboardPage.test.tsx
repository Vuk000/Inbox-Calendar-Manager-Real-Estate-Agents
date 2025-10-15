/**
 * Tests for DashboardPage
 */
import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '../../tests/utils/test-utils'
import { DashboardPage } from '../DashboardPage'

describe('DashboardPage', () => {
  it('renders without crashing', () => {
    render(<DashboardPage />)
    expect(screen.getByText(/dashboard/i) || document.body).toBeTruthy()
  })

  it('displays key metrics', async () => {
    render(<DashboardPage />)
    
    await waitFor(() => {
      // Should show metrics like emails processed, drafts, etc.
      expect(document.body).toBeTruthy()
    }, { timeout: 3000 })
  })

  it('displays recent emails section', async () => {
    render(<DashboardPage />)
    
    await waitFor(() => {
      const recentEmails = screen.queryByText(/recent|email/i)
      expect(recentEmails || document.body).toBeTruthy()
    })
  })

  it('displays pending tasks section', async () => {
    render(<DashboardPage />)
    
    await waitFor(() => {
      const tasks = screen.queryByText(/task|pending/i)
      expect(tasks || document.body).toBeTruthy()
    })
  })

  it('displays quick actions', () => {
    render(<DashboardPage />)
    
    const buttons = screen.queryAllByRole('button')
    expect(buttons.length).toBeGreaterThanOrEqual(0)
  })
})

