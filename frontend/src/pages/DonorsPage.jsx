import { useEffect, useState } from "react";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import {
  createDonor,
  getApiErrorMessage,
  getMyDonorProfile,
  listDonors,
  updateDonor,
} from "../services/api";
import Navbar from "../components/Navbar";

const BLOOD_GROUPS = ["A+", "A-", "B+", "B-", "AB+", "AB-", "O+", "O-"];
const AVAILABILITY_LABELS = {
  available: "Available",
  unavailable: "Unavailable",
  unknown: "Unknown",
};

export default function DonorsPage() {
  const { user } = useAuth();
  const [donors, setDonors] = useState([]);
  const [searching, setSearching] = useState(false);
  const [searched, setSearched] = useState(false);
  const [searchFilters, setSearchFilters] = useState(null);
  const [searchOffset, setSearchOffset] = useState(0);
  const [searchError, setSearchError] = useState("");
  const [myProfile, setMyProfile] = useState(null);
  const [profileError, setProfileError] = useState("");
  const [profileMessage, setProfileMessage] = useState("");
  const [profileLoading, setProfileLoading] = useState(user?.role === "donor");
  const [showForm, setShowForm] = useState(false);

  const {
    register: registerSearch,
    handleSubmit: handleSearch,
    reset: resetSearch,
  } = useForm({ defaultValues: { availability_status: "available" } });
  const {
    register: registerProfile,
    handleSubmit: handleProfile,
    reset: resetProfile,
    formState: { errors, isSubmitting },
  } = useForm({
    defaultValues: {
      blood_group: BLOOD_GROUPS[0],
      availability_status: "available",
      consent_to_contact: false,
    },
  });

  useEffect(() => {
    if (user?.role !== "donor") {
      setProfileLoading(false);
      return;
    }

    getMyDonorProfile()
      .then((response) => {
        setMyProfile(response.data);
        resetProfile(response.data);
      })
      .catch((error) => {
        if (error.response?.status !== 404) {
          setProfileError(getApiErrorMessage(error, "Could not load your donor profile."));
        }
      })
      .finally(() => setProfileLoading(false));
  }, [user?.role, resetProfile]);

  useEffect(() => {
    if (!searched || !searchFilters) return undefined;

    let active = true;
    setSearching(true);
    setSearchError("");
    listDonors({ ...searchFilters, offset: searchOffset, limit: 51 })
      .then((response) => {
        if (active) setDonors(response.data);
      })
      .catch((error) => {
        if (active) {
          setDonors([]);
          setSearchError(getApiErrorMessage(error, "Could not search donors."));
        }
      })
      .finally(() => {
        if (active) setSearching(false);
      });

    return () => { active = false; };
  }, [searched, searchFilters, searchOffset]);

  async function onSearch(data) {
    const params = {};
    if (data.blood_group) params.blood_group = data.blood_group;
    if ((data.city ?? "").trim()) params.city = data.city.trim();
    if (data.availability_status) params.availability_status = data.availability_status;
    setSearchOffset(0);
    setSearchFilters(params);
    setSearched(true);
  }

  async function onSaveProfile(data) {
    setProfileError("");
    setProfileMessage("");
    try {
      const response = myProfile
        ? await updateDonor(myProfile.id, data)
        : await createDonor(data);
      setMyProfile(response.data);
      resetProfile(response.data);
      setProfileMessage("Your donor profile has been saved.");
      setShowForm(false);
    } catch (error) {
      setProfileError(getApiErrorMessage(error, "Could not save your profile."));
    }
  }

  function toggleProfileForm() {
    setProfileError("");
    setProfileMessage("");
    resetProfile(myProfile ?? {
      blood_group: BLOOD_GROUPS[0],
      phone_number: "",
      city: "",
      availability_status: "available",
      consent_to_contact: false,
    });
    setShowForm((visible) => !visible);
  }

  return (
    <>
      <Navbar />
      <main className="page-container">
        <header className="page-header">
          <div>
            <h2>Donor directory</h2>
            <p className="page-subtitle">Search consenting donors by blood group, location, and availability.</p>
          </div>
        </header>

        {user?.role === "donor" && (
          <section className="card" aria-labelledby="profile-heading">
            <div className="card-header">
              <h3 id="profile-heading">My donor profile</h3>
              <button
                className="btn btn-outline"
                type="button"
                onClick={toggleProfileForm}
                disabled={profileLoading}
              >
                {showForm ? "Close" : myProfile ? "Edit profile" : "Create profile"}
              </button>
            </div>
            {profileLoading && <p className="empty-text">Loading your profile…</p>}
            {profileError && <div className="alert alert-error" role="alert">{profileError}</div>}
            {profileMessage && <div className="alert alert-success" role="status">{profileMessage}</div>}

            {myProfile && !showForm && (
              <div className="profile-summary">
                <span className="badge">{myProfile.blood_group}</span>
                <span>{myProfile.city}</span>
                <span className={`status-dot ${myProfile.availability_status}`}>
                  {AVAILABILITY_LABELS[myProfile.availability_status]}
                </span>
                <span>{myProfile.consent_to_contact ? "Contact consent enabled" : "Contact consent disabled"}</span>
              </div>
            )}

            {showForm && (
              <form onSubmit={handleProfile(onSaveProfile)} className="inline-form" noValidate>
                <div className="form-row">
                  <div className="form-group">
                    <label htmlFor="profile-blood-group">Blood group</label>
                    <select id="profile-blood-group" {...registerProfile("blood_group", { required: "Choose a blood group." })}>
                      {BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}
                    </select>
                    {errors.blood_group && <span className="error-text">{errors.blood_group.message}</span>}
                  </div>
                  <div className="form-group">
                    <label htmlFor="profile-phone">Phone number</label>
                    <input
                      id="profile-phone"
                      type="tel"
                      autoComplete="tel"
                      {...registerProfile("phone_number", {
                        required: "Phone number is required.",
                        validate: (value) => {
                          const normalized = value.trim();
                          const isValidFormat = /^[+]?[0-9][0-9\s().-]{5,24}$/.test(normalized);
                          return (isValidFormat && (normalized.match(/[0-9]/g) ?? []).length >= 7)
                            || "Enter a valid phone number.";
                        },
                      })}
                    />
                    {errors.phone_number && <span className="error-text">{errors.phone_number.message}</span>}
                  </div>
                  <div className="form-group">
                    <label htmlFor="profile-city">City</label>
                    <input
                      id="profile-city"
                      type="text"
                      maxLength="100"
                      {...registerProfile("city", {
                        required: "City is required.",
                        validate: (value) => value.trim().length >= 2 || "Enter at least 2 characters.",
                      })}
                    />
                    {errors.city && <span className="error-text">{errors.city.message}</span>}
                  </div>
                  <div className="form-group">
                    <label htmlFor="profile-availability">Availability</label>
                    <select id="profile-availability" {...registerProfile("availability_status")}>
                      {Object.entries(AVAILABILITY_LABELS).map(([value, label]) => (
                        <option key={value} value={value}>{label}</option>
                      ))}
                    </select>
                  </div>
                </div>
                <label className="checkbox-label">
                  <input type="checkbox" {...registerProfile("consent_to_contact")} />
                  I consent to being listed in donor search results
                </label>
                <p className="hint-text">Your phone number is never shown in the donor directory.</p>
                <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
                  {isSubmitting ? "Saving…" : "Save profile"}
                </button>
              </form>
            )}
          </section>
        )}

        <section className="card" aria-labelledby="search-heading">
          <h3 id="search-heading">Search donors</h3>
          <form onSubmit={handleSearch(onSearch)} className="search-form">
            <div className="form-group">
              <label htmlFor="search-blood-group">Blood group</label>
              <select id="search-blood-group" {...registerSearch("blood_group")}>
                <option value="">All blood groups</option>
                {BLOOD_GROUPS.map((group) => <option key={group} value={group}>{group}</option>)}
              </select>
            </div>
            <div className="form-group">
              <label htmlFor="search-city">City</label>
              <input id="search-city" type="search" maxLength="100" placeholder="e.g. Delhi" {...registerSearch("city")} />
            </div>
            <div className="form-group">
              <label htmlFor="search-availability">Availability</label>
              <select id="search-availability" {...registerSearch("availability_status")}>
                {Object.entries(AVAILABILITY_LABELS).map(([value, label]) => (
                  <option key={value} value={value}>{label}</option>
                ))}
              </select>
            </div>
            <button className="btn btn-primary search-btn" type="submit" disabled={searching}>
              {searching ? "Searching…" : "Search"}
            </button>
            <button
              className="btn btn-outline search-btn"
              type="button"
              onClick={() => {
                resetSearch({ availability_status: "available" });
                setSearched(false);
                setSearchFilters(null);
                setSearchOffset(0);
                setSearching(false);
                setDonors([]);
                setSearchError("");
              }}
            >
              Clear
            </button>
          </form>
          <p className="hint-text">Only donors who chose to appear in search results are shown. Search is for coordination only; it does not assess eligibility or compatibility.</p>
        </section>

        {searchError && <div className="alert alert-error" role="alert">{searchError}</div>}
        {searched && (
          <section className="card" aria-live="polite">
            <h3>Results <span className="count">({Math.min(donors.length, 50)} shown)</span></h3>
            {searching ? (
              <p className="empty-text">Searching…</p>
            ) : donors.length === 0 ? (
              <p className="empty-text">No consenting donors match those filters.</p>
            ) : (
              <>
                <div className="table-wrap">
                  <table className="data-table">
                    <thead>
                      <tr>
                        <th scope="col">Donor ID</th>
                        <th scope="col">Blood group</th>
                        <th scope="col">City</th>
                        <th scope="col">Availability</th>
                      </tr>
                    </thead>
                    <tbody>
                      {donors.slice(0, 50).map((donor) => (
                        <tr key={donor.id}>
                          <td>#{donor.id}</td>
                          <td><span className="badge">{donor.blood_group}</span></td>
                          <td>{donor.city}</td>
                          <td>
                            <span className={`status-dot ${donor.availability_status}`}>
                              {AVAILABILITY_LABELS[donor.availability_status]}
                            </span>
                          </td>
                        </tr>
                      ))}
                    </tbody>
                  </table>
                </div>
                <div className="pagination-controls" aria-label="Donor search pages">
                  <button
                    className="btn btn-outline"
                    type="button"
                    onClick={() => setSearchOffset((offset) => Math.max(0, offset - 50))}
                    disabled={searchOffset === 0 || searching}
                  >
                    Previous
                  </button>
                  <span>Page {Math.floor(searchOffset / 50) + 1}</span>
                  <button
                    className="btn btn-outline"
                    type="button"
                    onClick={() => setSearchOffset((offset) => offset + 50)}
                    disabled={donors.length <= 50 || searching}
                  >
                    Next
                  </button>
                </div>
              </>
            )}
          </section>
        )}
      </main>
    </>
  );
}
