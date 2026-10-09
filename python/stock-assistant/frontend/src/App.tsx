import { BrowserRouter as Router, Routes, Route } from 'react-router-dom'
import Layout from '@/components/layout/Layout'
import ToastContainer from '@/components/ToastContainer'
import Dashboard from '@/pages/Dashboard'
import Watchlist from '@/pages/Watchlist'
import SectorFundFlow from '@/pages/SectorFundFlow'
import Rules from '@/pages/Rules'
import History from '@/pages/History'
import Settings from '@/pages/Settings'

export default function App() {
  return (
    <Router>
      <ToastContainer />
      <Routes>
        <Route element={<Layout />}>
          <Route path="/" element={<Dashboard />} />
          <Route path="/watchlist" element={<Watchlist />} />
          <Route path="/sectors" element={<SectorFundFlow />} />
          <Route path="/rules" element={<Rules />} />
          <Route path="/history" element={<History />} />
          <Route path="/settings" element={<Settings />} />
        </Route>
      </Routes>
    </Router>
  )
}
