import { useState } from "react";
import FooterButtons from "./FooterButtons";
import styles from "./LoginForm.module.css";
import { login } from "../services/authApi";

const LoginForm = () => {
  const [values, setValues] = useState({ username: "", password: "" });
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");

  const handleChange = ({ target }) => {
    setValues((current) => ({ ...current, [target.name]: target.value }));
    setErrors((current) => ({ ...current, [target.name]: undefined, non_field_errors: undefined }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setErrors({});
    setSuccess("");
    try {
      const user = await login(values);
      setSuccess(`Sesión iniciada como ${user.username}.`);
    } catch (error) {
      setErrors(error.fields || { non_field_errors: [error.message] });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <div><h2>Inicio de Sesión</h2><h4>Ingrese sus credenciales</h4></div>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        <label htmlFor="username">Nombre de usuario *</label>
        <input id="username" name="username" value={values.username} onChange={handleChange} required />
        {errors.username && <p className={styles.error}>{errors.username[0]}</p>}
        <label htmlFor="password">Contraseña *</label>
        <input id="password" name="password" type="password" value={values.password} onChange={handleChange} required />
        {errors.password && <p className={styles.error}>{errors.password[0]}</p>}
        {errors.non_field_errors && <p className={styles.error} role="alert">{errors.non_field_errors[0]}</p>}
        {success && <p className={styles.success} role="status">{success}</p>}
        <button type="submit" disabled={submitting}>{submitting ? "Iniciando…" : "Iniciar sesión"}</button>
      </form>
      <FooterButtons />
    </div>
  );
};

export default LoginForm;
