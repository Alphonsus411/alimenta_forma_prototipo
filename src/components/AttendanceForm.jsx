import PropTypes from "prop-types";
import { useState } from "react";

const AttendanceForm = ({ registrations, busy = false, onSubmit }) => {
  const [student, setStudent] = useState(""); const [date, setDate] = useState(""); const [present, setPresent] = useState("true");
  return <form onSubmit={(event) => { event.preventDefault(); onSubmit({ student: Number(student), date, present: present === "true" }); }}>
    <h3>Registrar asistencia</h3><label htmlFor="attendance-student">Alumno</label><select id="attendance-student" value={student} onChange={(event) => setStudent(event.target.value)} required>
      <option value="">Selecciona un alumno</option>{registrations.map((item) => <option key={item.id} value={item.student}>{item.student_username || `Alumno #${item.student}`}</option>)}</select>
    <label htmlFor="attendance-date">Fecha</label><input id="attendance-date" type="date" value={date} onChange={(event) => setDate(event.target.value)} required />
    <label htmlFor="attendance-present">Estado</label><select id="attendance-present" value={present} onChange={(event) => setPresent(event.target.value)}><option value="true">Presente</option><option value="false">Ausente</option></select>
    <button type="submit" disabled={busy || registrations.length === 0}>Registrar asistencia</button>
  </form>;
};
AttendanceForm.propTypes = { registrations: PropTypes.array.isRequired, busy: PropTypes.bool, onSubmit: PropTypes.func.isRequired };
export default AttendanceForm;
