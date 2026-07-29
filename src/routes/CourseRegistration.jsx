import { useCallback, useState } from "react";
import { Link, useParams } from "react-router-dom";
import AsyncState from "../components/AsyncState";
import Header from "../components/Header";
import useRemoteResource from "../hooks/useRemoteResource";
import { getCurrentUser } from "../services/authApi";
import { getCourse } from "../services/coursesApi";
import { registerForCourse } from "../services/registrationsApi";
import styles from "./StudentRoutes.module.css";

const CourseRegistration = () => {
  const { courseId } = useParams();
  const load = useCallback(async () => ({ user: await getCurrentUser(), course: await getCourse(courseId) }), [courseId]);
  const { data, error, loading, reload } = useRemoteResource(load);
  const [submitting, setSubmitting] = useState(false);
  const [result, setResult] = useState("");
  const [submitError, setSubmitError] = useState(null);

  const enroll = async () => {
    setSubmitting(true); setResult(""); setSubmitError(null);
    try {
      await registerForCourse(courseId);
      setResult("Matrícula realizada correctamente.");
    } catch (requestError) {
      if (requestError.status === 400 && requestError.fields?.course) setResult("Ya estás matriculado en este curso.");
      else setSubmitError(requestError);
    } finally { setSubmitting(false); }
  };

  const anonymous = error?.status === 401 || error?.status === 403;
  return <><Header /><main className={styles.main}><h1>Matrícula del curso</h1>
    {anonymous ? <div role="alert"><p>Debes iniciar sesión para matricularte.</p><Link to="/login">Iniciar sesión</Link></div> :
      <AsyncState loading={loading} error={error} empty={!data} emptyMessage="No se encontró el curso." onRetry={reload}>
        {data && <section className={styles.card}>
          <h2>{data.course.title}</h2><p>Vas a matricular a <strong>{data.user.first_name || data.user.username}</strong>.</p>
          <button className={styles.button} type="button" disabled={submitting || Boolean(result)} onClick={enroll}>{submitting ? "Matriculando…" : "Confirmar matrícula"}</button>
          {result && <p role="status">{result}</p>}
          {submitError && <p role="alert">{submitError.status === 403 ? "No tienes permisos para realizar esta matrícula." : submitError.message}</p>}
        </section>}
      </AsyncState>}
  </main></>;
};

export default CourseRegistration;
