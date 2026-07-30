import PropTypes from "prop-types";
import { Link } from "react-router-dom";
import styles from "./CourseCard.module.css";

const CourseCard = ({ course }) => {
	return (
		<article className={styles.container}>
			<h2>{course.title}</h2>
			<p>{course.detail}</p>
			<ul>
				<li>Profesor: {course.teacher_name || `#${course.teacher}`}</li>
				<li>Categoría: {course.category_name || "Pendiente de definir"}</li>
				<li>Modalidad: {course.modality_display || course.modality || "Pendiente de definir"}</li>
				<li>Duración: {course.duration_hours ? `${course.duration_hours} horas` : `${course.classes} clases`}</li>
				{course.start_date && <li>Fechas: {course.start_date} — {course.end_date}</li>}
				{course.capacity && <li>Aforo: {course.capacity} plazas</li>}
				{course.price != null && <li>Precio: {Number(course.price) === 0 ? "Gratuito" : `${course.price} €`}</li>}
				<li>Estado: {course.status_display || course.status}</li>
			</ul>
			<Link className={styles.link} to={`/courses/${course.id}`}>Ver detalle de {course.title}</Link>
		</article>
	)
}

CourseCard.propTypes = {
	course: PropTypes.shape({
		id: PropTypes.number.isRequired,
		title: PropTypes.string.isRequired,
		detail: PropTypes.string.isRequired,
		classes: PropTypes.number.isRequired,
		teacher: PropTypes.number.isRequired,
		teacher_name: PropTypes.string,
		status: PropTypes.string.isRequired,
		status_display: PropTypes.string,
		category_name: PropTypes.string,
		modality: PropTypes.string,
		modality_display: PropTypes.string,
		duration_hours: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
		start_date: PropTypes.string,
		end_date: PropTypes.string,
		capacity: PropTypes.number,
		price: PropTypes.oneOfType([PropTypes.string, PropTypes.number]),
	}).isRequired,
};

export default CourseCard;
