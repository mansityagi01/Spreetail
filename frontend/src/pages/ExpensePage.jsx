import { useEffect, useState } from 'react'
import { useParams, useNavigate } from 'react-router-dom'
import { api } from '../api'

function ExpensePage({ user }) {
  const { expenseId } = useParams()
  const navigate = useNavigate()
  const [expense, setExpense] = useState(null)
  const [messages, setMessages] = useState([])
  const [newMessage, setNewMessage] = useState('')
  const [users, setUsers] = useState([])
  const [attachments, setAttachments] = useState([])
  const [file, setFile] = useState(null)
  const [error, setError] = useState('')

  const userName = (id) => users.find(u => u.id === id)?.name || 'User ' + id

  const loadUsers = async () => {
    try { const res = await api.get('/api/users'); setUsers(res.data) } catch(e) {}
  }

  const loadExpense = async () => {
    try {
      const res = await api.get(`/api/expenses/${expenseId}`)
      setExpense(res.data)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to load expense')
    }
  }

  const loadMessages = async () => {
    try {
      const res = await api.get(`/api/expenses/${expenseId}/chat`)
      setMessages(res.data || [])
    } catch (e) {}
  }

  const loadAttachments = async () => {
    try { const res = await api.get(`/api/expenses/${expenseId}/attachments`); setAttachments(res.data || []) } catch(e) {}
  }

  useEffect(() => {
    loadUsers()
    loadExpense()
    loadMessages()
    loadAttachments()

    const timer = setInterval(() => {
      loadMessages()
    }, 3000)

    return () => clearInterval(timer)
  }, [expenseId])

  const onSend = async (e) => {
    e.preventDefault()
    if (!newMessage.trim()) return
    try {
      await api.post(
        `/api/expenses/${expenseId}/chat`,
        { message: newMessage.trim() },
        { params: { user_id: user.user_id } },
      )
      setNewMessage('')
      await loadMessages()
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to send message')
    }
  }

  const onDelete = async () => {
    if (!window.confirm('Delete this expense?')) return
    try {
      await api.delete(`/api/expenses/${expenseId}`, { params: { user_id: user.user_id } })
      navigate(-1)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Failed to delete')
    }
  }

  const onUploadFile = async (e) => {
    e.preventDefault()
    if (!file) return
    const formData = new FormData()
    formData.append('file', file)
    try {
      await api.post(`/api/expenses/${expenseId}/attachments`, formData, {
        params: { user_id: user.user_id },
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setFile(null)
      loadAttachments()
    } catch(e) { setError(e?.response?.data?.detail || 'Upload failed') }
  }

  if (!expense) return <p>Loading expense...</p>

  return (
    <div className="dashboard-grid">
      {error && <p className="error-msg">{error}</p>}

      <section className="card">
        <h2>Expense Detail</h2>
        <p><strong>Description:</strong> {expense.description}</p>
        <p><strong>Amount:</strong> ₹{expense.amount}</p>
        <p><strong>Paid by:</strong> {userName(expense.payer_id)}</p>
        <p><strong>Type:</strong> {expense.expense_type}</p>

        {expense.created_by === user.user_id && (
          <div className="action-buttons">
            <button className="btn-danger-sm" onClick={onDelete}>Delete Expense</button>
          </div>
        )}

        <h3>Split Details</h3>
        <ul className="balance-list">
          {expense.splits?.map(s => (
            <li key={s.id}>
              <strong>{userName(s.user_id)}</strong>
              <span>₹{s.amount_owed?.toFixed(2)} ({s.split_type})</span>
            </li>
          ))}
        </ul>
      </section>

      <section className="card">
        <h3>Attachments</h3>
        <ul className="balance-list">
          {attachments.map(a => (
            <li key={a.id}>
              <span>{a.file_name}</span>
              <a href={`${api.defaults.baseURL}/api/expenses/attachments/${a.id}/download`} target="_blank" rel="noreferrer">Download</a>
            </li>
          ))}
        </ul>
        {!attachments.length && <p>No attachments.</p>}
        <form onSubmit={onUploadFile} className="form-stack" style={{marginTop: '0.5rem'}}>
          <input type="file" onChange={(e) => setFile(e.target.files[0])} />
          <button type="submit" disabled={!file}>Upload Attachment</button>
        </form>
      </section>

      <section className="card card-wide">
        <h2>Expense Chat</h2>
        <ul className="balance-list">
          {messages.map((m) => (
            <li key={m.id}>
              <strong>{userName(m.user_id)}</strong>
              <span>{m.message}</span>
              <small className="chat-time">{new Date(m.created_at).toLocaleString()}</small>
            </li>
          ))}
        </ul>
        <form onSubmit={onSend} className="form-stack" style={{ marginTop: '0.75rem' }}>
          <input
            placeholder="Write a message"
            value={newMessage}
            onChange={(e) => setNewMessage(e.target.value)}
          />
          <button type="submit">Send</button>
        </form>
      </section>
    </div>
  )
}

export default ExpensePage
