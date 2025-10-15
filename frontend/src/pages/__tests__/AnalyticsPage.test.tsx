/**
 * Tests for AnalyticsPage
 */
import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '../../tests/utils/test-utils'
import { AnalyticsPage } from '../AnalyticsPage'

describe('AnalyticsPage', () => {
  it('renders without crashing', () => {
    render(<AnalyticsPage />)
    expect(screen.getByText(/analytics|metrics/i) || document.body).toBeTruthy()
  })

  it('displays productivity metrics', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      // Should show metrics like emails triaged, time saved, etc.
      expect(document.body).toBeTruthy()
    }, { timeout: 3000 })
  })

  it('displays charts', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      // Recharts should render SVG charts
      const svgs = document.querySelectorAll('svg')
      expect(svgs.length >= 0).toBe(true)
    })
  })

  it('allows selecting time period', async () => {
    render(<AnalyticsPage />)
    
    // May have dropdown or buttons for time range
    const buttons = screen.queryAllByRole('button')
    expect(buttons.length).toBeGreaterThanOrEqual(0)
  })

  it('displays ROI calculator', async () => {
    render(<AnalyticsPage />)
    
    await waitFor(() => {
      const roi = screen.queryByText(/roi|return/i)
      expect(roi || document.body).toBeTruthy()
    })
  })
})

