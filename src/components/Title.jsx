import styles from "./Title.module.css";
import PropTypes from "prop-types";

const Title = ({ text }) => {
  return (
		<div className={styles.container}>
			<h2>{text}</h2>
		</div>
	)
}

Title.propTypes = {
	text: PropTypes.string.isRequired,
};

export default Title;
