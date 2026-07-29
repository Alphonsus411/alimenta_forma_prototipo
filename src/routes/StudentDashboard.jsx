import { useCallback } from "react";
import { Link } from "react-router-dom";
import AsyncState from "../components/AsyncState";
import Header from "../components/Header";
import useRemoteResource from "../hooks/useRemoteResource";
import { getAttendance } from "../services/attendanceApi";
import { getCurrentUser } from "../services/authApi";
import { getContents } from "../services/contentApi";
import { getCourses } from "../services/coursesApi";
import { getMarks } from "../services/marksApi";
import { getRegistrations } from "../services/registrationsApi";
import styles from "./StudentRoutes.module.css";

const percentage = (records) => records.length
  ? Math.round((records.filter((record) => record.present).length / records.length) * 100)
  : 0;

const StudentDashboard = () => {
  const load = useCallback(async () => {
    const user = await getCurrentUser();
    const [registrations, courses, contents, attendance, marks] = await Promise.all([
      getRegistrations(), getCourses(), getContents(), getAttendance(), getMarks(),
    ]);
    return { user, registrations, courses, contents, attendance, marks };
  }, []);
  const { data, error, loading, reload } = useRemoteResource(load);
  const anonymous = error?.status === 401 || error?.status === 403;
  const enrolled = data?.registrations.map((registration) => ({
    registration,
    course: data.courses.find((course) => course.id === registration.course),
  })).filter((item) => item.course) || [];

  return <><Header /><main className={styles.main}><h1>Panel del alumno</h1>
    {anonymous ? <div role="alert"><p>Debes iniciar sesión para consultar tu progreso.</p><Link to="/login">Iniciar sesión</Link></div> :
      <AsyncState loading={loading} error={error} empty={Boolean(data) && enrolled.length === 0} emptyMessage="Todavía no estás matriculado en ningún curso." onRetry={reload}>
        {data && <section aria-label="Cursos matriculados"><h2>Cursos matriculados</h2><ul className={styles.list}>
          {enrolled.map(({ registration, course }) => {
            const records = data.attendance.filter((item) => item.course === course.id);
            const mark = data.marks.find((item) => item.course === course.id);
            const content = data.contents.find((item) => item.id === course.content);
            return <li className={styles.card} key={registration.id}>
              <h3>{course.title}</h3>
              <p>Contenidos disponibles: {content ? content.title : "Ninguno por ahora"}</p>
              <p>Asistencia: {percentage(records)}%</p>
              <p>Regularidad: {registration.enabled ? "Regular" : "No regular"}</p>
              <p>Notas: {mark ? [mark.mark_1, mark.mark_2, mark.mark_3].filter((value) => value != null).join(", ") || "Sin notas" : "Sin notas"}</p>
              <p>Promedio: {mark?.average ?? "Pendiente"}</p>
              <p>Finalización: {course.status === "f" ? "Finalizado" : "En curso"}</p>
              <Link to={`/courses/${course.id}/classroom`}>Acceder al aula</Link>
            </li>;
          })}
        </ul></section>}
      </AsyncState>}
  </main></>;
};

export default StudentDashboard;
