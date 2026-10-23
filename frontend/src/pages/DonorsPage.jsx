/**
 * DonorsPage — search donors by blood group and city.
 * Donors can also create or update their own profile from here.
 */
import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import { listDonors, createDonor, getMyDonorProfile, updateDonor } from "../services/api";
import Navbar from "../components/Navbar";

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];

export default function DonorsPage() {
  const { user } = useAuth();

  // Search state
  const [donors, setDonors]       = useState([]);
  const [searching, setSearching] = useState(false);
  const [searched, setSearched]   = useState(false);

  // Donor profile state (for users with role=donor)
  const [myProfile, setMyProfile]     = useState(null);
  const [profileMsg, setProfileMsg]   = useState("");
  const [showForm, setShowForm]       = useState(false);

  // Search form
  const { register: regSearch, handleSubmit: handleSearch } = useForm();

  // Profile form
  const {
    register: regProfile,
    handleSubmit: handleProfile,
    reset,
    formState: { isSubmitting },
  } = useForm();

  // Load own donor profile if logged in as donor
  useEffect(() => {
    if (user?.role === "donor") {
      getMyDonorProfile()
        .then((res) => {
          setMyProfile(res.data);
          reset(res.data); // pre-fill the form
        })
        .catch(() => {}); // no profile yet — that's fine
    }
  }, [user, reset]);

  // Search donors
  async function onSearch(data) {
    setSearching(true);
    setSearched(true);
    try {
      const params = {};
      if (data.blood_group) params.blood_group = data.blood_group;
      if (data.city)        params.city        = data.city;
      const res = await listDonors(params);
      setDonors(res.data);
    } catch {
      setDonors([]);
    } finally {
      setSearching(false);
    }
  }

  // Create or update donor profile
  async function onSaveProfile(data) {
    setProfileMsg("");
    try {
      if (myProfile) {
        const res = await updateDonor(myProfile.id, data);
        setMyProfile(res.data);
      } else {
        const res = await createDonor(data);
        setMyProfile(res.data);
      }
      setProfileMsg("Profile saved successfully.");
      setShowForm(false);
    } catch (err) {
      setProfileMsg(err.response?.data?.detail ?? "Could not save profile.");
    }
  }

  return (
    <>
      <Navbar />

      <main className="page-container">

        {/* ── Donor Profile Section (donors only) ── */}
        {user?.role === "donor" && (
          <section className="card">
            <div className="card-header">
              <h3>My Donor Profile</h3>
              <button className="btn btn-outline" onClick={() => setShowForm(!showForm)}>
                {showForm ? "Cancel" : myProfile ? "Edit" : "Create Profile"}
              </button>
            </div>

            {profileMsg && (
              <div className={`alert ${profileMsg.includes("success") ? "alert-success" : "alert-error"}`}>
                {profileMsg}
              </div>
            )}

            {/* Profile summary */}
            {myProfile && !showForm && (
              <div className="profile-summary">
                <span className="badge">{myProfile.blood_group}</span>
                <span>{myProfile.city}</span>
                <span className={`status-dot ${myProfile.availability_status}`}>
                  {myProfile.availability_status}
                </span>
              </div>
            )}

            {/* Profile form */}
            {showForm && (
              <form onSubmit={handleProfile(onSaveProfile)} className="inline-form">
                <div className="form-row">
                  <div className="form-group">
                    <label>Blood Group</label>
                    <select {...regProfile("blood_group", { required: true })}>
                      {BLOOD_GROUPS.map((bg) => <option key={bg}>{bg}</option>)}
                    </select>
                  </div>
                  <div className="form-group">
                    <label>Phone Number</label>
                    <input type="tel" {...regProfile("phone_number", { required: true })} />
                  </div>
                  <div className="form-group">
                    <label>City</label>
                    <input type="text" {...regProfile("city", { required: true })} />
                  </div>
                  <div className="form-group">
                    <label>Availability</label>
                    <select {...regProfile("availability_status")}>
                      <option value="available">Available</option>
                      <option value="unavailable">Unavailable</option>
                      <option value="unknown">Unknown</option>
                    </select>
                  </div>
                </div>
                <div className="form-group">
                  <label className="checkbox-label">
                    <input type="checkbox" {...regProfile("consent_to_contact")} />
                    I consent to being contacted
                  </label>
                </div>
                <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Saving…" : "Save Profile"}
                </button>
              </form>
            )}
          </section>
        )}

        {/* ── Donor Search Section ── */}
        <section className="card">
          <h3>Search Donors</h3>
          <form onSubmit={handleSearch(onSearch)} className="search-form">
            <div className="form-group">
              <label>Blood Group</label>
              <select {...regSearch("blood_group")}>
                <option value="">All blood groups</option>
                {BLOOD_GROUPS.map((bg) => <option key={bg}>{bg}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label>City</label>
              <input type="text" placeholder="e.g. Delhi" {...regSearch("city")} />
            </div>
            <button className="btn btn-primary search-btn" type="submit">
              {searching ? "Searching…" : "Search"}
            </button>
          </form>
        </section>

        {/* ── Search Results ── */}
        {searched && (
          <section className="card">
            <h3>Results {donors.length > 0 && <span className="count">({donors.length} found)</span>}</h3>

            {donors.length === 0 ? (
              <p className="empty-text">No donors found for the selected filters.</p>
            ) : (
              <div className="table-wrap">
                <table className="data-table">
                  <thead>
                    <tr>
                      <th>Blood Group</th>
                      <th>City</th>
                      <th>Availability</th>
                      <th>Contact Consent</th>
                    </tr>
                  </thead>
                  <tbody>
                    {donors.map((d) => (
                      <tr key={d.id}>
                        <td><span className="badge">{d.blood_group}</span></td>
                        <td>{d.city}</td>
                        <td>
                          <span className={`status-dot ${d.availability_status}`}>
                            {d.availability_status}
                          </span>
                        </td>
                        <td>{d.consent_to_contact ? "✅ Yes" : "❌ No"}</td>
                      </tr>
                    ))}
                  </tbody>
                </table>
              </div>
            )}
          </section>
        )}

      </main>
    </>
  );
}
