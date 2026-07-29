import PropTypes from "prop-types";
import styles from "./Announcement.module.css"

const Announcement = ({ announcement }) => {
	return (
		<article className={styles.container}>
			<p className={styles.p1}>Anuncio de la comunidad</p>
			<a className={styles.p2} href={announcement.detail}>Ver anuncio</a>
		</article>
	)
}

Announcement.propTypes = {
	announcement: PropTypes.shape({
		id: PropTypes.number.isRequired,
		detail: PropTypes.string.isRequired,
	}).isRequired,
};

export default Announcement;
