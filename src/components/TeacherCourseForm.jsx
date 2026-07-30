import PropTypes from "prop-types";
import { useEffect, useState } from "react";

const EMPTY_COURSE = { title: "", detail: "", classes: 1, status: "i" };

const TeacherCourseForm = ({ course = null, busy = false, onCancel, onSubmit }) => {
  const [values, setValues] = useState(EMPTY_COURSE);
  useEffect(() => setValues(course ? {
    title: course.title, detail: course.detail, classes: course.classes, status: course.status,
  } : EMPTY_COURSE), [course]);
  const change = ({ target }) => setValues((current) => ({ ...current, [target.name]: target.value }));

  return <form onSubmit={(event) => { event.preventDefault(); onSubmit({ ...values, classes: Number(values.classes) }); }}>
    <h2>{course ? `Editar ${course.title}` : "Crear curso"}</h2>
    <label htmlFor="course-title">Título</label>
    <input id="course-title" name="title" value={values.title} onChange={change} required maxLength="150" />
    <label htmlFor="course-detail">Descripción</label>
    <textarea id="course-detail" name="detail" value={values.detail} onChange={change} required maxLength="500" />
    <label htmlFor="course-classes">Número de clases</label>
    <input id="course-classes" name="classes" type="number" min="1" value={values.classes} onChange={change} required />
    <label htmlFor="course-status">Estado</label>
    <select id="course-status" name="status" value={values.status} onChange={change}>
      <option value="i">Inscripción</option><option value="d">Desarrollo</option><option value="f">Finalizado</option>
    </select>
    <div><button type="submit" disabled={busy}>{course ? "Guardar curso" : "Crear curso"}</button>
      {course && <button type="button" onClick={onCancel}>Cancelar edición</button>}</div>
  </form>;
};

TeacherCourseForm.propTypes = { course: PropTypes.object, busy: PropTypes.bool, onCancel: PropTypes.func.isRequired, onSubmit: PropTypes.func.isRequired };
export default TeacherCourseForm;
