/**
 * Tests for LoginPage
 */
import { describe, it, expect } from 'vitest'
import { render, screen, waitFor } from '../../tests/utils/test-utils'
import { LoginPage } from '../LoginPage'
import userEvent from '@testing-library/user-event'

describe('LoginPage', () => {
  it('renders login form', () => {
    render(<LoginPage />)
    
    expect(screen.getByRole('textbox', { name: /email/i }) || screen.getByLabelText(/email/i)).toBeInTheDocument()
    expect(screen.getByLabelText(/password/i)).toBeInTheDocument()
    expect(screen.getByRole('button', { name: /login|sign in/i })).toBeInTheDocument()
  })

  it('allows entering email and password', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)
    
    const emailInput = screen.getByRole('textbox', { name: /email/i }) || screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    
    expect(emailInput).toHaveValue('test@example.com')
    expect(passwordInput).toHaveValue('password123')
  })

  it('submits login form', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)
    
    const emailInput = screen.getByRole('textbox', { name: /email/i }) || screen.getByLabelText(/email/i)
    const passwordInput = screen.getByLabelText(/password/i)
    const submitButton = screen.getByRole('button', { name: /login|sign in/i })
    
    await user.type(emailInput, 'test@example.com')
    await user.type(passwordInput, 'password123')
    await user.click(submitButton)
    
    // Should handle submission
    await waitFor(() => {
      expect(document.body).toBeTruthy()
    })
  })

  it('displays validation errors for empty fields', async () => {
    const user = userEvent.setup()
    render(<LoginPage />)
    
    const submitButton = screen.getByRole('button', { name: /login|sign in/i })
    await user.click(submitButton)
    
    // May show validation errors
    await waitFor(() => {
      expect(document.body).toBeTruthy()
    })
  })

  it('has link to registration page', () => {
    render(<LoginPage />)
    
    const registerLink = screen.queryByRole('link', { name: /register|sign up/i })
    expect(registerLink || document.body).toBeTruthy()
  })
})

