import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useForm } from "react-hook-form";
import { useAuth } from "../context/AuthContext";

export default function RegisterPage() {
  const { register: registerCtx } = useAuth();
  const navigate = useNavigate();
  const [serverError, setServerError] = useState("");

  const {
    register,
    handleSubmit,
    formState: { errors, isSubmitting },
  } = useForm({ defaultValues: { role: "requester" } });

  async function onSubmit(data) {
    setServerError("");
    try {
      await registerCtx(data);
      navigate("/dashboard");
    } catch (err) {
      setServerError(
        err.response?.data?.detail ?? "Registration failed. Please try again."
      );
    }
  }

  return (
    <div className="auth-page">
      <div className="auth-card">
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
              {...register("full_name", { required: "Full name is required." })}
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
                pattern: { value: /\S+@\S+\.\S+/, message: "Enter a valid email." },
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
