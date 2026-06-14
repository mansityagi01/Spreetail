import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'

function BalanceBreakdownPage({ user }) {
  const { otherUserId } = useParams()
  const navigate = useNavigate()
  const [breakdown, setBreakdown] = useState([])
  const [loading, setLoading] = useState(true)
  const [error, setError] = useState('')
  const [otherUser, setOtherUser] = useState(null)

  useEffect(() => {
    const fetchData = async () => {
      try {
        // Fetch users to get the other user's name
        const usersRes = await api.get('/api/users')
        const targetUser = usersRes.data.find(u => u.id === Number(otherUserId))
        setOtherUser(targetUser)

        const res = await api.get('/api/balances/breakdown', {
          params: { user_id: user.user_id, other_user_id: otherUserId }
        })
        setBreakdown(res.data)
      } catch (e) {
        setError(e?.response?.data?.detail || 'Failed to load breakdown')
      } finally {
        setLoading(false)
      }
    }
    fetchData()
  }, [user.user_id, otherUserId])

  if (loading) return <p>Loading breakdown...</p>

  const totalOwed = breakdown.reduce((sum, item) => sum + item.amount, 0)

  return (
    <div className="card card-wide">
      <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
        <h2>Itemized Balance with {otherUser?.name || 'Unknown'}</h2>
        <button onClick={() => navigate(-1)} className="btn-secondary">Back</button>
      </div>

      {error && <p className="error-msg">{error}</p>}

      <div className="summary-box" style={{ margin: '20px 0', padding: '15px', background: '#f5f5f5', borderRadius: '8px' }}>
        <h3>Net Balance: 
          <span style={{ color: totalOwed > 0 ? 'green' : totalOwed < 0 ? 'red' : 'black', marginLeft: '10px' }}>
            {totalOwed > 0 ? `They owe you ₹${totalOwed.toFixed(2)}` : totalOwed < 0 ? `You owe them ₹${(-totalOwed).toFixed(2)}` : 'Settled up'}
          </span>
        </h3>
      </div>

      <table className="anomaly-table">
        <thead>
          <tr>
            <th>Date</th>
            <th>Description</th>
            <th>Type</th>
            <th>Action</th>
            <th style={{textAlign: 'right'}}>Amount Effect</th>
          </tr>
        </thead>
        <tbody>
          {breakdown.map((item, idx) => (
            <tr key={idx}>
              <td>{new Date(item.date).toLocaleDateString()}</td>
              <td>{item.description}</td>
              <td><span className="badge">{item.type}</span></td>
              <td>{item.action}</td>
              <td style={{textAlign: 'right', color: item.amount > 0 ? 'green' : 'red', fontWeight: 'bold'}}>
                {item.amount > 0 ? '+' : ''}{item.amount.toFixed(2)}
              </td>
            </tr>
          ))}
          {breakdown.length === 0 && (
            <tr>
              <td colSpan="5" style={{textAlign: 'center'}}>No transactions found</td>
            </tr>
          )}
        </tbody>
      </table>
    </div>
  )
}

export default BalanceBreakdownPage
