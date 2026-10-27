import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";
import { getApiErrorMessage } from "../services/api";

const ELIGIBILITY_ITEMS = [
  { label: "I am at least 18 years old", hint: "Age requirement varies by country" },
  { label: "I weigh at least 50 kg (110 lbs)", hint: "Follow local donation rules" },
  { label: "I am generally healthy, no fever or infection", hint: "You may be deferred if unwell" },
  { label: "I have not traveled to malaria-risk areas recently", hint: "Travel history matters" },
  { label: "I am not taking medication that prevents donation", hint: "Ask your doctor if unsure" },
  { label: "I am not pregnant or breastfeeding", hint: "Follow local guidelines" },
];

export default function RegisterPage() {
  const { register: registerCtx } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    watch,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { role: "requester" }, mode: "onBlur" });

  const role = watch("role");

  async function onSubmit(data) {
    setServerError("");
    try {
      await registerCtx(data);
      navigate("/dashboard");
    } catch (err) {
      setServerError(getApiErrorMessage(err, "Registration failed. Please try again."));
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
        <div className="auth-brand">Blood Donation Manager</div>
        <h1>Create account</h1>
        <p className="subtitle">Join Blood Donation Manager</p>

        {serverError && <div className="alert alert-error">{serverError}</div>}

        <form onSubmit={handleSubmit(onSubmit)} noValidate>
          <div className="form-group">
            <label htmlFor="full_name">Full name</label>
            <input
              id="full_name"
              type="text"
              autoComplete="name"
              {...register("full_name", {
                required: "Full name is required.",
                validate: (value) => value.trim().length >= 2 || "Enter at least 2 characters.",
                maxLength: { value: 100, message: "Name must be 100 characters or fewer." },
              })}
            />
            {errors.full_name && <span className="error-text">{errors.full_name.message}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="email">Email</label>
            <input
              id="email"
              type="email"
              autoComplete="email"
              {...register("email", {
                required: "Email is required.",
                pattern: { value: /^[^\s@]+@[^\s@]+\.[^\s@]+$/, message: "Enter a valid email." },
              })}
            />
            {errors.email && <span className="error-text">{errors.email.message}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="password">Password</label>
            <input
              id="password"
              type="password"
              autoComplete="new-password"
              {...register("password", {
                required: "Password is required.",
                minLength: { value: 8, message: "Password must be at least 8 characters." },
                validate: (value) => new TextEncoder().encode(value).length <= 72
                  || "Password must be no more than 72 UTF-8 bytes.",
              })}
            />
            {errors.password && <span className="error-text">{errors.password.message}</span>}
          </div>

          <div className="form-group">
            <label htmlFor="role">I am a…</label>
            <select id="role" {...register("role", { required: true })}>
              <option value="requester">Blood Requester</option>
              <option value="donor">Donor</option>
            </select>
          </div>

          {role === "donor" && (
            <div className="eligibility-card">
              <div className="eligibility-header">
                <span className="eligibility-icon">✅</span>
                <div>
                  <h4>Eligibility Self-Check</h4>
                  <p className="hint-text">
                    Informational checklist to help you prepare before donating. Does not replace screening at the donation centre.
                  </p>
                </div>
              </div>
              <div className="checkbox-group">
                {ELIGIBILITY_ITEMS.map((item, idx) => (
                  <label className="checkbox-label" key={idx}>
                    <input type="checkbox" defaultChecked />
                    <div className="checkbox-text">
                      <span>{item.label}</span>
                      <span className="hint-text">{item.hint}</span>
                    </div>
                  </label>
                ))}
              </div>
            </div>
          )}

          <button className="btn btn-primary" type="submit" disabled={isSubmitting}>
            {isSubmitting ? "Creating account…" : "Create account"}
          </button>
        </form>

        <p className="mt-sm">
          Already have an account?{" "}
          <Link className="link-text" to="/login">
            Sign in
          </Link>
        </p>
      </div>
    </div>
  );
}