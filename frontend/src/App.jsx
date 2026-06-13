import { BrowserRouter, Link, Navigate, Route, Routes } from 'react-router-dom'
import LandingPage from './pages/LandingPage'
import DashboardPage from './pages/DashboardPage'
import BalancesPage from './pages/BalancesPage'
import GroupPage from './pages/GroupPage'
import SettlementsPage from './pages/SettlementsPage'
import ExpensePage from './pages/ExpensePage'
import Layout from './components/Layout'

function Protected({ children }) {
  const user = localStorage.getItem('splitwise_demo_user')
  if (!user) {
    return <Navigate to="/" replace />
  }

  return children
}

function AppRoutes() {
  const userStr = localStorage.getItem('splitwise_demo_user')
  const user = userStr ? JSON.parse(userStr) : null

  return (
    <Routes>
      <Route path="/" element={<LandingPage />} />
      <Route
        path="/app"
        element={
          <Protected>
            <Layout user={user}>
              <DashboardPage user={user} />
            </Layout>
          </Protected>
        }
      />
      <Route
        path="/app/balances"
        element={
          <Protected>
            <Layout user={user}>
              <BalancesPage user={user} />
            </Layout>
          </Protected>
        }
      />
      <Route
        path="/app/groups/:groupId"
        element={
          <Protected>
            <Layout user={user}>
              <GroupPage user={user} />
            </Layout>
          </Protected>
        }
      />
      <Route
        path="/app/settlements"
        element={
          <Protected>
            <Layout user={user}>
              <SettlementsPage user={user} />
            </Layout>
          </Protected>
        }
      />
      <Route
        path="/app/expenses/:expenseId"
        element={
          <Protected>
            <Layout user={user}>
              <ExpensePage user={user} />
            </Layout>
          </Protected>
        }
      />
      <Route path="*" element={
        <div className="not-found">
          <h1>404</h1>
          <p>Page not found</p>
          <Link to="/">Back to Home</Link>
        </div>
      } />
    </Routes>
  )
}

function App() {
  return (
    <BrowserRouter>
      <AppRoutes />
    </BrowserRouter>
  )
}

export default App
