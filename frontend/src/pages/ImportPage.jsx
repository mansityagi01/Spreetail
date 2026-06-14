import { useState } from 'react'
import { api } from '../api'

function ImportPage({ user }) {
  const [file, setFile] = useState(null)
  const [loading, setLoading] = useState(false)
  const [report, setReport] = useState(null)
  const [error, setError] = useState('')

  const onImport = async (e) => {
    e.preventDefault()
    if (!file) return

    setLoading(true)
    setError('')
    setReport(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const res = await api.post('/api/import', formData, {
        params: { user_id: user.user_id },
        headers: { 'Content-Type': 'multipart/form-data' }
      })
      setReport(res.data)
    } catch (e) {
      setError(e?.response?.data?.detail || 'Import failed')
    } finally {
      setLoading(false)
    }
  }

  return (
    <div className="card card-wide">
      <h2>Import CSV Data</h2>
      
      {!report && (
        <form onSubmit={onImport} className="form-stack">
          <p>Select your <code>expenses_export.csv</code> file to import into the Flatmates group.</p>
          <input 
            type="file" 
            accept=".csv" 
            onChange={(e) => setFile(e.target.files[0])} 
            required 
          />
          <button type="submit" disabled={!file || loading}>
            {loading ? 'Importing & Analyzing...' : 'Upload & Import'}
          </button>
        </form>
      )}

      {error && <p className="error-msg">{error}</p>}

      {report && (
        <div className="import-report">
          <h3>Import Successful!</h3>
          <p>
            Processed <strong>{report.total_rows}</strong> rows. 
            Successfully imported <strong>{report.imported_rows}</strong> transactions.
          </p>
          
          <h4>Anomaly Detection Report</h4>
          <p>The system detected {report.anomalies.length} data issues in the CSV and applied automated policies to resolve them.</p>
          
          <table className="anomaly-table">
            <thead>
              <tr>
                <th>Row</th>
                <th>Issue Type</th>
                <th>Description</th>
                <th>Action Taken</th>
              </tr>
            </thead>
            <tbody>
              {report.anomalies.map((anom, idx) => (
                <tr key={idx}>
                  <td>{anom.row_number}</td>
                  <td><span className="badge">{anom.issue_type}</span></td>
                  <td>{anom.description}</td>
                  <td>{anom.action_taken}</td>
                </tr>
              ))}
            </tbody>
          </table>
          
          <button onClick={() => window.location.href = '/app'} style={{marginTop: '20px'}}>
            Return to Dashboard
          </button>
        </div>
      )}
    </div>
  )
}

export default ImportPage
