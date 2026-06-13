import { useEffect, useState } from 'react'
import { Link, useParams } from 'react-router-dom'
import { api } from '../api'

function GroupPage({ user }) {
  const { groupId } = useParams()
  const [group, setGroup] = useState(null)
  const [balances, setBalances] = useState([])
  const [error, setError] = useState('')

  useEffect(() => {
    const loadGroup = async () => {
      try {
        const res = await api.get(`/api/groups/${groupId}`)
        setGroup(res.data)
      } catch (e) {
        setError(e?.response?.data?.detail || 'Failed to load group')
      }
    }
    const loadBalances = async () => {
      try {
        const res = await api.get(`/api/groups/${groupId}/balances`, { params: { user_id: user.user_id } })
        setBalances(res.data || [])
      } catch (e) {
        setError(e?.response?.data?.detail || 'Failed to load balances')
      }
    }
    loadGroup()
    loadBalances()
  }, [groupId, user.user_id])

  const onRemoveMember = async (memberId) => {
    if (!window.confirm('Remove this member from the group?')) return
    try {
      await api.delete(`/api/groups/${groupId}/members/${memberId}`, { params: { user_id: user.user_id } })
      // Reload group data
      const res = await api.get(`/api/groups/${groupId}`)
      setGroup(res.data)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to remove member')
    }
  }

  if (!group) return <p>Loading group...</p>

  return (
    <div className="dashboard-grid">
      {error && <p className="error-msg">{error}</p>}

      <section className="card">
        <h2>{group.name}</h2>
        <p>{group.description || 'No description'}</p>
        <h3>Members</h3>
        <ul className="balance-list">
          {group.members?.map((m) => (
            <li key={m.id}>
              <strong>{m.user?.name || `User ${m.user_id}`}</strong>
              <span>{m.is_active ? 'Active' : 'Removed (history only)'}</span>
              {m.is_active && (
                <button className="btn-danger-sm" onClick={() => onRemoveMember(m.user_id)}>Remove</button>
              )}
            </li>
          ))}
        </ul>
      </section>

      <section className="card card-wide">
        <h3>Group Balances</h3>
        {!balances.length && <p>No balances yet.</p>}
        <ul className="balance-list">
          {balances.map((b, idx) => (
            <li key={idx}>
              <strong>{b.user_name}</strong>
              <span>{b.description}</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card card-wide">
        <h3>Group Expenses</h3>
        {!group.expenses?.length && <p>No expenses yet.</p>}
        <ul className="group-list">
          {group.expenses?.map((e) => (
            <li key={e.id}>
              <div>
                <strong>{e.description}</strong>
                <p>₹{e.amount}</p>
              </div>
              <Link to={`/app/expenses/${e.id}`}>Open</Link>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

export default GroupPage
