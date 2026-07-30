import PropTypes from "prop-types";

const RegistrationsTable = ({ registrations }) => <section aria-labelledby="registrations-title"><h3 id="registrations-title">Matrículas</h3>
  {registrations.length === 0 ? <p>No hay alumnado matriculado en este curso.</p> : <table><thead><tr><th>Alumno</th><th>Regularidad</th></tr></thead>
    <tbody>{registrations.map((item) => <tr key={item.id}><td>{item.student_username || `Alumno #${item.student}`}</td><td>{item.enabled ? "Regular" : "No regular"}</td></tr>)}</tbody></table>}
</section>;
RegistrationsTable.propTypes = { registrations: PropTypes.array.isRequired };
export default RegistrationsTable;
