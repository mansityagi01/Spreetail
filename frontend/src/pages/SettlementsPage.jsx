import { useEffect, useState } from 'react'
import { api } from '../api'

function SettlementsPage({ user }) {
  const [list, setList] = useState([])
  const [users, setUsers] = useState([])
  const [groups, setGroups] = useState([])
  const [form, setForm] = useState({ from_user_id: '', to_user_id: '', amount: '', group_id: '' })
  const [msg, setMsg] = useState('')
  const [error, setError] = useState('')

  const loadData = async () => {
    try {
      const [settlementsRes, usersRes, groupsRes] = await Promise.all([
        api.get('/api/settlements'),
        api.get('/api/users'),
        api.get('/api/groups', { params: { user_id: user.user_id } }),
      ])
      setList(settlementsRes.data || [])
      setUsers(usersRes.data || [])
      setGroups(groupsRes.data || [])
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load data')
    }
  }

  useEffect(() => {
    loadData()
  }, [])

  const onSubmit = async (e) => {
    e.preventDefault()
    try {
      await api.post(
        '/api/settlements',
        {
          from_user_id: Number(form.from_user_id),
          to_user_id: Number(form.to_user_id),
          amount: Number(form.amount),
          group_id: form.group_id ? Number(form.group_id) : null,
        },
        { params: { user_id: user.user_id } },
      )

      setForm({ from_user_id: '', to_user_id: '', amount: '', group_id: '' })
      setMsg('Payment recorded and balances updated')
      setTimeout(() => setMsg(''), 3000)
      await loadData()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to record settlement')
    }
  }

  return (
    <div className="dashboard-grid">
      <section className="card">
        <h2>Record Payment</h2>
        {error && <p className="error-msg">{error}</p>}
        <form onSubmit={onSubmit} className="form-stack">
          <select
            value={form.from_user_id}
            onChange={(e) => setForm((p) => ({ ...p, from_user_id: e.target.value }))}
            required
          >
            <option value="">From user</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.name}</option>
            ))}
          </select>

          <select
            value={form.to_user_id}
            onChange={(e) => setForm((p) => ({ ...p, to_user_id: e.target.value }))}
            required
          >
            <option value="">To user</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>{u.name}</option>
            ))}
          </select>

          <input
            type="number"
            step="0.01"
            placeholder="Amount (INR)"
            value={form.amount}
            onChange={(e) => setForm((p) => ({ ...p, amount: e.target.value }))}
            required
          />
          <select value={form.group_id} onChange={(e) => setForm(p => ({...p, group_id: e.target.value}))}>
            <option value="">No group (global)</option>
            {groups.map(g => <option key={g.id} value={g.id}>{g.name}</option>)}
          </select>
          <button type="submit">Record Settlement</button>
        </form>
        {msg && <p className="success-msg">{msg}</p>}
      </section>

      <section className="card card-wide">
        <h2>Who Should Pay Whom</h2>
        {!list.length && <p>No pending settlements.</p>}
        <ul className="balance-list">
          {list.map((item, idx) => (
            <li key={idx}>
              <strong>{item.from_user_name} → {item.to_user_name}</strong>
              <span>₹{item.amount}</span>
            </li>
          ))}
        </ul>
      </section>
    </div>
  )
}

export default SettlementsPage
