import { useCallback, useState } from "react";
import { Link } from "react-router-dom";
import AttendanceForm from "../components/AttendanceForm";
import AttendanceTable from "../components/AttendanceTable";
import Header from "../components/Header";
import MarksTable from "../components/MarksTable";
import RegistrationsTable from "../components/RegistrationsTable";
import TeacherCourseForm from "../components/TeacherCourseForm";
import TeacherCoursesTable from "../components/TeacherCoursesTable";
import useRemoteResource from "../hooks/useRemoteResource";
import { backendErrorMessage } from "../services/apiErrors";
import { createAttendance, getAttendance, updateAttendance } from "../services/attendanceApi";
import { getCurrentUser } from "../services/authApi";
import { createCourse, getCourses, updateCourse } from "../services/coursesApi";
import { createMark, getMarks, updateMark } from "../services/marksApi";
import { getRegistrations } from "../services/registrationsApi";
import styles from "./Teacher.module.css";

const Teacher = () => {
  const load = useCallback(async () => {
    const user = await getCurrentUser();
    if (user.category !== "p") return { user, forbidden: true };
    const [allCourses, registrations, attendance, marks] = await Promise.all([getCourses(), getRegistrations(), getAttendance(), getMarks()]);
    return { user, courses: allCourses.filter((course) => course.teacher === user.id), registrations, attendance, marks };
  }, []);
  const { data, error, loading, reload } = useRemoteResource(load);
  const [selectedId, setSelectedId] = useState(null); const [editing, setEditing] = useState(null);
  const [actionError, setActionError] = useState(""); const [notice, setNotice] = useState(""); const [busy, setBusy] = useState(false);
  const act = async (operation, success) => { setBusy(true); setActionError(""); setNotice(""); try { await operation(); setNotice(success); await reload(); } catch (caught) { setActionError(backendErrorMessage(caught)); } finally { setBusy(false); } };
  const selectedRegistrations = data?.registrations?.filter((item) => item.course === selectedId) || [];
  const selectedAttendance = data?.attendance?.filter((item) => item.course === selectedId) || [];
  const selectedMarks = data?.marks?.filter((item) => item.course === selectedId) || [];
  const saveCourse = (values) => act(
    () => editing ? updateCourse(editing.id, values) : createCourse(values),
    editing ? "Curso actualizado correctamente." : "Curso creado correctamente.",
  ).then(() => setEditing(null));
  const saveAttendance = (values) => act(async () => {
    try { await createAttendance({ ...values, course: selectedId }); } catch (caught) { caught.operation = "attendance"; throw caught; }
  }, "Asistencia registrada correctamente.");
  const toggleAttendance = (record) => act(() => updateAttendance(record.id, { present: !record.present }), "Asistencia corregida correctamente.");
  const saveMark = (student, markId, values) => {
    const payload = Object.fromEntries(values.map((value, index) => [`mark_${index + 1}`, value === "" ? null : Number(value)]));
    return act(() => markId ? updateMark(markId, payload) : createMark({ ...payload, course: selectedId, student }), "Calificaciones guardadas y promedio recalculado.");
  };

  const anonymous = error?.status === 401 || error?.status === 403;
  return <><Header /><main className={styles.main}><h1>Panel docente</h1>
    {loading && <p role="status">Cargando panel docente…</p>}
    {anonymous && <div role="alert"><p>Debes iniciar sesión con una cuenta docente.</p><Link to="/login">Iniciar sesión</Link></div>}
    {data?.forbidden && <div role="alert"><h2>Acceso restringido</h2><p>Esta área está disponible únicamente para el rol docente.</p></div>}
    {error && !anonymous && <div role="alert"><p>{backendErrorMessage(error)}</p><button type="button" onClick={reload}>Reintentar</button></div>}
    {data && !data.forbidden && <div className={styles.panel}>
      <p>Sesión docente: <strong>{data.user.username}</strong>. Solo se muestran y editan tus cursos.</p>
      {actionError && <p role="alert" className={styles.error}>{actionError}</p>}{notice && <p role="status" className={styles.notice}>{notice}</p>}
      <TeacherCourseForm course={editing} busy={busy} onCancel={() => setEditing(null)} onSubmit={saveCourse} />
      <TeacherCoursesTable courses={data.courses} selectedId={selectedId} onEdit={setEditing} onSelect={setSelectedId} />
      {selectedId && <section aria-label="Gestión del curso seleccionado" className={styles.management}>
        <h2>Gestión de {data.courses.find((course) => course.id === selectedId)?.title}</h2>
        <RegistrationsTable registrations={selectedRegistrations} />
        <AttendanceForm registrations={selectedRegistrations} busy={busy} onSubmit={saveAttendance} />
        <AttendanceTable records={selectedAttendance} onToggle={toggleAttendance} />
        <MarksTable registrations={selectedRegistrations} marks={selectedMarks} onSave={saveMark} />
      </section>}
    </div>}
  </main></>;
};
export default Teacher;
