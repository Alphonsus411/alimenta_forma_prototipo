import PropTypes from "prop-types";
import { useEffect, useState } from "react";

const MarkRow = ({ registration, mark = null, onSave }) => {
  const [values, setValues] = useState(["", "", ""]);
  useEffect(() => setValues([mark?.mark_1 ?? "", mark?.mark_2 ?? "", mark?.mark_3 ?? ""]), [mark]);
  const numeric = values.filter((value) => value !== "").map(Number);
  const preview = numeric.length ? (numeric.reduce((sum, value) => sum + value, 0) / numeric.length).toFixed(1) : "Pendiente";
  return <tr><td>{registration.student_username || `Alumno #${registration.student}`}</td>{values.map((value, index) => <td key={index}><label className="visually-hidden" htmlFor={`mark-${registration.student}-${index}`}>Nota {index + 1}</label><input id={`mark-${registration.student}-${index}`} aria-label={`Nota ${index + 1} de ${registration.student_username || `Alumno #${registration.student}`}`} type="number" min="0" max="10" value={value} onChange={(event) => setValues((current) => current.map((item, position) => position === index ? event.target.value : item))} /></td>)}<td aria-label="Promedio provisional">{preview}</td><td><button type="button" onClick={() => onSave(registration.student, mark?.id, values)}>Guardar notas</button></td></tr>;
};
MarkRow.propTypes = { registration: PropTypes.object.isRequired, mark: PropTypes.object, onSave: PropTypes.func.isRequired };
const MarksTable = ({ registrations, marks, onSave }) => <section aria-labelledby="marks-title"><h3 id="marks-title">Calificaciones</h3>{registrations.length === 0 ? <p>No hay alumnado al que calificar.</p> : <table><thead><tr><th>Alumno</th><th>Nota 1</th><th>Nota 2</th><th>Nota 3</th><th>Promedio</th><th>Acción</th></tr></thead><tbody>{registrations.map((registration) => <MarkRow key={registration.id} registration={registration} mark={marks.find((item) => item.student === registration.student)} onSave={onSave} />)}</tbody></table>}</section>;
MarksTable.propTypes = { registrations: PropTypes.array.isRequired, marks: PropTypes.array.isRequired, onSave: PropTypes.func.isRequired };
export default MarksTable;
