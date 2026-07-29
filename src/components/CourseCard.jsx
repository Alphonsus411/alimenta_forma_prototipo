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
				<li>Cantidad de clases: {course.classes}</li>
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
	}).isRequired,
};

export default CourseCard;
