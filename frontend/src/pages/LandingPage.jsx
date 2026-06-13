import { useEffect, useState } from 'react'
import { useNavigate } from 'react-router-dom'
import { api } from '../api'

function LandingPage() {
  const [demoUsers, setDemoUsers] = useState([])
  const [selectedEmail, setSelectedEmail] = useState('')
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState('')
  const navigate = useNavigate()

  useEffect(() => {
    const existing = localStorage.getItem('splitwise_demo_user')
    if (existing) {
      navigate('/app')
      return
    }

    api
      .get('/api/auth/demo-users')
      .then((res) => {
        const users = res.data.demo_users || []
        setDemoUsers(users)
        if (users.length > 0) setSelectedEmail(users[0].email)
      })
      .catch(() => setError('Unable to load demo users. Start backend first.'))
  }, [navigate])

  const onDemoLogin = async () => {
    if (!selectedEmail) return
    setLoading(true)
    setError('')

    try {
      const res = await api.post('/api/auth/demo-login', { email: selectedEmail })
      localStorage.setItem('splitwise_demo_user', JSON.stringify(res.data))
      window.location.href = '/app'
    } catch (e) {
      setError(e?.response?.data?.detail || 'Demo login failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="landing">
      <section className="hero">
        <h1>Less stress when sharing expenses</h1>
        <p>
          Track group expenses, split fairly, and settle debts quickly.
          Built as a Splitwise-inspired MVP for internship assessment.
        </p>

        <div className="demo-login-box">
          <label htmlFor="demoUser">Choose Demo Account</label>
          <select
            id="demoUser"
            value={selectedEmail}
            onChange={(e) => setSelectedEmail(e.target.value)}
          >
            {demoUsers.map((u) => (
              <option key={u.email} value={u.email}>
                {u.name} ({u.email})
              </option>
            ))}
          </select>
          <button disabled={loading || !selectedEmail} onClick={onDemoLogin}>
            {loading ? 'Signing in...' : 'Demo Login'}
          </button>
          {error && <p className="error">{error}</p>}
        </div>
      </section>

      <section className="features">
        <div className="feature-card">
          <h3>Create groups and expenses</h3>
          <p>Manage members, add bills, and split by equal, unequal, percentage, or shares.</p>
        </div>
        <div className="feature-card">
          <h3>Smart balances</h3>
          <p>See who owes whom with simplified debt settlement suggestions.</p>
        </div>
        <div className="feature-card">
          <h3>Expense conversations</h3>
          <p>Discuss each expense inside dedicated chat threads.</p>
        </div>
      </section>
    </div>
  )
}

export default LandingPage
