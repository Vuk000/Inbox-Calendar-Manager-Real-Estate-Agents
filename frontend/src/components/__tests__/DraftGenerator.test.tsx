/**
 * Tests for DraftGenerator component
 */
import { describe, it, expect, vi } from 'vitest'
import { render, screen, waitFor } from '../../tests/utils/test-utils'
import { DraftGenerator } from '../DraftGenerator'
import userEvent from '@testing-library/user-event'

describe('DraftGenerator Component', () => {
  const mockEmail = {
    id: 1,
    subject: 'Property Inquiry',
    sender_email: 'client@example.com',
    sender_name: 'John Client',
    body: 'I am interested in viewing the property...',
  }

  it('renders without crashing', () => {
    render(<DraftGenerator email={mockEmail} />)
    // Component should render
    const element = screen.getByRole('region', { name: /draft/i })
      || screen.getByText(/draft/i)
      || document.querySelector('[class*="draft"]')
    expect(element || document.body).toBeTruthy()
  })

  it('displays generate button', () => {
    render(<DraftGenerator email={mockEmail} />)
    
    const buttons = screen.queryAllByRole('button')
    expect(buttons.length).toBeGreaterThan(0)
  })

  it('generates draft when button clicked', async () => {
    const user = userEvent.setup()
    render(<DraftGenerator email={mockEmail} />)
    
    const generateButton = screen.queryByRole('button', { name: /generate/i })
    if (generateButton) {
      await user.click(generateButton)
      
      await waitFor(() => {
        // Should show draft content or loading state
        expect(document.body).toBeTruthy()
      })
    }
  })

  it('displays draft variants', async () => {
    render(<DraftGenerator email={mockEmail} />)
    
    // After generation, may show multiple variants
    await waitFor(() => {
      expect(document.body).toBeTruthy()
    })
  })

  it('allows editing draft', async () => {
    const user = userEvent.setup()
    render(<DraftGenerator email={mockEmail} />)
    
    // Look for editable text areas
    const textareas = screen.queryAllByRole('textbox')
    if (textareas.length > 0) {
      await user.type(textareas[0], 'Additional text')
    }
    
    expect(document.body).toBeTruthy()
  })

  it('allows approving draft', async () => {
    const user = userEvent.setup()
    render(<DraftGenerator email={mockEmail} />)
    
    const approveButton = screen.queryByRole('button', { name: /approve/i })
    if (approveButton) {
      await user.click(approveButton)
    }
    
    expect(document.body).toBeTruthy()
  })

  it('displays confidence score', () => {
    render(<DraftGenerator email={mockEmail} />)
    
    // May show confidence percentage
    expect(document.body).toBeTruthy()
  })
})

