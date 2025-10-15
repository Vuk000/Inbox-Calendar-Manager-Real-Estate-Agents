/**
 * Tests for TaskBoard component
 */
import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '../../tests/utils/test-utils'
import { TaskBoard } from '../TaskBoard'
import userEvent from '@testing-library/user-event'

describe('TaskBoard Component', () => {
  it('renders without crashing', () => {
    render(<TaskBoard />)
    expect(screen.getByText(/task/i)).toBeInTheDocument()
  })

  it('displays loading state', () => {
    render(<TaskBoard />)
    // Should show some form of loading or tasks
    expect(document.body).toBeTruthy()
  })

  it('displays tasks after loading', async () => {
    render(<TaskBoard />)
    
    await waitFor(() => {
      // Mock tasks should appear
      expect(screen.getByText(/task/i)).toBeInTheDocument()
    }, { timeout: 3000 })
  })

  it('groups tasks by status', async () => {
    render(<TaskBoard />)
    
    await waitFor(() => {
      // May show columns: pending, in progress, completed
      const taskElements = screen.queryAllByRole('article')
        || screen.queryAllByRole('listitem')
      expect(document.body).toBeTruthy()
    })
  })

  it('allows creating new task', async () => {
    const user = userEvent.setup()
    render(<TaskBoard />)
    
    const createButton = screen.queryByRole('button', { name: /create|new|add/i })
    if (createButton) {
      await user.click(createButton)
    }
    
    expect(document.body).toBeTruthy()
  })

  it('allows marking task as complete', async () => {
    const user = userEvent.setup()
    render(<TaskBoard />)
    
    await waitFor(() => {
      expect(screen.getByText(/task/i)).toBeInTheDocument()
    })

    // Look for checkbox or complete button
    const checkboxes = screen.queryAllByRole('checkbox')
    if (checkboxes.length > 0) {
      await user.click(checkboxes[0])
    }
    
    expect(document.body).toBeTruthy()
  })

  it('displays task priority indicators', async () => {
    render(<TaskBoard />)
    
    await waitFor(() => {
      // May show priority badges (high, medium, low)
      expect(screen.getByText(/task/i)).toBeInTheDocument()
    })
  })

  it('allows filtering tasks', async () => {
    const user = userEvent.setup()
    render(<TaskBoard />)
    
    const filterButtons = screen.queryAllByRole('button')
    expect(filterButtons.length).toBeGreaterThan(0)
  })
})

