import { useCallback } from "react";
import { Link, useParams } from "react-router-dom";
import AsyncState from "../components/AsyncState";
import Header from "../components/Header";
import useRemoteResource from "../hooks/useRemoteResource";
import { getCourse } from "../services/coursesApi";
import styles from "./StudentRoutes.module.css";

const CourseDetail = () => {
  const { courseId } = useParams();
  const loadCourse = useCallback(() => getCourse(courseId), [courseId]);
  const { data: course, error, loading, reload } = useRemoteResource(loadCourse);

  return <><Header /><main className={styles.main}>
    <AsyncState loading={loading} error={error} empty={!course} emptyMessage="No se encontró el curso." onRetry={reload}>
      {course && <article className={styles.card}>
        <h1>{course.title}</h1>
        <p><strong>Programa:</strong> {course.program || course.detail}</p>
        <ul className={styles.meta}>
          <li>Profesor: {course.teacher_name || `#${course.teacher}`}</li>
          <li>Número de clases: {course.classes}</li>
          <li>Categoría: {course.category_name || "Pendiente de definir"}</li>
          <li>Modalidad: {course.modality_display || course.modality || "Pendiente de definir"}</li>
          {course.duration_hours && <li>Duración: {course.duration_hours} horas</li>}
          {course.start_date && <li>Fechas: {course.start_date} — {course.end_date}</li>}
          {course.capacity && <li>Aforo: {course.capacity} plazas</li>}
          {course.location && <li>Ubicación o acceso: {course.location}</li>}
          {course.price != null && <li>Precio: {Number(course.price) === 0 ? "Gratuito" : `${course.price} €`}</li>}
          <li>Estado: {course.status_display || course.status}</li>
        </ul>
        {course.objectives && <><h2>Objetivos</h2><p>{course.objectives}</p></>}
        {course.requirements && <><h2>Requisitos</h2><p>{course.requirements}</p></>}
        <h2>Programa ordenado</h2>
        {course.lessons?.length
          ? <ol>{course.lessons.map((lesson) => <li key={lesson.id}><strong>{lesson.title}</strong>: {lesson.comment}</li>)}</ol>
          : <p>El programa todavía no tiene lecciones publicadas.</p>}
        <div className={styles.actions}>
          <Link className={styles.link} to={`/courses/${course.id}/registration`}>Matricularme</Link>
          <Link className={styles.link} to={`/courses/${course.id}/classroom`}>Ir al aula</Link>
        </div>
      </article>}
    </AsyncState>
  </main></>;
};

export default CourseDetail;
