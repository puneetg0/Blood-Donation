import { useEffect, useState } from "react";
import { useAuth } from "../context/AuthContext";
import { useNavigate } from "react-router-dom";
import { getDonorCoordinations, getMyDonorProfile, respondToCoordination, getApiErrorMessage } from "../services/api";
import Navbar from "../components/Navbar";

export default function MyCoordinations() {
  const { user } = useAuth();
  const navigate = useNavigate();
  const [coordinations, setCoordinations] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState("");

  const isDonor = user?.role === "donor";

  useEffect(() => {
    if (!isDonor) {
      navigate("/requests", { replace: true });
      setLoading(false);
      return;
    }
    let active = true;
    getMyDonorProfile()
      .then((res) => {
        if (!active) return;
        return getDonorCoordinations(res.data.id);
      })
      .then((res) => {
        if (!active || !res) return;
        setCoordinations(res.data);
        setLoading(false);
      })
      .catch(() => {
        if (!active) return;
        setError("Could not load your coordinations.");
        setLoading(false);
      });
    return () => { active = false; };
  }, [isDonor, navigate, user?.id]);

  async function handleRespond(coordId, response) {
    try {
      const res = await respondToCoordination(coordId, response === "accept" ? "accept" : "decline");
      setCoordinations((prev) =>
        prev.map((c) => (c.id === coordId ? res.data : c))
      );
    } catch (err) {
      setError(getApiErrorMessage(err, "Could not respond."));
    }
  }

  if (loading) return <><Navbar /><main className="page-container"><p className="empty-text">Loading your coordinations…</p></main></>;
  if (error) return <><Navbar /><main className="page-container"><div className="alert alert-error">{error}</div></main></>;
  if (coordinations.length === 0)
    return (
      <>
        <Navbar />
        <main className="page-container">
          <div className="empty-state">
            <p>No pending coordinations yet.</p>
            <p className="hint-text">Coordinations will appear here when administrators link you to a request.</p>
          </div>
        </main>
      </>
    );

  return (
    <>
      <Navbar />
      <main className="page-container">
        <div className="card">
          <h2>My Coordination Requests</h2>
          <p className="hint-text">These are requests where administrators have linked you as a potential donor. You can accept or decline each one.</p>
          <div className="table-wrap">
            <table className="data-table">
              <thead>
                <tr>
                  <th>Request</th>
                  <th>Blood Group</th>
                  <th>City</th>
                  <th>Status</th>
                  <th>Action</th>
                </tr>
              </thead>
              <tbody>
                {coordinations.map((coord) => (
                  <tr key={coord.id}>
                    <td>#{coord.request_id}</td>
                    <td>{coord.blood_group}</td>
                    <td>{coord.city}</td>
                    <td>
                      <span className={`badge status-dot ${coord.coordination_status}`}>
                        {coord.coordination_status}
                      </span>
                    </td>
                    <td>
                      {coord.coordination_status === "contact_pending" ? (
                        <div className="coord-btns">
                          <button className="btn btn-success btn-sm" onClick={() => handleRespond(coord.id, "accept")}>
                            Accept
                          </button>
                          <button className="btn btn-danger btn-sm" onClick={() => handleRespond(coord.id, "decline")}>
                            Decline
                          </button>
                        </div>
                      ) : (
                        <span className="badge">{coord.coordination_status}</span>
                      )}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </main>
    </>
  );
}
