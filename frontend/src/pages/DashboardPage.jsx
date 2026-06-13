import { useEffect, useState } from 'react'
import { Link } from 'react-router-dom'
import { api } from '../api'

function DashboardPage({ user }) {
  const [groups, setGroups] = useState([])
  const [users, setUsers] = useState([])
  const [newGroup, setNewGroup] = useState({ name: '', description: '' })
  const [selectedGroupId, setSelectedGroupId] = useState('')
  const [newMemberId, setNewMemberId] = useState('')
  const [expense, setExpense] = useState({
    group_id: '',
    payer_id: '',
    amount: '',
    description: '',
    split_type: 'equal',
    split_user_ids: [],
    split_values: '',
  })
  const [message, setMessage] = useState('')
  const [error, setError] = useState('')

  const showMessage = (msg) => {
    setMessage(msg)
    setTimeout(() => setMessage(''), 3000)
  }

  const loadGroups = async () => {
    try {
      const res = await api.get('/api/groups', { params: { user_id: user.user_id } })
      setGroups(res.data)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load groups')
    }
  }

  const loadUsers = async () => {
    try {
      const res = await api.get('/api/users')
      setUsers(res.data)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load users')
    }
  }

  useEffect(() => {
    loadGroups()
    loadUsers()
  }, [])

  const onCreateGroup = async (e) => {
    e.preventDefault()
    try {
      await api.post('/api/groups', newGroup, { params: { user_id: user.user_id } })
      setNewGroup({ name: '', description: '' })
      showMessage('Group created')
      loadGroups()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to create group')
    }
  }

  const onAddMember = async (e) => {
    e.preventDefault()
    if (!selectedGroupId || !newMemberId) return
    try {
      await api.post(
        `/api/groups/${selectedGroupId}/members`,
        {},
        { params: { user_id: user.user_id, new_user_id: Number(newMemberId) } },
      )
      showMessage('Member added')
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to add member')
    }
  }

  const onCreateExpense = async (e) => {
    e.preventDefault()
    try {
      const splitUserIds = expense.split_user_ids // already an array

      let splits
      if (expense.split_type === 'equal') {
        splits = splitUserIds.map((uid) => ({
          user_id: uid,
          split_type: expense.split_type,
          split_value: 0,
        }))
      } else {
        const splitValues = expense.split_values
          .split(',')
          .map((v) => v.trim())
          .filter(Boolean)
          .map(Number)

        splits = splitUserIds.map((uid, idx) => ({
          user_id: uid,
          split_type: expense.split_type,
          split_value: splitValues[idx] ?? 0,
        }))
      }

      await api.post(
        '/api/expenses',
        {
          group_id: expense.group_id ? Number(expense.group_id) : null,
          payer_id: Number(expense.payer_id),
          amount: Number(expense.amount),
          description: expense.description,
          expense_type: expense.group_id ? 'group' : 'direct_2person',
          splits,
        },
        { params: { user_id: user.user_id } },
      )

      showMessage('Expense created')
      setExpense({
        group_id: '',
        payer_id: '',
        amount: '',
        description: '',
        split_type: 'equal',
        split_user_ids: [],
        split_values: '',
      })
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to create expense')
    }
  }

  return (
    <div className="dashboard-grid">
      <section className="card">
        <h2>Your Groups</h2>
        <ul className="group-list">
          {groups.map((g) => (
            <li key={g.id}>
              <div>
                <strong>{g.name}</strong>
                <p>{g.description || 'No description'}</p>
              </div>
              <Link to={`/app/groups/${g.id}`}>Open</Link>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h2>Create Group</h2>
        <form onSubmit={onCreateGroup} className="form-stack">
          <input
            placeholder="Group name"
            value={newGroup.name}
            onChange={(e) => setNewGroup((p) => ({ ...p, name: e.target.value }))}
            required
          />
          <textarea
            placeholder="Description"
            value={newGroup.description}
            onChange={(e) => setNewGroup((p) => ({ ...p, description: e.target.value }))}
          />
          <button type="submit">Create</button>
        </form>
      </section>

      <section className="card">
        <h2>Add Group Member</h2>
        <form onSubmit={onAddMember} className="form-stack">
          <select
            value={selectedGroupId}
            onChange={(e) => setSelectedGroupId(e.target.value)}
            required
          >
            <option value="">Select group</option>
            {groups.map((g) => (
              <option key={g.id} value={g.id}>
                {g.name}
              </option>
            ))}
          </select>
          <select value={newMemberId} onChange={(e) => setNewMemberId(e.target.value)} required>
            <option value="">Select user</option>
            {users.map((u) => (
              <option key={u.id} value={u.id}>
                {u.name}
              </option>
            ))}
          </select>
          <button type="submit">Add Member</button>
        </form>
      </section>

      <section className="card card-wide">
        <h2>Create Expense</h2>
        <form onSubmit={onCreateExpense} className="form-stack">
          <div className="inline-grid">
            <select value={expense.group_id} onChange={(e) => setExpense((p) => ({ ...p, group_id: e.target.value }))}>
              <option value="">No group (direct 2-person)</option>
              {groups.map((g) => (
                <option key={g.id} value={g.id}>
                  {g.name}
                </option>
              ))}
            </select>
            <select
              value={expense.payer_id}
              onChange={(e) => setExpense((p) => ({ ...p, payer_id: e.target.value }))}
              required
            >
              <option value="">Select payer</option>
              {users.map((u) => (
                <option key={u.id} value={u.id}>
                  {u.name}
                </option>
              ))}
            </select>
            <input
              type="number"
              step="0.01"
              placeholder="Amount"
              value={expense.amount}
              onChange={(e) => setExpense((p) => ({ ...p, amount: e.target.value }))}
              required
            />
          </div>
          <input
            placeholder="Description"
            value={expense.description}
            onChange={(e) => setExpense((p) => ({ ...p, description: e.target.value }))}
            required
          />
          <select
            value={expense.split_type}
            onChange={(e) => setExpense((p) => ({ ...p, split_type: e.target.value }))}
          >
            <option value="equal">Equal</option>
            <option value="unequal">Unequal</option>
            <option value="percentage">Percentage</option>
            <option value="shares">Shares</option>
          </select>
          <div className="checkbox-group">
            <label>Split among:</label>
            {users.map(u => (
              <label key={u.id} className="checkbox-label">
                <input type="checkbox" checked={expense.split_user_ids.includes(u.id)}
                  onChange={(e) => {
                    if (e.target.checked) setExpense(p => ({...p, split_user_ids: [...p.split_user_ids, u.id]}))
                    else setExpense(p => ({...p, split_user_ids: p.split_user_ids.filter(id => id !== u.id)}))
                  }} />
                {u.name}
              </label>
            ))}
          </div>
          {expense.split_type !== 'equal' && (
            <input
              placeholder="Split values (comma-separated, e.g. 40,30,30)"
              value={expense.split_values}
              onChange={(e) => setExpense((p) => ({ ...p, split_values: e.target.value }))}
              required
            />
          )}
          <button type="submit">Create Expense</button>
        </form>
      </section>

      {error && <p className="error-msg">{error}</p>}
      {message && <p className="success-msg">{message}</p>}
    </div>
  )
}

export default DashboardPage
