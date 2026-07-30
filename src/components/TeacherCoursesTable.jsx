import PropTypes from "prop-types";

const STATUS = { i: "Inscripción", d: "Desarrollo", f: "Finalizado" };
const TeacherCoursesTable = ({ courses, selectedId = null, onEdit, onSelect }) => <section aria-labelledby="own-courses-title">
  <h2 id="own-courses-title">Mis cursos</h2>
  {courses.length === 0 ? <p>No tienes cursos asignados todavía.</p> : <table><thead><tr><th>Curso</th><th>Clases</th><th>Estado</th><th>Acciones</th></tr></thead>
    <tbody>{courses.map((course) => <tr key={course.id} aria-current={selectedId === course.id ? "true" : undefined}>
      <td>{course.title}</td><td>{course.classes}</td><td>{STATUS[course.status] || course.status}</td><td>
        <button type="button" onClick={() => onSelect(course.id)}>Gestionar alumnado</button>
        <button type="button" onClick={() => onEdit(course)}>Editar</button>
      </td></tr>)}</tbody></table>}
</section>;
TeacherCoursesTable.propTypes = { courses: PropTypes.array.isRequired, selectedId: PropTypes.number, onEdit: PropTypes.func.isRequired, onSelect: PropTypes.func.isRequired };
export default TeacherCoursesTable;
