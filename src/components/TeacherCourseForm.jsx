import PropTypes from "prop-types";
import { useEffect, useState } from "react";

const today = new Date().toISOString().slice(0, 10);
const EMPTY_COURSE = {
  title: "", detail: "", classes: 1, category: 1, modality: "presencial",
  duration_hours: 1, start_date: today, end_date: today, capacity: 1,
  location: "Pendiente de actualizar", price: 0,
  objectives: "Pendiente de actualizar", requirements: "Sin requisitos",
  status: "borrador",
};

const TeacherCourseForm = ({ course = null, busy = false, onCancel, onSubmit }) => {
  const [values, setValues] = useState(EMPTY_COURSE);
  useEffect(() => setValues(course ? {
    ...EMPTY_COURSE, ...course,
  } : EMPTY_COURSE), [course]);
  const change = ({ target }) => setValues((current) => ({ ...current, [target.name]: target.value }));

  return <form onSubmit={(event) => { event.preventDefault(); onSubmit({
    ...values, classes: Number(values.classes), category: Number(values.category),
    capacity: Number(values.capacity), price: Number(values.price),
  }); }}>
    <h2>{course ? `Editar ${course.title}` : "Crear curso"}</h2>
    <label htmlFor="course-title">Título</label>
    <input id="course-title" name="title" value={values.title} onChange={change} required maxLength="150" />
    <label htmlFor="course-detail">Descripción</label>
    <textarea id="course-detail" name="detail" value={values.detail} onChange={change} required maxLength="500" />
    <label htmlFor="course-classes">Número de clases</label>
    <input id="course-classes" name="classes" type="number" min="1" value={values.classes} onChange={change} required />
    <label htmlFor="course-category">Identificador de categoría</label>
    <input id="course-category" name="category" type="number" min="1" value={values.category} onChange={change} required />
    <label htmlFor="course-modality">Modalidad</label>
    <select id="course-modality" name="modality" value={values.modality} onChange={change}>
      <option value="presencial">Presencial</option><option value="online">Online</option><option value="mixta">Mixta</option>
    </select>
    <label htmlFor="course-duration">Duración (horas)</label>
    <input id="course-duration" name="duration_hours" type="number" min="0.01" step="0.01" value={values.duration_hours} onChange={change} required />
    <label htmlFor="course-start">Fecha de inicio</label>
    <input id="course-start" name="start_date" type="date" value={values.start_date} onChange={change} required />
    <label htmlFor="course-end">Fecha de fin</label>
    <input id="course-end" name="end_date" type="date" value={values.end_date} onChange={change} required />
    <label htmlFor="course-capacity">Aforo</label>
    <input id="course-capacity" name="capacity" type="number" min="1" value={values.capacity} onChange={change} required />
    <label htmlFor="course-location">Ubicación o acceso</label>
    <input id="course-location" name="location" value={values.location} onChange={change} required />
    <label htmlFor="course-price">Precio (€)</label>
    <input id="course-price" name="price" type="number" min="0" step="0.01" value={values.price} onChange={change} required />
    <label htmlFor="course-objectives">Objetivos</label>
    <textarea id="course-objectives" name="objectives" value={values.objectives} onChange={change} required />
    <label htmlFor="course-requirements">Requisitos</label>
    <textarea id="course-requirements" name="requirements" value={values.requirements} onChange={change} required />
    <label htmlFor="course-status">Estado</label>
    <select id="course-status" name="status" value={values.status} onChange={change}>
      <option value="borrador">Borrador</option><option value="revision">En revisión</option>
    </select>
    <div><button type="submit" disabled={busy}>{course ? "Guardar curso" : "Crear curso"}</button>
      {course && <button type="button" onClick={onCancel}>Cancelar edición</button>}</div>
  </form>;
};

TeacherCourseForm.propTypes = { course: PropTypes.object, busy: PropTypes.bool, onCancel: PropTypes.func.isRequired, onSubmit: PropTypes.func.isRequired };
export default TeacherCourseForm;
