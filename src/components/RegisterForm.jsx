import { useState } from "react";
import styles from "./RegisterForm.module.css";
import FooterButtons from "./FooterButtons";
import { register } from "../services/authApi";

const initialValues = {
  username: "", email: "", first_name: "", last_name: "",
  category: "s", password: "", password_confirmation: "",
};

const fields = [
  ["username", "Nombre de usuario *", "text"],
  ["email", "Correo electrónico *", "email"],
  ["first_name", "Nombre *", "text"],
  ["last_name", "Apellido *", "text"],
  ["password", "Contraseña *", "password"],
  ["password_confirmation", "Confirmación de contraseña *", "password"],
];

const RegisterForm = () => {
  const [values, setValues] = useState(initialValues);
  const [errors, setErrors] = useState({});
  const [submitting, setSubmitting] = useState(false);
  const [success, setSuccess] = useState("");

  const handleChange = ({ target }) => {
    setValues((current) => ({ ...current, [target.name]: target.value }));
    setErrors((current) => ({ ...current, [target.name]: undefined }));
  };

  const handleSubmit = async (event) => {
    event.preventDefault();
    setSubmitting(true);
    setErrors({});
    setSuccess("");
    try {
      const user = await register(values);
      setSuccess(`La cuenta de ${user.username} se creó correctamente.`);
      setValues(initialValues);
    } catch (error) {
      setErrors(error.fields || { non_field_errors: [error.message] });
    } finally {
      setSubmitting(false);
    }
  };

  return (
    <div className={styles.container}>
      <h2>Registro de usuario</h2><h4>Ingrese sus datos</h4>
      <form className={styles.form} onSubmit={handleSubmit} noValidate>
        {fields.map(([name, label, type]) => (
          <div className={styles.field} key={name}>
            <label htmlFor={name}>{label}</label>
            <input id={name} name={name} type={type} value={values[name]} onChange={handleChange} required />
            {errors[name] && <p className={styles.error}>{errors[name][0]}</p>}
          </div>
        ))}
        <div className={styles.field}>
          <label htmlFor="category">Categoría *</label>
          <select id="category" name="category" value={values.category} onChange={handleChange}>
            <option value="s">Estudiante</option><option value="p">Profesor</option><option value="c">Empresa</option>
          </select>
          {errors.category && <p className={styles.error}>{errors.category[0]}</p>}
        </div>
        {errors.non_field_errors && <p className={styles.error} role="alert">{errors.non_field_errors[0]}</p>}
        {success && <p className={styles.success} role="status">{success}</p>}
        <button type="submit" disabled={submitting}>{submitting ? "Registrando…" : "Registrarse"}</button>
      </form>
      <FooterButtons />
    </div>
  );
};

export default RegisterForm;
