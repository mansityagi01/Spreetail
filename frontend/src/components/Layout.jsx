import { NavLink, useNavigate } from 'react-router-dom'

function Layout({ user, children }) {
  const navigate = useNavigate()

  const onLogout = () => {
    localStorage.removeItem('splitwise_demo_user')
    window.location.href = '/'
  }

  return (
    <div className="app-shell">
      <header className="topbar">
        <div className="brand">Spreetail</div>
        <nav className="nav-links">
          <NavLink to="/app" end>Dashboard</NavLink>
          <NavLink to="/app/balances">Balances</NavLink>
          <NavLink to="/app/settlements">Settlements</NavLink>
          <NavLink to="/app/import">Import Data</NavLink>
        </nav>
        <div className="user-box">
          <span>{user?.name}</span>
          <button onClick={onLogout}>Logout</button>
        </div>
      </header>
      <main className="content">{children}</main>
    </div>
  )
}

export default Layout
