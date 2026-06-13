import { useEffect, useState } from 'react'
import { api } from '../api'

function BalancesPage({ user }) {
  const [balances, setBalances] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')

  useEffect(() => {
    api
      .get('/api/balances', { params: { user_id: user.user_id } })
      .then((res) => setBalances(res.data || []))
      .catch((e) => setError(e?.response?.data?.detail || 'Failed to load balances'))
      .finally(() => setLoading(false))
  }, [user.user_id])

  if (loading) return <p>Loading balances...</p>

  return (
    <div className="card">
      <h2>Global Balances</h2>
      {error && <p className="error-msg">{error}</p>}
      {!balances.length && !error && <p>No balances found.</p>}
      <ul className="balance-list">
        {balances.map((b) => (
          <li key={`${b.user_id}-${b.other_user_id}`}>
            <strong>{b.other_user_name}</strong>
            <span>{b.description}</span>
          </li>
        ))}
      </ul>
    </div>
  )
}

export default BalancesPage
